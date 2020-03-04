from uuid import UUID


def guess(value):
    if isinstance(value, (bool, int, float)):
        return value

    if not isinstance(value, str):
        raise ValueError()

    # That will will coerce uuid, boolean, and numbers as string into
    # their python type.  In particular, during the import process.
    # It is not clear in what situation one would want to represent a
    # number as a string.  Similarly for boolean and uuid.

    value = value.strip()
    if not value:
        raise ValueError()
    # Try to guess the Python object
    try:
        value = UUID(hex=value)
    except ValueError:
        try:
            value = int(value)
        except ValueError:
            if value.lower() == 'false':
                value = False
            elif value.lower() == 'true':
                value = True
            else:
                # just a string
                value = value
    return value
