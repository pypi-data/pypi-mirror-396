"""
Comprehensive Test Suite for Django Integration

Tests cover:
- DigipinField model field behavior
- Validation and normalization
- Database storage and retrieval
- Custom lookups (within, startswith, etc.)
- Migration support (deconstruct)
- Edge cases and error handling
- Integration with Django ORM

Note: These tests require Django and will be skipped if Django is not installed.
"""

import pytest
import os
import sys

# Try to import Django
try:
    import django
    from django.conf import settings
    from django.core.exceptions import ValidationError

    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

# Configure Django settings for testing
if DJANGO_AVAILABLE and not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        SECRET_KEY="test-secret-key-for-digipin-tests",
        USE_TZ=True,
    )
    django.setup()

# Now import Django models and our extension
if DJANGO_AVAILABLE:
    from django.db import models, connection
    from django.test import TestCase

    try:
        from digipin.django_ext import DigipinField

        DIGIPIN_DJANGO_AVAILABLE = True
    except ImportError:
        DIGIPIN_DJANGO_AVAILABLE = False
else:
    DIGIPIN_DJANGO_AVAILABLE = False

from digipin import is_valid, encode

# Skip all tests if Django or digipin.django_ext not available
pytestmark = pytest.mark.skipif(
    not DIGIPIN_DJANGO_AVAILABLE,
    reason="Django not installed (install with: pip install digipinpy[django])",
)


# ============================================================================
# Test Models
# ============================================================================

if DIGIPIN_DJANGO_AVAILABLE:

    class Location(models.Model):
        """Test model with DigipinField."""

        name = models.CharField(max_length=100)
        digipin = DigipinField()

        class Meta:
            app_label = "test_digipin"

    class OptionalLocation(models.Model):
        """Test model with optional DigipinField."""

        name = models.CharField(max_length=100)
        digipin = DigipinField(null=True, blank=True)

        class Meta:
            app_label = "test_digipin"

    class CustomLengthLocation(models.Model):
        """Test model with custom max_length."""

        name = models.CharField(max_length=100)
        digipin = DigipinField(max_length=20)

        class Meta:
            app_label = "test_digipin"


# ============================================================================
# Test Classes
# ============================================================================


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestDigipinFieldBasics:
    """Test basic DigipinField functionality."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables for each test."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
            schema_editor.create_model(OptionalLocation)
            schema_editor.create_model(CustomLengthLocation)
        yield
        # Cleanup
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)
            schema_editor.delete_model(OptionalLocation)
            schema_editor.delete_model(CustomLengthLocation)

    def test_field_has_correct_default_max_length(self):
        """DigipinField should have max_length=10 by default."""
        field = DigipinField()
        assert field.max_length == 10

    def test_field_accepts_custom_max_length(self):
        """DigipinField should accept custom max_length."""
        field = DigipinField(max_length=20)
        assert field.max_length == 20

    def test_field_description(self):
        """Field should have appropriate description."""
        field = DigipinField()
        assert "DIGIPIN" in str(field.description)


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestValidation:
    """Test DIGIPIN code validation."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables for each test."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
        yield
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_valid_code_passes_validation(self):
        """Valid DIGIPIN codes should pass validation."""
        loc = Location(name="Delhi Office", digipin="39J49LL8T4")

        # Should not raise
        loc.full_clean()

    def test_invalid_code_raises_validation_error(self):
        """Invalid DIGIPIN codes should raise ValidationError."""
        loc = Location(name="Bad Location", digipin="INVALID123")

        with pytest.raises(ValidationError) as exc_info:
            loc.full_clean()

        # Error should be about the digipin field
        assert "digipin" in exc_info.value.message_dict

    def test_empty_code_fails_validation_if_required(self):
        """Empty code should fail validation if field is required."""
        loc = Location(name="No Code")

        with pytest.raises(ValidationError):
            loc.full_clean()

    def test_empty_code_passes_if_optional(self):
        """Empty code should pass validation if field allows blank."""
        loc = OptionalLocation(name="Optional", digipin=None)

        # Should not raise
        loc.full_clean()

    def test_too_short_code_fails(self):
        """Too short codes should fail validation."""
        loc = Location(name="Short Code", digipin="39J")

        with pytest.raises(ValidationError):
            loc.full_clean()

    def test_too_long_code_fails(self):
        """Too long codes should fail validation."""
        loc = Location(name="Long Code", digipin="39J49LL8T4X")

        with pytest.raises(ValidationError):
            loc.full_clean()

    def test_code_with_invalid_characters_fails(self):
        """Codes with invalid characters should fail."""
        loc = Location(
            name="Bad Chars", digipin="ABCDEFGHIJ"
        )  # A, B, D, E, G, H not in alphabet

        with pytest.raises(ValidationError):
            loc.full_clean()


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestNormalization:
    """Test automatic uppercase normalization."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables for each test."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
        yield
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_lowercase_input_normalized_to_uppercase(self):
        """Lowercase input should be converted to uppercase."""
        loc = Location(name="Test", digipin="39j49ll8t4")
        loc.full_clean()
        loc.save()

        # Should be uppercase
        assert loc.digipin == "39J49LL8T4"

    def test_mixed_case_normalized(self):
        """Mixed case should be normalized."""
        loc = Location(name="Test", digipin="39J49ll8T4")
        loc.full_clean()
        loc.save()

        assert loc.digipin == "39J49LL8T4"

    def test_retrieved_from_db_is_uppercase(self):
        """Values retrieved from DB should be uppercase."""
        loc = Location.objects.create(name="Test", digipin="39j49ll8t4")

        # Retrieve from DB
        retrieved = Location.objects.get(pk=loc.pk)
        assert retrieved.digipin == "39J49LL8T4"


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestDatabaseOperations:
    """Test database storage and retrieval."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables for each test."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
        yield
        # Cleanup
        Location.objects.all().delete()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_save_and_retrieve(self):
        """Save and retrieve a location with DIGIPIN code."""
        # Create
        loc = Location.objects.create(name="Dak Bhawan", digipin="39J49LL8T4")

        # Retrieve
        retrieved = Location.objects.get(pk=loc.pk)

        assert retrieved.name == "Dak Bhawan"
        assert retrieved.digipin == "39J49LL8T4"

    def test_filter_by_exact_code(self):
        """Filter by exact DIGIPIN code."""
        Location.objects.create(name="Delhi", digipin="39J49LL8T4")
        Location.objects.create(name="Mumbai", digipin="58C4K9FF72")

        results = Location.objects.filter(digipin="39J49LL8T4")

        assert results.count() == 1
        assert results.first().name == "Delhi"

    def test_filter_by_startswith(self):
        """Filter by code prefix (region)."""
        Location.objects.create(name="Delhi 1", digipin="39J49LL8T4")
        Location.objects.create(name="Delhi 2", digipin="39J49LL8T5")
        Location.objects.create(name="Mumbai", digipin="58C4K9FF72")

        # Get all locations in '39J' region
        results = Location.objects.filter(digipin__startswith="39J")

        assert results.count() == 2

    def test_multiple_saves(self):
        """Test updating a location multiple times."""
        loc = Location.objects.create(name="Test", digipin="39J49LL8T4")

        # Update code
        loc.digipin = "58C4K9FF72"
        loc.save()

        # Retrieve and verify
        retrieved = Location.objects.get(pk=loc.pk)
        assert retrieved.digipin == "58C4K9FF72"


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestCustomLookups:
    """Test custom lookup operations (within)."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables and test data."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)

        # Create test data
        Location.objects.create(name="Delhi 1", digipin="39J49LL8T4")
        Location.objects.create(name="Delhi 2", digipin="39J49LL8T5")
        Location.objects.create(name="Delhi 3", digipin="39J49LL8T6")
        Location.objects.create(name="Delhi Other", digipin="39J48LL8T4")
        Location.objects.create(name="Mumbai", digipin="58C4K9FF72")

        yield

        # Cleanup
        Location.objects.all().delete()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_within_lookup_basic(self):
        """Test the custom 'within' lookup."""
        # Find all locations within '39J49L' region
        results = Location.objects.filter(digipin__within="39J49L")

        # Should find 3 locations (ending in T4, T5, T6)
        assert results.count() == 3
        names = set(r.name for r in results)
        assert names == {"Delhi 1", "Delhi 2", "Delhi 3"}

    def test_within_lookup_broader_region(self):
        """Test within lookup with broader region."""
        # Find all locations within '39' region
        results = Location.objects.filter(digipin__within="39")

        # Should find 4 locations (all Delhi ones)
        assert results.count() == 4

    def test_within_lookup_specific_region(self):
        """Test within lookup with very specific region."""
        # Find locations within '39J49LL8T' (very specific)
        results = Location.objects.filter(digipin__within="39J49LL8T")

        # Should find 3 locations
        assert results.count() == 3

    def test_within_lookup_no_matches(self):
        """Test within lookup with no matches."""
        results = Location.objects.filter(digipin__within="99XXX")

        assert results.count() == 0


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestMigrationSupport:
    """Test migration support (deconstruct method)."""

    def test_deconstruct_returns_correct_structure(self):
        """Field deconstruct should return correct structure."""
        field = DigipinField()
        name, path, args, kwargs = field.deconstruct()

        # Should be a CharField
        assert "CharField" in path or "DigipinField" in path

        # Default max_length should not be in kwargs (to keep migrations clean)
        assert "max_length" not in kwargs

    def test_deconstruct_preserves_custom_max_length(self):
        """Custom max_length should be preserved in deconstruct."""
        field = DigipinField(max_length=20)
        name, path, args, kwargs = field.deconstruct()

        # Custom max_length should be in kwargs
        assert kwargs.get("max_length") == 20

    def test_deconstruct_preserves_other_kwargs(self):
        """Other kwargs should be preserved."""
        field = DigipinField(null=True, blank=True, db_index=True)
        name, path, args, kwargs = field.deconstruct()

        assert kwargs.get("null") == True
        assert kwargs.get("blank") == True
        assert kwargs.get("db_index") == True


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables for each test."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(OptionalLocation)
        yield
        OptionalLocation.objects.all().delete()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(OptionalLocation)

    def test_none_value_in_optional_field(self):
        """None should be handled correctly in optional fields."""
        loc = OptionalLocation.objects.create(name="No Code", digipin=None)

        retrieved = OptionalLocation.objects.get(pk=loc.pk)
        assert retrieved.digipin is None

    def test_empty_string_vs_none(self):
        """Empty string and None should be handled differently."""
        # Create with empty string
        loc1 = OptionalLocation(name="Empty String", digipin="")
        loc1.full_clean()
        loc1.save()

        # Create with None
        loc2 = OptionalLocation(name="None", digipin=None)
        loc2.full_clean()
        loc2.save()

        # Both should be retrievable
        assert OptionalLocation.objects.count() == 2

    def test_whitespace_handling(self):
        """Whitespace in codes should fail validation."""
        loc = Location(name="Whitespace", digipin="39J 49LL8T4")

        # Note: We need to create the Location table first
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)

        try:
            with pytest.raises(ValidationError):
                loc.full_clean()
        finally:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(Location)


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables and test data."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
        yield
        Location.objects.all().delete()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_warehouse_management_scenario(self):
        """Simulate warehouse location management."""
        # Create warehouses
        warehouses = [
            ("Warehouse Delhi North", 28.7, 77.1),
            ("Warehouse Delhi South", 28.5, 77.2),
            ("Warehouse Mumbai", 19.0, 72.8),
        ]

        for name, lat, lon in warehouses:
            code = encode(lat, lon, precision=8)
            Location.objects.create(name=name, digipin=code)

        # Query Delhi region
        delhi_warehouses = Location.objects.filter(digipin__startswith="39")
        assert delhi_warehouses.count() == 2

    def test_location_aggregation(self):
        """Test aggregating locations by region."""
        from django.db.models import Count
        from django.db.models.functions import Substr

        # Create locations
        for i in range(5):
            Location.objects.create(name=f"Delhi {i}", digipin=f"39J49LL8T{i}")
        for i in range(3):
            Location.objects.create(name=f"Mumbai {i}", digipin=f"58C4K9FF7{i}")

        # Group by first 2 characters (broad region)
        region_counts = (
            Location.objects.annotate(region=Substr("digipin", 1, 2))
            .values("region")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        region_dict = {r["region"]: r["count"] for r in region_counts}
        assert region_dict.get("39") == 5
        assert region_dict.get("58") == 3

    def test_bulk_create_with_validation(self):
        """Test bulk creating locations with validation."""
        locations = [
            Location(name="Delhi 1", digipin="39J49LL8T4"),
            Location(name="Delhi 2", digipin="39J49LL8T5"),
            Location(name="Mumbai 1", digipin="58C4K9FF72"),
        ]

        # Validate all first
        for loc in locations:
            loc.full_clean()

        # Bulk create
        Location.objects.bulk_create(locations)

        assert Location.objects.count() == 3


@pytest.mark.skipif(not DIGIPIN_DJANGO_AVAILABLE, reason="Django not available")
class TestNotImplementedLookup:
    """Test that is_neighbor lookup raises NotImplementedError."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Create tables."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Location)
        Location.objects.create(name="Test", digipin="39J49LL8T4")
        yield
        Location.objects.all().delete()
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Location)

    def test_is_neighbor_lookup_not_implemented(self):
        """The is_neighbor lookup should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            list(Location.objects.filter(digipin__is_neighbor="39J49LL8T4"))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
