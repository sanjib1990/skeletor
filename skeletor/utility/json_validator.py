from jsonschema import Draft7Validator

from skeletor.utility.exceptions.validation_exception import ValidationException


class JSONSchemaValidator(object):

    @classmethod
    def draft_validator(cls, schema, instance):
        # Logger.log(Logger.INFO, "schema {0}, instance {1}".format(
        #     schema, instance))
        error_list = []
        draft = Draft7Validator(schema)
        if not draft.is_valid(instance):
            for error in sorted(draft.iter_errors(instance), key=lambda e: e.path):
                error_list.append(error.message)
            raise ValidationException(message="Invalid schema", validation=error_list)
        return error_list or None
