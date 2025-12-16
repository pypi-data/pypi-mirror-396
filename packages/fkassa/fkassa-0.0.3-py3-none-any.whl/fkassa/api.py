import hashlib
import hmac
import time
from datetime import datetime
from typing import Any, Dict

import requests

from fkassa.enums import Currency, OrderStatus, PaymentSystem
from fkassa.exceptions import (
    FreeKassaAuthError,
    FreeKassaError,
    PaymentSystemUnavaliableError,
)
from fkassa.models import (
    BalanceResponse,
    CreateWithdrawalResponse,
    FreeKassaResponse,
    OrderResponse,
    OrdersResponse,
    PaymentSystemResponse,
    PaymentSystemsResponse,
    RefundResponse,
    ShopsResponse,
    WithdrawalPaymentSystemsResponse,
    WithdrawalsResponse,
)


class FKBase:
    shop_id: int
    api_key: str
    secret_word_1: str
    base_url: str

    def _generate_form_signature(self, order_id: str, amount: float, currency: Currency | str) -> str:
        """
        Генерация подписи для формы.

        :param params: Параметры формы.
        :return: Подпись в формате HMAC SHA-256.
        """
        return hashlib.md5(
            f"{self.shop_id}:{amount}:{self.secret_word_1}:{currency}:{order_id}".encode("utf-8")
        ).hexdigest()

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Генерация подписи для запроса.

        :param params: Параметры запроса.
        :return: Подпись в формате HMAC SHA-256.
        """
        # Сортируем параметры по ключам
        sorted_params = sorted(params.items())
        # Конкатенируем значения с разделителем '|'
        sign_string = "|".join(str(value) for _, value in sorted_params)
        # Генерируем HMAC SHA-256
        return hmac.new(self.api_key.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def request(self, route: str, data: Dict[str, Any] | None = None) -> FreeKassaResponse:
        """
        Отправка запроса к API.

        :param route: Маршрут запроса.
        :param data: Параметры запроса.
        :return: Ответ API в формате JSON.
        """
        # Clear None
        data = {k: v for k, v in (data or {}).items() if v is not None}

        data["shopId"] = self.shop_id
        data["nonce"] = time.time_ns()  # Уникальный ID запроса

        # Генерируем подпись
        data["signature"] = self._generate_signature(data)

        # Отправляем запрос
        response = requests.post(self.base_url + route, json=data)

        # Проверяем статус ответа
        if response.status_code == 401:
            raise FreeKassaAuthError(response.text)

        if response.status_code == 400:
            raise FreeKassaError(response.text)

        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code} - {response.text}")

        return FreeKassaResponse(**response.json())


class FreeKassa(FKBase):
    def __init__(
        self,
        shop_id: int,
        api_key: str,
        secret_word_1: str,
        base_url: str = "https://api.freekassa.com/v1/",
    ) -> None:
        """
        ## Инициализация класса FreeKassa.
        ### Документация: https://docs.freekassa.net/

        :param int shop_id: ID магазина.
        :param str api_key: API ключ.
        :param str secret_word_1: Секретное слово 1.
        :param str base_url: Базовый URL API.
        """
        self.shop_id = shop_id
        self.api_key = api_key
        self.secret_word_1 = secret_word_1
        self.base_url = base_url

    def create_payment_link(
        self,
        order_id: str,
        amount: float,
        currency: Currency | str,
        payment_system: PaymentSystem | int = PaymentSystem.SBP,
        phone: str | None = None,
        email: str | None = None,
        lang: str | None = None,
    ) -> str:
        """
        ## Создание ссылки на оплату.
        ### https://docs.freekassa.net/#section/1.-Vvedenie/1.3.-Nastrojka-formy-oplaty

        :param str order_id: Номер заказа в Вашем магазине.
        :param float amount: Сумма оплаты.
        :param `enums.Currency` currency: Валюта оплаты.
        :param `enums.PaymentSystem` payment_system: ID платежной системы.
        :param str phone: Телефон покупателя.
        :param str email: Email покупателя.
        :param str lang: Язык оплаты.

        :return str: Ссылка на оплату.
        :raises `exceptions.PaymentSystemUnavaliableError`: Платежная система недоступна.
        """
        # Формируем подпись
        sign = self._generate_form_signature(order_id, amount, currency)

        # Формируем параметры для ссылки
        params = {
            "m": self.shop_id,
            "oa": amount,
            "currency": currency,
            "o": order_id,
            "s": sign,
            "i": payment_system,
            "phone": phone,
            "em": email,
            "lang": lang,
        }
        params = {k: v for k, v in params.items() if v is not None}

        if payment_system:
            resp = self.check_payment_system_status(payment_system)
            if resp.type != "success":
                raise PaymentSystemUnavaliableError(resp.description)

        return "https://pay.fk.money/?" + "&".join(f"{key}={value}" for key, value in params.items())

    # aliases
    pay = create_payment_link
    payment = create_payment_link
    pay_url = create_payment_link
    payment_url = create_payment_link
    link = create_payment_link

    def get_orders(
        self,
        fk_id: str | None = None,
        order_id: int | None = None,
        order_status: OrderStatus | int | None = None,
        date_from: datetime | str | None = None,
        date_to: datetime | str | None = None,
        page: int = 1,
    ) -> OrdersResponse:
        """
        ## Получение списка заказов.
        ### https://docs.freekassa.net/#operation/getOrders

        :param int fk_id: Номер заказа Freekassa.
        :param str order_id: Номер заказа в Вашем магазине.
        :param `enums.OrderStatus` order_status: Статус заказа.
        :param datetime date_from: Дата начала периода.
        :param datetime date_to: Дата окончания периода.
        :param int page: Номер страницы результатов.

        :return `models.OrdersResponse`: Список заказов.
        """

        response = self.request(
            "orders",
            {
                "orderId": fk_id,
                "paymentId": order_id,
                "orderStatus": order_status,
                "dateFrom": date_from.strftime("%Y-%m-%d %H:%M:%S") if isinstance(date_from, datetime) else date_from,
                "dateTo": date_to.strftime("%Y-%m-%d %H:%M:%S") if isinstance(date_to, datetime) else date_to,
                "page": page,
            },
        )

        return OrdersResponse(type=response.type, pages=response.pages or 0, orders=response.orders)

    # alias
    orders = get_orders

    def create_order(
        self,
        order_id: str,
        amount: float,
        currency: Currency,
        email: str = "user@example.com",
        ip: str = "1.1.1.1",
        payment_system: PaymentSystem = PaymentSystem.SBP,
        tel: str | None = None,
        success_url: str | None = None,
        failure_url: str | None = None,
        notification_url: str | None = None,
        recurrent: bool | None = None,
        recurrent_period: str | None = None,
        recurrent_description: str | None = None,
        recurrent_order_id: int | None = None,
    ) -> OrderResponse:
        """
        ## Создать заказ и получить ссылку на оплату
        ### В некоторых случаях необходимо передавать дополнительные поля, узнать их можно в запросе getCurrencies (параметр fields)
        ### https://docs.freekassa.net/#operation/createOrder

        :param str order_id: Номер заказа в Вашем магазине.
        :param float amount: Сумма оплаты.
        :param `enums.Currency` currency: Валюта оплаты.
        :param str email: Email покупателя.
        :param str ip: IP покупателя.
        :param `enums.PaymentSystem` payment_system: Платежная система.
        :param str tel: Телефон плательщика, требуется в некоторых способах оплат.
        :param str success_url: Переопределение URL для перенаправления после успешной оплаты. (для включения данного параметра обратитесь в поддержку)
        :param str failure_url: Переопределение URL для перенаправления после неуспешной оплаты. (для включения данного параметра обратитесь в поддержку)
        :param str notification_url: Переопределение URL для перенаправления после оплаты. (для включения данного параметра обратитесь в поддержку)
        :param bool recurrent: Флаг рекуррентного платежа.
        :param str recurrent_period: Периодичность рекуррентного платежа (возможные значения - day, week, month, year).
        :param str recurrent_description: Описание рекуррентного платежа (от 10 до 200 символов)
        :param int recurrent_order_id: ID рекуррентного платежа для повторной оплаты.

        :return `models.OrderResponse`: Ответ API с информацией о созданном заказе.
        """
        params = {
            "paymentId": order_id,
            "amount": amount,
            "currency": currency,
            "email": email,
            "ip": ip,
            "i": payment_system,
            "tel": tel,
            "success_url": success_url,
            "failure_url": failure_url,
            "notification_url": notification_url,
            "recurrent": recurrent,
            "recurrent_period": recurrent_period,
            "recurrent_description": recurrent_description,
            "recurrent_order_id": recurrent_order_id,
        }

        if payment_system:
            resp = self.check_status(payment_system)
            if resp.type != "success":
                raise PaymentSystemUnavaliableError(resp.description)

        response = self.request("orders/create", params)

        if response.orderId is None or response.orderHash is None or response.location is None:
            raise FreeKassaError("Invalid response: missing order fields")

        return OrderResponse(
            type=response.type,
            orderId=response.orderId,
            orderHash=response.orderHash,
            location=response.location,
        )

    def refund_order(self, fk_id: int | None = None, order_id: str | None = None) -> RefundResponse:
        """
        ## Возврат заказа.
        ### https://docs.freekassa.net/#operation/refundOrder

        :param int fk_id: Номер заказа Freekassa.
        :param str order_id: Номер заказа в Вашем магазине.
        :return `models.RefundResponse`: Ответ API с информацией о возврате.
        """
        if fk_id is None and order_id is None:
            raise ValueError("Either fk_id or order_id must be provided.")

        response = self.request("orders/refund", {"orderId": fk_id, "paymentId": order_id})

        if response.id is None:
            raise FreeKassaError("Invalid response: missing refund id")

        return RefundResponse(type=response.type, id=response.id)

    # alias
    refund = refund_order

    def get_withdrawals(
        self,
        fk_id: str | None = None,
        order_id: int | None = None,
        order_status: OrderStatus | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
    ) -> WithdrawalsResponse:
        """
        ## Получение списка выплат.
        ### https://docs.freekassa.net/#operation/getWithdrawals

        :param int fk_id: Номер заказа Freekassa.
        :param str order_id: Номер заказа в Вашем магазине.
        :param `enums.OrderStatus` order_status: Статус заказа.
        :param datetime date_from: Дата с.
        :param datetime date_to: Дата по.
        :param int page: Страница

        :return `models.WithdrawalsResponse`: Ответ API с информацией о выплатах.
        """
        response = self.request(
            "withdrawals",
            {
                "orderId": fk_id,
                "paymentId": order_id,
                "orderStatus": order_status,
                "dateFrom": date_from,
                "dateTo": date_to,
                "page": page,
            },
        )

        return WithdrawalsResponse(type=response.type, pages=response.pages or 0, orders=response.orders or [])

    # alias
    withdrawals = get_withdrawals

    def create_withdrawal(
        self, payment_id: str, amount: float, currency: Currency, account: str
    ) -> CreateWithdrawalResponse:
        """
        ## Создание выплаты.
        ### https://docs.freekassa.net/#operation/createWithdrawal

        :param str payment_id: Номер заказа в Вашем магазине.
        :param float amount: Сумма выплаты.
        :param str currency: Валюта выплаты.
        :param str account: Кошелек для зачисления средств.

        :return `models.CreateWithdrawalResponse`: Ответ API с информацией о созданной выплате.
        """

        response = self.request(
            "withdrawals/create",
            {
                "paymentId": payment_id,
                "amount": amount,
                "currency": currency,
                "account": account,
            },
        )

        if response.data is None:
            raise FreeKassaError("Invalid response: missing withdrawal data")

        return CreateWithdrawalResponse(type=response.type, data=response.data)

    # alias
    withdrawal = create_withdrawal

    def get_balance(self) -> BalanceResponse:
        """
        ## Получение баланса магазина.
        ### https://docs.freekassa.net/#operation/getBalance

        :return `models.BalanceResponse`: Ответ API с информацией о балансе.
        """
        response = self.request("balance")

        return BalanceResponse(type=response.type, balance=response.balance or [])

    # alias
    balance = get_balance

    def get_currencies(self) -> PaymentSystemsResponse:
        """
        ## Получение списка всех платежных систем.
        ### https://docs.freekassa.net/#operation/getCurrencies

        :return `models.PaymentSystemsResponse`: Ответ API с информацией о доступных валютах.
        """
        response = self.request("currencies")

        return PaymentSystemsResponse(type=response.type, currencies=response.currencies or [])

    # aliases
    currencies = get_currencies
    systems = get_currencies
    payments = get_currencies
    payment_systems = get_currencies
    get_payment_systems = get_currencies

    def get_avaliable_payment_systems(self) -> PaymentSystemsResponse:
        """
        ## Получение списка доступных платежных систем.
        ### https://docs.freekassa.net/#operation/getCurrencies

        :return `models.PaymentSystemsResponse`: Ответ API с информацией о доступных платежных системах.
        """
        response = self.payments()
        response.currencies = [x for x in (response.currencies or []) if x.is_enabled]
        return response

    def check_payment_system_status(self, payment_system: PaymentSystem | int) -> PaymentSystemResponse:
        """
        ## Проверка доступности платежной системы.
        ### https://docs.freekassa.net/#operation/currencyStatus

        :param `enums.PaymentSystem` payment_system: ID платежной системы.
        :return `models.PaymentSystemResponse`: Ответ API с информацией о доступности платежной системы.
        """
        response = self.request(f"currencies/{payment_system}/status")

        return PaymentSystemResponse(type=response.type, description=getattr(response, "description", None))

    # aliases
    payment_system_status = check_payment_system_status
    check_payment_system = check_payment_system_status
    check_system = check_payment_system_status
    check_status = check_payment_system_status

    def get_withdrawal_currencies(self) -> WithdrawalPaymentSystemsResponse:
        """
        ## Получение списка валют для выплат.
        ### https://docs.freekassa.net/#operation/getWithdrawalsCurrencies

        :return `models.WithdrawalPaymentSystemsResponse`: Ответ API с информацией о доступных валютах для выплат.
        """
        response = self.request("withdrawals/currencies")

        return WithdrawalPaymentSystemsResponse(type=response.type, currencies=response.currencies or [])

    # aliases
    withdrawal_currencies = get_withdrawal_currencies
    withdrawal_payment_systems = get_withdrawal_currencies
    withdrawal_systems = get_withdrawal_currencies
    withdrawal_payments = get_withdrawal_currencies

    def get_shops(self) -> ShopsResponse:
        """
        Получение списка магазинов.

        :return `models.ShopsResponse`: Ответ API с информацией о магазинах.
        """
        response = self.request("shops")

        return ShopsResponse(type=response.type, shops=response.shops or [])

    # aliases
    shops = get_shops
