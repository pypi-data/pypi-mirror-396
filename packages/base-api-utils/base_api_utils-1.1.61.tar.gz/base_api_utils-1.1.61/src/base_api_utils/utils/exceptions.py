import json
import logging
import traceback


from django.core.exceptions import FieldError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound, ErrorDetail

from .external_errors import handle_external_service_errors


def serialize_errors(errors, parent_key='', error_type=''):
    result = []

    if isinstance(errors, dict):
        for key, value in errors.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            result.extend(serialize_errors(value, full_key, error_type))

    elif isinstance(errors, list):
        for index, item in enumerate(errors):
            if isinstance(item, dict):
                result.extend(serialize_errors(item, parent_key, error_type))
            else:
                msg = str(item).rstrip('.') if isinstance(item, ErrorDetail) else str(item)

                # Try to extract errors from JSON
                try:
                    parsed_data = json.loads(msg)
                    if isinstance(parsed_data, dict) and 'errors' in parsed_data:
                        # Recursively process the extracted errors array
                        result.extend(serialize_errors(parsed_data['errors'], parent_key, error_type))
                        continue
                except (json.JSONDecodeError, ValueError):
                    # Not valid JSON, continue with normal processing
                    pass

                if parent_key and not parent_key in msg:
                    msg = f'{parent_key}: {msg}'
                result.append(msg)
    else:
        # Single messages
        msg = str(errors).rstrip('.') if isinstance(errors, ErrorDetail) else str(errors)

        # Try to extract errors from JSON
        try:
            parsed_data = json.loads(msg)
            if isinstance(parsed_data, dict) and 'errors' in parsed_data:
                result.extend(serialize_errors(parsed_data['errors'], parent_key, error_type))
                return result
        except (json.JSONDecodeError, ValueError):
            pass

        result.append(msg)

    return result

def custom_exception_handler(e, context):
    if isinstance(e, NotFound):
        errors = [e.__str__()]
        return Response({'message': 'Not found', 'errors': errors, 'code': 0},
                        status=status.HTTP_404_NOT_FOUND)

    if isinstance(e, FieldError):
        errors = [e.__str__()]
        return Response({'message': 'Validation Failed', 'errors': errors, 'code': 0},
                        status=status.HTTP_412_PRECONDITION_FAILED)

    if isinstance(e, ValidationError):
        errors = serialize_errors(e.detail, error_type='validation_error')
        return Response({'message': 'Validation Failed', 'errors': errors, 'code': 0},
                        status=status.HTTP_412_PRECONDITION_FAILED)

    # First check if DRF handles it
    response = exception_handler(e, context)

    if response is not None:
        return response

    external_error_response = handle_external_service_errors(e)
    if external_error_response:
        return external_error_response

    # Default to 500
    logging.getLogger('api').error(e)
    logging.getLogger('api').error(traceback.format_exc())
    return Response({'message': 'server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class S3Exception(Exception):
    def __init__(self, message):
        super().__init__(message)