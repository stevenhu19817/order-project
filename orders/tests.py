from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .validators import OrderValidator, NameValidator, PriceValidator, CurrencyValidator
from .services import OrderService, USDFormatter, TWDFormatter, FormatterFactory
from .views import OrderView
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory
import json


class TestValidators(TestCase):
    # 設置測試環境
    def setUp(self):
        self.order_validator = OrderValidator()

    # 測試姓名驗證器
    def test_name_validator(self):
        validator = NameValidator()
        # 正確姓名應該不會有錯誤
        self.assertEqual(validator.validate("Steven Hu"), [])
        # 含有非英文字符的姓名應該會有錯誤
        self.assertIn("non-English characters", validator.validate("Steven Hü")[0])
        # 未大寫的姓名應該會有錯誤
        self.assertIn("not capitalized", validator.validate("steven hu")[0])

    # 測試價格驗證器
    def test_price_validator(self):
        validator = PriceValidator()
        # 價格小於或等於2000應該不會有錯誤
        self.assertEqual(validator.validate("2000"), [])
        # 價格大於2000應該會有錯誤
        self.assertIn("over 2000", validator.validate("2001")[0])

    # 測試貨幣驗證器
    def test_currency_validator(self):
        validator = CurrencyValidator()
        # 正確的貨幣類型應該不會有錯誤
        self.assertEqual(validator.validate("USD"), [])
        self.assertEqual(validator.validate("TWD"), [])
        # 錯誤的貨幣類型應該會有錯誤
        self.assertIn("wrong", validator.validate("JPY")[0])

    # 測試訂單驗證器
    def test_order_validator(self):
        valid_data = {"name": "Steven Hu", "price": "2000", "currency": "USD"}
        # 正確的訂單數據應該會被成功驗證
        self.assertEqual(self.order_validator.validate(valid_data), valid_data)

        # 錯誤的訂單數據應該會引發驗證錯誤
        with self.assertRaises(ValidationError):
            self.order_validator.validate(
                {"name": "steven hü", "price": "2001", "currency": "JPY"}
            )


class TestServices(TestCase):
    # 測試USD格式化器
    def test_usd_formatter(self):
        formatter = USDFormatter()
        data = {"price": "100", "currency": "USD"}
        result = formatter.format(data)
        # USD格式化器應該將價格轉換為台幣價格
        self.assertEqual(result["price"], "3100")
        self.assertEqual(result["currency"], "TWD")

    # 測試台幣格式化器
    def test_twd_formatter(self):
        formatter = TWDFormatter()
        data = {"price": "100", "currency": "TWD"}
        result = formatter.format(data)
        # 台幣格式化器不應該改變價格和貨幣類型
        self.assertEqual(result, data)

    # 測試格式化器工廠
    def test_formatter_factory(self):
        # 檢查格式化器工廠是否能夠正確地返回格式化器
        self.assertIsInstance(FormatterFactory.get_formatter("USD"), USDFormatter)
        self.assertIsInstance(FormatterFactory.get_formatter("TWD"), TWDFormatter)
        # 如果貨幣類型不支持，應該返回台幣格式化器
        self.assertIsInstance(FormatterFactory.get_formatter("JPY"), TWDFormatter)

    # 測試訂單服務
    def test_order_service(self):
        service = OrderService()
        data = {"price": "100", "currency": "USD"}
        result = service.process(data)
        # 訂單服務應該能夠正確地格式化價格和貨幣類型
        self.assertEqual(result["price"], "3100")
        self.assertEqual(result["currency"], "TWD")


class TestOrderView(TestCase):
    # 設置測試環境
    def setUp(self):
        self.view = OrderView()
        self.factory = APIRequestFactory()

    # 使用mock測試POST請求
    @patch("orders.validators.OrderValidator.validate")
    @patch("orders.services.OrderService.process")
    def test_post(self, mock_process, mock_validate):
        mock_validate.return_value = {
            "id": "A0000001",
            "name": "Steven Hu",
            "address": {"city": "Taipei", "district": "Da'an", "street": "Xinyi Rd"},
            "price": "100",
            "currency": "USD",
        }
        mock_process.return_value = {
            "id": "A0000001",
            "name": "Steven Hu",
            "address": {"city": "Taipei", "district": "Da'an", "street": "Xinyi Rd"},
            "price": "3100",
            "currency": "TWD",
        }

        data = {
            "id": "A0000001",
            "name": "Steven Hu",
            "address": {"city": "Taipei", "district": "Da'an", "street": "Xinyi Rd"},
            "price": "100",
            "currency": "USD",
        }
        request = self.factory.post(
            "/orders/", json.dumps(data), content_type="application/json"
        )

        response = self.view.post(request)

        # 檢查回應的狀態碼和數據是否正確
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data,
            {
                "id": "A0000001",
                "name": "Steven Hu",
                "address": {
                    "city": "Taipei",
                    "district": "Da'an",
                    "street": "Xinyi Rd",
                },
                "price": "3100",
                "currency": "TWD",
            },
        )

    # 測試POST請求時傳入無效數據
    @patch("orders.validators.OrderValidator.validate")
    def test_post_invalid_data(self, mock_validate):
        mock_validate.side_effect = ValidationError({"name": ["Invalid name"]})

        data = {
            "id": "A0000001",
            "name": "invalid",
            "address": {"city": "Taipei", "district": "Da'an", "street": "Xinyi Rd"},
            "price": "100",
            "currency": "USD",
        }
        request = self.factory.post(
            "/orders/", json.dumps(data), content_type="application/json"
        )

        response = self.view.post(request)

        # 檢查回應的狀態碼和錯誤訊息是否正確
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
