from .filter_utils_mixin import FilterUtilsMixin
from ..utils import safe_str_to_number
from django.db.models import Q
from django_filters import rest_framework as filters


class BaseFilter(FilterUtilsMixin, filters.FilterSet):
    def parse_list_values(self, value_str):
        """
        Parses a string with values separated by && and returns a list.
        Automatically converts to numbers if possible.
        """
        if self.list_separator not in value_str:
            return None

        values = []
        for val in value_str.split(self.list_separator):
            val = val.strip()
            if self.is_numeric(val):
                values.append(safe_str_to_number(val))
            elif self.is_boolean(val):
                values.append(str(val).lower() == 'true')
            else:
                values.append(val)
        return values

    def filter_field(self, queryset, filter_name, filter_op, filter_value):
        """
        Generic method for filtering based on dynamic comparisons.
        """
        if filter_op is None:
            return queryset

        is_exclude_filter = filter_name.endswith('__not_in')

        if is_exclude_filter:
            # Remove the _not_in suffix to get the actual field name
            base_field_name = filter_name[:-8]  # Remove '__not_in'

            # Parse the values in the list
            list_values = self.parse_list_values(filter_value)

            if list_values:
                # Apply exclusion with __in
                return queryset.exclude(**{f"{base_field_name}__in": list_values})
            else:
                # If not a list, apply simple exclusion
                value_to_filter = (
                    safe_str_to_number(filter_value)
                    if self.is_numeric(filter_value)
                    else filter_value
                )
                return queryset.exclude(**{f"{base_field_name}{filter_op}": value_to_filter})

        value_to_filter = (
            safe_str_to_number(filter_value)) \
            if filter_op in ['__gte', '__lte', '__gt', '__lt', ''] and self.is_numeric(filter_value) \
            else filter_value

        if self.is_boolean(value_to_filter):
            value_to_filter = str(value_to_filter).lower() == 'true'

        return queryset.filter(**{f"{filter_name}{filter_op}": value_to_filter})

    def apply_or_filters(self, queryset, or_filters):
        or_filter_subquery = Q()
        active_filters = self.get_filters()
        for or_filter in or_filters:
            filter_name, filter_op, filter_value = self.parse_filter(or_filter)
            if filter_name in active_filters:
                filter_name = active_filters[filter_name].field_name
            or_filter_subquery |= Q(**{f"{filter_name}{filter_op}": filter_value})
        queryset = queryset.filter(or_filter_subquery)
        return queryset

    def filter_queryset(self, queryset):
        """
        Overrides the `filter_queryset` method to apply filters dynamically.
        Invoked when Django applies filters to the query.

        Examples of possible filters:
        - filter[]=field1=@value1,field2>value2                                        (OR filter)

        - filter=field1=@value1,field2>value2                                          (OR filter)

        - filter[]=field1=@value1&filter[]=field2>value2                               (AND filter)

        - filter==field1@@value

        - filter[]=field1_not_in==10&&20&&30                                           (Exclude list)

        - filter[]=field1=@value1,field2=@value2&filter[]=field3=@value3               (OR then AND filter)
          Generates: ...WHERE (field1 LIKE '%value1%' OR field2 LIKE '%value2%') AND field3 LIKE '%value3%'
        """
        and_filter_key = 'and'
        or_filter_key = 'or'

        filter_without_brackets = self.data.get(self.filter_param, None)
        filter_with_brackets = self.data.getlist(self.filters_param, [])

        filter_category = {
            or_filter_key: filter_without_brackets.split(self.filters_separator) if filter_without_brackets else [],
            and_filter_key: []
        }

        for item in filter_with_brackets:
            if "," in item:
                filter_category[or_filter_key].extend(item.split(self.filters_separator))
            else:
                filter_category[and_filter_key].append(item)

        # Apply dynamic filters
        if filter_category[or_filter_key]:
            queryset = self.apply_or_filters(queryset, filter_category[or_filter_key])

        if not filter_category[and_filter_key]:
            return queryset

        # Get filters defined in the FilterSet
        active_filters = self.get_filters()

        for and_filter in filter_category[and_filter_key]:
            filter_name, filter_op, filter_value = self.parse_filter(and_filter)
            if filter_name in active_filters:
                filter_instance = active_filters[filter_name]

                if filter_instance.method == 'epoch_to_datetime':
                    queryset = self.filter_by_epoch_timestamp(queryset, filter_instance.field_name, filter_op, filter_value)
                    continue

                queryset = self.filter_field(queryset, filter_instance.field_name, filter_op, filter_value)

        return queryset
