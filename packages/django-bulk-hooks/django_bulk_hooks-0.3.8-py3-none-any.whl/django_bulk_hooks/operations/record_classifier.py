"""
Record classification service for database queries.

This service handles all database queries related to classifying and fetching
records based on various criteria (PKs, unique fields, etc.).

Separates data access concerns from business logic.
"""

import logging

from django.db.models import Q

from django_bulk_hooks.operations.field_utils import get_field_value_for_db

logger = logging.getLogger(__name__)


class RecordClassifier:
    """
    Service for classifying and fetching records via database queries.

    This is the SINGLE point of truth for record classification queries.
    Keeps database access logic separate from business/planning logic.
    """

    def __init__(self, model_cls):
        """
        Initialize classifier for a specific model.

        Args:
            model_cls: The Django model class
        """
        self.model_cls = model_cls

    def classify_for_upsert(self, objs, unique_fields, query_model=None):
        """
        Classify records as new or existing based on unique_fields.

        Queries the database to check which records already exist based on the
        unique_fields constraint.

        Args:
            objs: List of model instances
            unique_fields: List of field names that form the unique constraint
            query_model: Optional model class to query (defaults to self.model_cls)

        Returns:
            Tuple of (existing_record_ids, existing_pks_map)
            - existing_record_ids: Set of id() for objects that exist in DB
            - existing_pks_map: Dict mapping id(obj) -> pk for existing records
        """
        if not unique_fields or not objs:
            return set(), {}

        # Use query_model if provided, otherwise use self.model_cls
        query_model = query_model or self.model_cls

        # Build a query to find existing records
        queries = []
        obj_to_unique_values = {}

        for obj in objs:
            # Build lookup dict for this object's unique fields
            lookup = {}
            normalized_values = []

            for field_name in unique_fields:
                # Use centralized field value extraction for consistent FK handling
                value = get_field_value_for_db(obj, field_name, query_model)
                if value is None:
                    # Can't match on None values
                    break
                lookup[field_name] = value
                normalized_values.append(value)
            else:
                # All unique fields have values, add to query
                if lookup:
                    queries.append(Q(**lookup))
                    # Store normalized values for comparison with database results
                    obj_to_unique_values[id(obj)] = tuple(normalized_values)

        if not queries:
            return set(), {}

        # Query for existing records
        combined_query = queries[0]
        for q in queries[1:]:
            combined_query |= q

        logger.info(f"Classifying for upsert: model={query_model.__name__}, query={combined_query}, unique_fields={unique_fields}")
        queryset = query_model.objects.filter(combined_query)
        logger.info(f"Queryset SQL: {queryset.query}")
        logger.info(f"All records in table: {query_model.objects.all().count()}")
        existing_records = list(queryset.values("pk", *unique_fields))
        logger.info(f"Found {len(existing_records)} existing records: {existing_records}")

        # Map existing records back to original objects
        existing_record_ids = set()
        existing_pks_map = {}

        for record in existing_records:
            record_values = tuple(record[field] for field in unique_fields)
            # Find which object(s) match these values
            for obj_id, obj_values in obj_to_unique_values.items():
                if obj_values == record_values:
                    existing_record_ids.add(obj_id)
                    existing_pks_map[obj_id] = record["pk"]

        logger.info(
            f"Classified {len(existing_record_ids)} existing and {len(objs) - len(existing_record_ids)} new records for upsert",
        )

        return existing_record_ids, existing_pks_map

    def fetch_by_pks(self, pks, select_related=None, prefetch_related=None):
        """
        Fetch records by primary keys with optional relationship loading.

        Args:
            pks: List of primary key values
            select_related: Optional list of fields to select_related
            prefetch_related: Optional list of fields to prefetch_related

        Returns:
            Dict[pk, instance] for O(1) lookups
        """
        if not pks:
            return {}

        queryset = self.model_cls._base_manager.filter(pk__in=pks)

        if select_related:
            queryset = queryset.select_related(*select_related)

        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        return {obj.pk: obj for obj in queryset}

    def fetch_by_unique_constraint(self, field_values_map):
        """
        Fetch records matching a unique constraint.

        Args:
            field_values_map: Dict of {field_name: value} for unique constraint

        Returns:
            Model instance if found, None otherwise
        """
        try:
            return self.model_cls.objects.get(**field_values_map)
        except self.model_cls.DoesNotExist:
            return None
        except self.model_cls.MultipleObjectsReturned:
            logger.warning(
                f"Multiple {self.model_cls.__name__} records found for unique constraint {field_values_map}",
            )
            return self.model_cls.objects.filter(**field_values_map).first()

    def exists_by_pks(self, pks):
        """
        Check if records exist by primary keys without fetching them.

        Args:
            pks: List of primary key values

        Returns:
            Set of PKs that exist in the database
        """
        if not pks:
            return set()

        existing_pks = self.model_cls.objects.filter(
            pk__in=pks,
        ).values_list("pk", flat=True)

        return set(existing_pks)

    def count_by_unique_fields(self, objs, unique_fields):
        """
        Count how many objects already exist based on unique fields.

        Useful for validation or reporting before upsert operations.

        Args:
            objs: List of model instances
            unique_fields: List of field names that form the unique constraint

        Returns:
            Tuple of (existing_count, new_count)
        """
        existing_ids, _ = self.classify_for_upsert(objs, unique_fields)
        existing_count = len(existing_ids)
        new_count = len(objs) - existing_count
        return existing_count, new_count
