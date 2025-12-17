from collections.abc import Mapping
from enum import Enum
from rest_framework import serializers

class GetWithInstanceDefaultMixin:
    #
    # Helper to get a field value from incoming data,
    # falling back to the instance on updates.
    #

    def _get_with_instance_default(self, data: dict, field_name: str):
        #
        # Return value from data if present and not empty, otherwise
        # fallback to instance.<field_name> (on updates).
        #
        value = data.get(field_name, None)

        # You can customize what "empty" means here
        is_empty = value is None or value == ""

        if is_empty and getattr(self, "instance", None) is not None:
            value = getattr(self.instance, field_name, None)

        return value

class PolymorphicSerializer(serializers.Serializer):

    # Generic write-only polymorphic serializer.
    # Subclasses must define:
    #  - discriminator_field: name of the field in the incoming payload
    #  - serializer_mapping: {enum_or_string_value: SerializerClass}

    discriminator_field: str = None
    serializer_mapping: Mapping = None

    def _get_discriminator_value(self, data):
        field = self.discriminator_field
        if not field:
            raise RuntimeError("discriminator_field must be set on the subclass")

        if field not in data:
            raise serializers.ValidationError({field: f"{field} field is required."})

        raw = data[field]
        if raw is None or (isinstance(raw, str) and raw.strip() == ""):
            raise serializers.ValidationError({field: f"{field} field cannot be empty."})

        return raw

    def _select_serializer_class(self, data):
        if not self.serializer_mapping:
            raise RuntimeError("serializer_mapping must be set on the subclass")

        raw = self._get_discriminator_value(data)
        raw_str = str(raw).strip().lower()

        for key, ser_cls in self.serializer_mapping.items():
            # Allow enum or plain string as mapping keys
            if isinstance(key, Enum):
                key_val = str(key.value)
            else:
                key_val = str(key)

            if key_val.lower() == raw_str:
                return ser_cls

        field = self.discriminator_field
        allowed = ", ".join(
            str(k.value if isinstance(k, Enum) else k)
            for k in self.serializer_mapping.keys()
        )
        raise serializers.ValidationError({
            field: f"Unsupported {field} '{raw}'. Allowed values: {allowed}"
        })

    def to_internal_value(self, data):
        ser_cls = self._select_serializer_class(data)
        nested = ser_cls(context=self.context, data=data)
        nested.is_valid(raise_exception=True)
        # keep reference if you want to delegate save()
        self._nested = nested
        return nested.validated_data

