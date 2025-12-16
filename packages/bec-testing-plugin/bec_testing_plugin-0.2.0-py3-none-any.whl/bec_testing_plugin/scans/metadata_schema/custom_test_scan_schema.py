from bec_lib.metadata_schema import BasicScanMetadata


class CustomScanSchema(BasicScanMetadata):
    treatment_description: str
    treatment_temperature_k: int
