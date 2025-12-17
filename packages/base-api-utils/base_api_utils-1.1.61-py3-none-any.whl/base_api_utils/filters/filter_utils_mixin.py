import re
from datetime import datetime, timezone
from rest_framework.exceptions import ValidationError

class FilterUtilsMixin:
    """Mixin with utilities for filtering and converting values."""

    filter_op = '='
    filters_separator = ','
    name_operator_separator = '__'
    filter_param = 'filter'
    filters_param = 'filter[]'
    list_separator = '&&'

    operator_map = {
        '>=': "__gte",
        '<=': "__lte",
        '>': "__gt",
        '<': "__lt",
        '==': "",
        '=@': "__icontains",
        '@@': "__istartswith"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_number_re = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')
        self.split_pattern = '|'.join(map(re.escape, self.operator_map.keys()))

    def is_numeric(self, value):
        return bool(self.is_number_re.match(str(value)))

    def is_boolean(self, value):
        return str(value).lower() in ['true', 'false']

    def epoch_to_datetime(self, value):
        try:
           return datetime.fromtimestamp(int(value), tz=timezone.utc)
        except (ValueError, TypeError):
            return None

    def filter_by_epoch_timestamp(self, queryset, name, op, value):
        dt = self.epoch_to_datetime(value)
        if dt is not None:
            return queryset.filter(**{f"{name}{op}": dt})
        else:
            return queryset.none()

    def parse_filter(self, filter_str):
        try:
            parts = re.split(f"({self.split_pattern})", filter_str)
            field_name = parts[0].strip()
            operator = self.operator_map.get(parts[1].strip())
            value = parts[2].strip()
        except ValueError:
            raise ValidationError("Invalid filter format. Expected 'key=value'.")
        return field_name, operator, value
