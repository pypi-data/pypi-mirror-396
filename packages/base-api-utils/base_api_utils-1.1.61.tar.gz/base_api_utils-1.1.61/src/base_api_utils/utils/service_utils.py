
def apply_payload(instance, payload: dict, allowed_fields: set[str]) -> list[str]:
    """
    Assigns values from `payload` to `instance` only for fields in `allowed_fields`.
    Returns the list of fields that were actually updated.
    """
    updated_fields = []
    for field in allowed_fields:
        if field in payload:
            setattr(instance, field, payload[field])
            updated_fields.append(field)
    return updated_fields