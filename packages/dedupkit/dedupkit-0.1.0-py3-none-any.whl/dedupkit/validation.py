from .exceptions import ValidationError

def validate_non_empty_string(value: str, field_name: str):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string.")

def validate_non_empty_list_of_strings(value: list, field_name: str):
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValidationError(f"{field_name} must be a non-empty list of non-empty strings.")

def validate_embedding_dimensions(embedding: list[float], expected_dimensions: int):
    if not isinstance(embedding, list) or len(embedding) != expected_dimensions:
        raise ValidationError(f"Embedding must be a list of {expected_dimensions} floats.")

def validate_dimensions(dimensions: int):
    validate_positive_integer(dimensions, "dimensions")

def validate_positive_integer(value: int, field_name: str):
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer.")