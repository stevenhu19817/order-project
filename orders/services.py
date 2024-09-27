from abc import ABC, abstractmethod


class CurrencyFormatterStrategy(ABC):
    @abstractmethod
    def format(self, data):
        pass


class USDFormatter(CurrencyFormatterStrategy):
    def format(self, data):
        data["price"] = str(round(int(data["price"]) * 31))
        data["currency"] = "TWD"
        return data


class TWDFormatter(CurrencyFormatterStrategy):
    def format(self, data):
        return data


class FormatterFactory:
    _formatters = {"USD": USDFormatter, "TWD": TWDFormatter}

    @classmethod
    def get_formatter(cls, currency):
        formatter_class = cls._formatters.get(currency, TWDFormatter)
        return formatter_class()

    @classmethod
    def register_formatter(cls, currency, formatter_class):
        cls._formatters[currency] = formatter_class


class OrderServiceInterface(ABC):
    @abstractmethod
    def process(self, data):
        pass


class OrderService(OrderServiceInterface):
    def __init__(self, formatter_factory=FormatterFactory):
        self.formatter_factory = formatter_factory

    def process(self, data):
        formatter = self.formatter_factory.get_formatter(data["currency"])
        return formatter.format(data)
