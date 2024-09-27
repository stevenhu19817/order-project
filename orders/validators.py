from abc import ABC, abstractmethod
from rest_framework.exceptions import ValidationError


class Validator(ABC):
    @abstractmethod
    def validate(self, value):
        pass


class NameValidator(Validator):
    def validate(self, name):
        errors = []
        if any(ord(char) > 127 for char in name):
            errors.append("Name contains non-English characters")
        words = name.split()
        if any(not word[0].isupper() for word in words):
            errors.append("Name is not capitalized")
        return errors


class PriceValidator(Validator):
    def validate(self, price):
        if int(price) > 2000:
            return ["Price is over 2000"]
        return []


class CurrencyValidator(Validator):
    def validate(self, currency):
        if currency not in ["TWD", "USD"]:
            return ["Currency format is wrong"]
        return []


class OrderValidator:
    def __init__(self):
        self.validators = {
            "name": NameValidator(),
            "price": PriceValidator(),
            "currency": CurrencyValidator(),
        }

    def validate(self, data):
        errors = {}
        for field, validator in self.validators.items():
            if field in data:
                field_errors = validator.validate(data[field])
                if field_errors:
                    errors[field] = field_errors
        if errors:
            raise ValidationError(errors)
        return data
