from rest_framework import serializers


class AddressSerializer(serializers.Serializer):
    city = serializers.CharField()
    district = serializers.CharField()
    street = serializers.CharField()


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    address = AddressSerializer()
    price = serializers.CharField()
    currency = serializers.CharField()
