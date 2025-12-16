# from .metadata_schema_template import ExampleSchema
from .custom_test_scan_schema import CustomScanSchema

METADATA_SCHEMA_REGISTRY = {
    # Add models which should be used to validate scan metadata here.
    # Make a model according to the template, and import it as above
    # Then associate it with a scan like so:
    "custom_testing_scan": CustomScanSchema
}

# Define a default schema type which should be used as the fallback for everything:

DEFAULT_SCHEMA = None
