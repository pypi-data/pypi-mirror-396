class DatasetCredsValidator:
    @staticmethod
    def validate_type(type: str) -> str:
        valid_types = ['AWS_S3', 'GCP', 'Azure']  # Add multiple types as required
        if type not in valid_types:
            raise ValueError(f"Invalid type. Must be one of {valid_types}.")
        return type

    @staticmethod
    def validate_location(location: str) -> str:
        if not location:
            raise ValueError("Location is required.")
        # Additional validation logic specific to location, e.g., checking format or accessibility
        return location

    @staticmethod
    def validate_reference_id(reference_id: str) -> str:
        if not reference_id:
            raise ValueError("Reference ID is required.")
        # Additional validation logic specific to reference_id, e.g., checking length or format
        return reference_id