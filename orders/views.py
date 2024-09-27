from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from django.http import HttpRequest
from .serializers import OrderSerializer
from .validators import OrderValidator
from .services import OrderService, FormatterFactory


class OrderView(APIView):
    def __init__(self, validator=None, service=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = validator or OrderValidator()
        self.service = service or OrderService(FormatterFactory)

    def post(self, request):
        if isinstance(request, HttpRequest):
            data = JSONParser().parse(request)
        else:
            data = request.data

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            try:
                validated_data = self.validator.validate(serializer.validated_data)
                processed_data = self.service.process(validated_data)
                return Response(processed_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
