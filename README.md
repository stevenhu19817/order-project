# 資料庫測驗

## 題目一
請寫出一條查詢語句 (SQL)，列出在 2023 年 5 月下訂的訂單，使用台幣付款且5月總金額最多的前 10 筆的旅宿 ID (bnb_id), 旅宿名稱 (bnb_name), 5 月總金額 (may_amount)

```sql
SELECT
    bnb_id, b.name AS bnb_name, SUM(o.amount) AS may_amount
FROM
    orders o
    JOIN bnbs b
        ON o.bnb_id = b.id
WHERE
    o.currency = 'TWD'
    AND o.created_at >= '2023-05-01 00:00:00'
    AND o.created_at < '2023-06-01 00:00:00'
GROUP BY
    b.id, bnb_name
ORDER BY
    may_amount DESC
LIMIT 10;
```

## 題目二
在題目一的執行下，我們發現 SQL 執行速度很慢，您會怎麼去優化？請闡述您怎麼判斷與優化的方式


1. 使用 EXPLAIN 來查看查詢計畫，包括 type 及 possible_keys
2. 發現 orders 表 type 為 ALL 全表掃描（const 或 eq_ref 為最佳），或查看 rows 是否有大量的行被讀取，可能為性能瓶頸主要原因，假如 possible_keys 中有索引但 key 為 NULL，表示沒有使用任何索引
    - 添加適當索引減少全表掃描情況
    - 優化查詢語句，避免使用 SELECT * 或 WHERE 到多餘的東西
3. 建立索引
   ```sql
   CREATE INDEX idx_orders_currency ON orders (currency);
   CREATE INDEX idx_orders_created_at ON orders (created_at);
   ```
   或多列索引（同時使用 WHERE 時才能使用，若只有 WHERE 其中一個 currency 或 created_at 則無法使用）
   ```sql
   CREATE INDEX idx_orders_currency_created_at ON orders (currency, created_at);
   ```
4. 檢查索引
   ```sql
   SHOW INDEX FROM orders;
   EXPLAIN SELECT * FROM orders WHERE currency = 'TWD';
   ```
   重新執行 EXPLAIN 檢查 possible_keys 是否有使用索引
5. 更新統計訊息
   ```sql
   ANALYZE TABLE orders;
   ```

# API 實作測驗
## SOLID 原則的應用

## 1. 單一職責原則 (Single Responsibility Principle, SRP)

每個類別都具有單一責任，專注於處理一個功能，這樣可以提高可維護性和擴展性：
- `OrderView`：負責處理 HTTP 請求。
- `OrderService`：負責處理業務邏輯，尤其是格式轉換部分。
- `OrderValidator`：負責訂單數據的驗證，透過具體的驗證器類別（如 `NameValidator`、`PriceValidator`）。
- `FormatterFactory`：負責提供適當的貨幣格式化策略。

## 2. 開放封閉原則 (Open/Closed Principle, OCP)

系統對於擴展是開放的，但對於修改是封閉的：
- **格式轉換**：新貨幣格式只需新增對應的 `CurrencyFormatterStrategy` 子類別，無需修改現有的程式碼，只需透過 `FormatterFactory.register_formatter` 註冊新的格式化器。
- **驗證邏輯**：同樣地，新的驗證邏輯可以通過繼承 `Validator` 類別來實現，而不需要修改現有的驗證器或 `OrderValidator`。

## 3. 里氏替換原則 (Liskov Substitution Principle, LSP)

子類別必須能夠替換其父類別，並且不改變程式的正確性：
- `USDFormatter` 和 `TWDFormatter` 都是基於 `CurrencyFormatterStrategy` 類別實現，這意味著可以替換不同的子類別（如 `USDFormatter`），而不影響 `OrderService` 的邏輯。
- 各個 `Validator` 子類別（如 `NameValidator`、`PriceValidator`）也都遵循這個原則，任何具體的驗證邏輯可以替換或擴展而不影響主邏輯。

## 4. 介面隔離原則 (Interface Segregation Principle, ISP)

介面應該只包含客戶端需要的方法，過於龐大的介面應該被拆分：
- `CurrencyFormatterStrategy` 和 `Validator`：這些抽象父類提供的介面非常具體，僅包含所需的方法（如 `format` 和 `validate`），沒有多餘的方法或責任，這符合介面隔離原則。

## 5. 依賴反轉原則 (Dependency Inversion Principle, DIP)

高層模組不應該依賴低層模組，兩者都應該依賴於抽象：
- `OrderService` 依賴於抽象的 `CurrencyFormatterStrategy`，而不是具體的 `USDFormatter` 或 `TWDFormatter`，這樣可以很容易地替換或擴展不同的格式轉換邏輯。
- `OrderValidator` 依賴於 `Validator` 抽象介面，而不是具體的驗證器實現，這樣可以保持高層模組（如 `OrderView`）與具體邏輯的分離，增加靈活性。

---

# 設計模式

## 1. 策略模式 (Strategy Pattern)

- `CurrencyFormatterStrategy` 是策略模式的實例，它允許動態選擇不同的貨幣格式轉換策略。`OrderService` 根據訂單中的貨幣類型，選擇適當的格式化策略（如 `USDFormatter` 或 `TWDFormatter`）。

---

## 2. 工廠模式 (Factory Pattern)

- `FormatterFactory` 提供工廠方法，負責根據給定的貨幣類型創建合適的 `CurrencyFormatterStrategy`。這符合工廠模式，避免了在 `OrderService` 中直接創建具體的格式器類別，降低耦合度。

---

## 3. 模板方法模式 (Template Method Pattern)

- 在 `Validator` 和各個具體的驗證器類別中，父類別定義了抽象方法 `validate`，具體的驗證器實現細節。這種設計符合模板方法模式，允許子類別在不改變主結構的情況下定義具體的行為。

---

## 4. 依賴注入 (Dependency Injection)

- `OrderView` 將 `OrderService` 和 `OrderValidator` 注入到視圖中，這樣允許我們在不同的場景下傳遞不同的實現，這是依賴注入的一種實現方式，有助於提高程式碼的可測試性和靈活性。

# Setup and Usage

## Prerequisites

- Docker
- Docker Compose

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Clone the Repository

```bash
git clone https://github.com/stevenhu19817/order-project.git
cd order-project
```

### Build and Run with Docker

1. Build the Docker images:
   ```bash
   docker-compose build
   ```

2. Start the Docker containers:
   ```bash
   docker-compose up -d
   ```

3. Run database migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

### Accessing the API

Once the containers are up and running, you can access the API at:

http://127.0.0.1:8000/api/orders/

## Testing

To run tests:

```bash
docker-compose exec web python manage.py test orders
```