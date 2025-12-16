from functools import wraps
from devvio_util.exceptions import (
    InternalInputValidationError,
    InternalOutputValidationError,
)
import devvio_util.logging as logging
logger = logging.DevvLogger("decorators")


def validate_with_schema(input_schema, output_schema):
    """Decorator to validate input with a given schema."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            input_data = input_schema().dump(args[1])
            error = input_schema().validate(input_data)
            if error:
                logger.warning(f"{error} : {input_data}")
                raise InternalInputValidationError(error)
            output = f(*args, **kwargs)
            output_data = output_schema().dump(output)
            error = output_schema().validate(output_data)
            if error:
                raise InternalOutputValidationError(error)
            return output

        return wrapper

    return decorator
