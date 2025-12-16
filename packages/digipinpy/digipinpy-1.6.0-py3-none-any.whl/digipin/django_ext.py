"""
Django Integration for DIGIPIN

This module provides a custom Django Model Field for DIGIPIN codes.
It handles validation, normalization, and database interactions.

Usage:
    from django.db import models
    from digipin.django_ext import DigipinField

    class Warehouse(models.Model):
        location_code = DigipinField()

    # Querying
    # Find all warehouses in Delhi region (starts with '39')
    Warehouse.objects.filter(location_code__startswith='39')
"""

try:
    from django.db import models
    from django.core.exceptions import ValidationError
    from django.utils.translation import gettext_lazy as _
except ImportError:
    raise ImportError(
        "Django is required for this feature. "
        "Install it with: pip install digipinpy[django]"
    )

from .utils import is_valid_digipin, validate_digipin
from .decoder import is_within


class DigipinField(models.CharField):
    """
    A Django Model Field for storing DIGIPIN codes.

    Features:
    - Auto-validates DIGIPIN format (characters and length)
    - Normalizes input to Uppercase
    - Default max_length is 10
    """

    description = _("DIGIPIN code")

    def __init__(self, *args, **kwargs):
        # Force max_length to 10 unless specified
        kwargs.setdefault("max_length", 10)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Don't serialize default max_length to keep migrations clean
        if kwargs.get("max_length") == 10:
            del kwargs["max_length"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return str(value).upper()

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return value.upper()
        return str(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value:
            return value.upper()
        return value

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value:
            # Use strict validation if max_length is the default (10)
            # This ensures full-precision codes in the database
            strict = self.max_length == 10
            if not is_valid_digipin(value, strict=strict):
                raise ValidationError(
                    _("%(value)s is not a valid DIGIPIN code"),
                    params={"value": value},
                )


# -------------------------------------------------------------------------
# Custom Lookups
# Enables queries like: User.objects.filter(zip__within='39J4')
# -------------------------------------------------------------------------


@DigipinField.register_lookup
class WithinLookup(models.Lookup):
    """
    Allows filtering by parent region.
    Example: Address.objects.filter(digipin__within='39J4')

    Translates to SQL: digipin LIKE '39J4%'
    """

    lookup_name = "within"

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # In SQL, we implement 'within' as a LIKE prefix match
        # Logic: if row_value LIKE 'parent_code%'
        # The LIKE pattern is constructed as: rhs_params[0] + '%'
        return f"{lhs} LIKE %s", [f"{rhs_params[0]}%"]


@DigipinField.register_lookup
class IsNeighborLookup(models.Lookup):
    """
    Custom lookup to check if a DB value is a neighbor of the query value.
    Note: This is complex to implement purely in SQL for all databases without
    stored procedures. For V1, we stick to 'within' which is most useful.
    """

    lookup_name = "is_neighbor"

    def as_sql(self, compiler, connection):
        raise NotImplementedError(
            "Neighbor lookups are not yet supported at the database level. "
            "Use application-side filtering with get_neighbors() instead."
        )
