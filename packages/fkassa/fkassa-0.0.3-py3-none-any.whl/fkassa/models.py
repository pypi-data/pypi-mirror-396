from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from fkassa.enums import Currency, OrderStatus, PaymentSystemCurrency


class FreeKassaOrder(BaseModel):
    order_id: str = Field(alias="merchant_order_id")
    fk_id: int = Field(alias="fk_order_id")
    amount: float
    currency: Currency
    email: str
    date: datetime = Field(alias="date")
    status: OrderStatus
    commission: int
    payer_account: str | None
    amount_to: float
    claim: int


class FreeKassaResponse(BaseModel, extra="allow"):
    type: Literal["success", "error"]
    pages: Optional[int] = None
    orders: list[Any] = Field(default_factory=list)
    orderId: Optional[int] = None
    orderHash: Optional[str] = None
    location: Optional[str] = None
    id: Optional[int] = None
    data: Optional[Any] = None
    balance: list[Any] = Field(default_factory=list)
    currencies: list[Any] = Field(default_factory=list)
    description: Optional[str] = None
    shops: list[Any] = Field(default_factory=list)


class OrdersResponse(BaseModel):
    type: str
    pages: int
    orders: list[FreeKassaOrder]


class OrderResponse(BaseModel):
    type: str
    fk_id: int = Field(alias="orderId")
    hash: str = Field(alias="orderHash")
    url: str = Field(alias="location")


class PaymentSystemResponse(BaseModel):
    type: str
    description: Optional[str] = ""


class CurrencyBalance(BaseModel):
    currency: Currency
    value: float


class BalanceResponse(BaseModel):
    type: str
    balance: list[CurrencyBalance]


class RefundResponse(BaseModel):
    type: str
    id: int


class PaymentSystemLimits(BaseModel):
    min: float
    max: float


class PaymentSystemFee(BaseModel):
    merchant: float
    user: float
    default: float


class PaymentSystemField(BaseModel):
    type: str
    placeholder: str
    value: str
    required: bool
    validation: str = Field(alias="validate")


class PaymentSystemFields(BaseModel):
    email: PaymentSystemField | None = None
    tel: PaymentSystemField | None = None


class PaymentSystemInfo(BaseModel):
    id: int
    name: str
    currency: PaymentSystemCurrency
    fields: PaymentSystemFields
    is_enabled: bool
    is_favorite: bool
    limits: PaymentSystemLimits
    fee: PaymentSystemFee


class CurrenciesResponse(BaseModel):
    type: str
    currencies: list[PaymentSystemInfo]


# alias
PaymentSystemsResponse = CurrenciesResponse


class WithdrawalPaymentSystemInfo(BaseModel):
    id: int
    name: str
    min: float
    max: float
    currency: PaymentSystemCurrency
    can_exchange: bool


class WithdrawalCurrenciesResponse(BaseModel):
    type: str
    currencies: list[WithdrawalPaymentSystemInfo]


# alias
WithdrawalPaymentSystemsResponse = WithdrawalCurrenciesResponse


class WithdrawalsItem(BaseModel):
    id: int
    amount: float
    currency: Currency
    ext_currency_id: int
    account: str
    date: datetime
    status: OrderStatus


class WithdrawalsResponse(BaseModel):
    type: str
    pages: int
    orders: list[WithdrawalsItem]


class CreateWithdrawalData(BaseModel):
    id: int


class CreateWithdrawalResponse(BaseModel):
    type: str
    data: CreateWithdrawalData


class Shop(BaseModel):
    id: int
    name: str
    site_url: str
    activated: bool


class ShopsResponse(BaseModel):
    type: str
    shops: list[Shop]
