
from .exceptions import BaseError


def validate(model, raw_data, partial=False, strict=False, context=None):
    # context may contain data already validated
    data = dict(context) if context is not None else {}
    errors = {}

    # validate raw_data by the model fields
    for field_name, field in model._fields.iteritems():
        serialized_field_name = field.serialized_name or field_name
        try:
            value = raw_data[serialized_field_name]
        except KeyError:
            if data.get(field_name):
                # skip already validated data
                continue
            value = field.default

        if field.required and value is None:
            if not partial:
                errors[serialized_field_name] = [field.messages['required'], ]
        elif value is None:  # the field isn't required so the value can be None
            data[field_name] = None
        else:
            try:
                field.validate(value)
            except BaseError as e:
                errors[serialized_field_name] = e.messages
            else:
                data[field_name] = value
    if strict:
        rogue_field_errors = _check_for_unknown_fields(model, data)
        errors.update(rogue_field_errors)

    return data, errors


def _check_for_unknown_fields(model, data):
    errors = []
    rogues_found = set(data) - set(model._fields)
    if len(rogues_found) > 0:
        for field_name in rogues_found:
            errors[field_name] = [u'%s is an illegal field.' % field_name]
    return errors
