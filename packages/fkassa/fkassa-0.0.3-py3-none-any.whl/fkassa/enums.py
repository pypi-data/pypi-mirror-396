try:
    from enum import IntEnum, StrEnum  # type: ignore[attr-defined]
except ImportError:
    # for python < 3.12
    from enum import Enum

    IntEnum = Enum  # type: ignore[assignment,misc]
    StrEnum = Enum  # type: ignore[assignment,misc]


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    KZT = "KZT"


class PaymentSystemCurrency(StrEnum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    KZT = "KZT"

    # +crypto
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    USDT = "USDT"
    BNB = "BNB"
    TON = "TON"
    TRX = "TRX"


class PaymentSystem(IntEnum):
    FK_WALLET_RUB = 1
    FK_WALLET_USD = 2
    FK_WALLET_EUR = 3
    VISA_RUB = 4
    YOOMONEY = 6
    VISA_UAH = 7
    MASTERCARD_RUB = 8
    MASTERCARD_UAH = 9
    QIWI = 10
    VISA_EUR = 11
    MIR = 12
    ONLINE_BANK = 13
    USDT_ERC20 = 14
    USDT_TRC20 = 15
    BITCOIN_CASH = 16
    BNB = 17
    DASH = 18
    DOGECOIN = 19
    ZCASH = 20
    MONERO = 21
    WAVES = 22
    RIPPLE = 23
    BITCOIN = 24
    LITECOIN = 25
    ETHEREUM = 26
    STEAMPAY = 27
    MEGAFON = 28
    TELE2 = 30
    BEELINE = 31
    VISA_USD = 32
    PERFECT_MONEY_USD = 33
    SHIBA_INU = 34
    QIWI_API = 35
    CARD_RUB_API = 36
    GOOGLE_PAY = 37
    APPLE_PAY = 38
    TRON = 39
    WEBMONEY_WMZ = 40
    VISA_MASTER_CARD_KZT = 41
    SBP = 42
    SBER_PAY = 43
    SBP_API = 44
    TON = 45


class OrderStatus(IntEnum):
    NEW = 0
    PAID = 1
    REFUND = 6
    NOT_FOUND = 7
    ERROR = 8
    CANCEL = 9
