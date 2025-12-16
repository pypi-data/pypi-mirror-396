"""Pydantic models for AlpacaFarmer - Alpaca Markets API wrapper.

This module contains all request and response models organized by API:
- Shared Enums
- Base Models
- Account Models (Trader API)
- Order Models
- Position Models
- Asset Models
- Market Data Models
- Broker API Models
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================
# ENUMS (Shared across APIs)
# ============================================


class OrderSide(str, Enum):
    """Order side - buy or sell."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type for trade execution."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class TimeInForce(str, Enum):
    """Time in force for order validity."""

    DAY = "day"
    GTC = "gtc"
    OPG = "opg"
    CLS = "cls"
    IOC = "ioc"
    FOK = "fok"


class OrderStatus(str, Enum):
    """Order status values."""

    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    DONE_FOR_DAY = "done_for_day"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REPLACED = "replaced"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    PENDING_NEW = "pending_new"
    ACCEPTED = "accepted"
    STOPPED = "stopped"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    CALCULATED = "calculated"


class OrderClass(str, Enum):
    """Order class for different order types."""

    SIMPLE = "simple"
    BRACKET = "bracket"
    OCO = "oco"
    OTO = "oto"
    MLEG = "mleg"


class QueryOrderStatus(str, Enum):
    """Query order status for filtering orders."""

    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class PositionIntent(str, Enum):
    """Position intent for options orders."""

    BUY_TO_OPEN = "buy_to_open"
    BUY_TO_CLOSE = "buy_to_close"
    SELL_TO_OPEN = "sell_to_open"
    SELL_TO_CLOSE = "sell_to_close"


class AssetClass(str, Enum):
    """Asset class types."""

    US_EQUITY = "us_equity"
    CRYPTO = "crypto"
    US_OPTION = "us_option"


class AssetStatus(str, Enum):
    """Asset trading status."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class PositionSide(str, Enum):
    """Position side - long or short."""

    LONG = "long"
    SHORT = "short"


class AccountStatus(str, Enum):
    """Account status values."""

    ONBOARDING = "ONBOARDING"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMITTED = "SUBMITTED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    INACTIVE = "INACTIVE"
    ACCOUNT_CLOSED = "ACCOUNT_CLOSED"


class AccountType(str, Enum):
    """Account type for broker accounts."""

    TRADING = "trading"
    CUSTODIAL = "custodial"


class AccountSubType(str, Enum):
    """Account sub-type for broker accounts."""

    INDIVIDUAL = "individual"
    JOINT = "joint"
    IRA_TRADITIONAL = "ira_traditional"
    IRA_ROTH = "ira_roth"


class SupportedCurrencies(str, Enum):
    """Supported currencies for accounts."""

    USD = "USD"


class Timeframe(str, Enum):
    """Timeframe for market data bars."""

    MIN_1 = "1Min"
    MIN_5 = "5Min"
    MIN_15 = "15Min"
    MIN_30 = "30Min"
    HOUR_1 = "1Hour"
    HOUR_4 = "4Hour"
    DAY_1 = "1Day"
    WEEK_1 = "1Week"
    MONTH_1 = "1Month"


class DataFeed(str, Enum):
    """Market data feed source."""

    IEX = "iex"
    SIP = "sip"


class TransferDirection(str, Enum):
    """Transfer direction for fund movements."""

    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"


class TransferType(str, Enum):
    """Transfer type."""

    ACH = "ach"
    WIRE = "wire"


class TransferTiming(str, Enum):
    """Transfer timing options."""

    IMMEDIATE = "immediate"


class TransferStatus(str, Enum):
    """Transfer status."""

    QUEUED = "QUEUED"
    PENDING = "PENDING"
    SENT_TO_CLEARING = "SENT_TO_CLEARING"
    APPROVED = "APPROVED"
    COMPLETE = "COMPLETE"
    CANCELED = "CANCELED"
    RETURNED = "RETURNED"


class FeePaymentMethod(str, Enum):
    """Fee payment method for transfers."""

    USER = "user"
    INVOICE = "invoice"


class BankAccountType(str, Enum):
    """Bank account type for ACH relationships."""

    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class BankCodeType(str, Enum):
    """Bank code type for wire transfers."""

    ABA = "ABA"
    BIC = "BIC"


class JournalEntryType(str, Enum):
    """Journal entry type for fund movements between accounts."""

    JNLC = "JNLC"  # Cash journal
    JNLS = "JNLS"  # Security journal


class JournalStatus(str, Enum):
    """Journal entry status."""

    QUEUED = "queued"
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELED = "canceled"
    REJECTED = "rejected"


class FundingSource(str, Enum):
    """Source of funding for account."""

    EMPLOYMENT_INCOME = "employment_income"
    INVESTMENTS = "investments"
    INHERITANCE = "inheritance"
    BUSINESS_INCOME = "business_income"
    SAVINGS = "savings"
    FAMILY = "family"


class TaxIdType(str, Enum):
    """Tax ID type."""

    USA_SSN = "USA_SSN"
    USA_ITIN = "USA_ITIN"


class ContractType(str, Enum):
    """Option contract type."""

    CALL = "call"
    PUT = "put"


class ExerciseStyle(str, Enum):
    """Option exercise style."""

    AMERICAN = "american"
    EUROPEAN = "european"


class CorporateActionType(str, Enum):
    """Corporate action type."""

    DIVIDEND = "dividend"
    MERGER = "merger"
    SPINOFF = "spinoff"
    SPLIT = "split"


class CorporateActionDateType(str, Enum):
    """Corporate action date type for filtering."""

    DECLARATION_DATE = "declaration_date"
    EX_DATE = "ex_date"
    RECORD_DATE = "record_date"
    PAYABLE_DATE = "payable_date"


class DocumentType(str, Enum):
    """Document type for uploads."""

    IDENTITY_VERIFICATION = "identity_verification"
    ADDRESS_VERIFICATION = "address_verification"
    DATE_OF_BIRTH_VERIFICATION = "date_of_birth_verification"
    TAX_ID_VERIFICATION = "tax_id_verification"
    ACCOUNT_APPROVAL_LETTER = "account_approval_letter"
    W8BEN = "w8ben"


class Sort(str, Enum):
    """Sort direction."""

    ASC = "asc"
    DESC = "desc"


class AccountEntities(str, Enum):
    """Account entities to include in responses."""

    CONTACT = "contact"
    IDENTITY = "identity"
    DISCLOSURES = "disclosures"
    AGREEMENTS = "agreements"
    DOCUMENTS = "documents"
    TRUSTED_CONTACT = "trusted_contact"


# ============================================
# BASE MODELS
# ============================================


class AlpacaBaseModel(BaseModel):
    """Base model with common configuration for all Alpaca models."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


# ============================================
# ACCOUNT MODELS (Trader API)
# ============================================


class Account(AlpacaBaseModel):
    """Trading account information."""

    id: str = Field(..., description="Account ID")
    account_number: str = Field(..., description="Account number")
    status: AccountStatus = Field(..., description="Account status")
    currency: str = Field(..., description="Account currency (e.g., USD)")
    cash: Decimal = Field(..., description="Cash balance")
    portfolio_value: Decimal = Field(..., description="Total portfolio value")
    buying_power: Decimal = Field(..., description="Current buying power")
    daytrading_buying_power: Decimal = Field(
        ..., description="Day trading buying power"
    )
    regt_buying_power: Decimal = Field(..., description="Reg T buying power")
    equity: Decimal = Field(..., description="Account equity")
    last_equity: Decimal = Field(..., description="Previous day's equity")
    long_market_value: Decimal = Field(..., description="Long positions market value")
    short_market_value: Decimal = Field(
        ..., description="Short positions market value"
    )
    initial_margin: Decimal = Field(..., description="Initial margin requirement")
    maintenance_margin: Decimal = Field(
        ..., description="Maintenance margin requirement"
    )
    last_maintenance_margin: Decimal = Field(
        ..., description="Previous day's maintenance margin"
    )
    sma: Decimal = Field(..., description="Special memorandum account value")
    pattern_day_trader: bool = Field(
        ..., description="Whether account is flagged as pattern day trader"
    )
    trading_blocked: bool = Field(..., description="Whether trading is blocked")
    transfers_blocked: bool = Field(..., description="Whether transfers are blocked")
    account_blocked: bool = Field(..., description="Whether account is blocked")
    trade_suspended_by_user: bool = Field(
        ..., description="Whether trading is suspended by user"
    )
    multiplier: str = Field(..., description="Leverage multiplier")
    shorting_enabled: bool = Field(..., description="Whether shorting is enabled")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AccountConfiguration(AlpacaBaseModel):
    """Account configuration settings."""

    dtbp_check: Literal["both", "entry", "exit"] = Field(
        ..., description="Day trading buying power check"
    )
    trade_confirm_email: Literal["all", "none"] = Field(
        ..., description="Trade confirmation email setting"
    )
    suspend_trade: bool = Field(..., description="Whether trading is suspended")
    no_shorting: bool = Field(..., description="Whether shorting is disabled")
    fractional_trading: bool = Field(
        ..., description="Whether fractional trading is enabled"
    )
    max_margin_multiplier: str = Field(..., description="Maximum margin multiplier")
    pdt_check: Literal["entry", "exit"] = Field(
        ..., description="Pattern day trader check setting"
    )
    ptp_no_exception_entry: bool = Field(
        ..., description="PTP no exception entry setting"
    )


# ============================================
# ORDER MODELS
# ============================================


class TakeProfitRequest(AlpacaBaseModel):
    """Take profit configuration for bracket orders."""

    limit_price: Decimal = Field(..., gt=0, description="Limit price for take profit")


class StopLossRequest(AlpacaBaseModel):
    """Stop loss configuration for bracket orders."""

    stop_price: Decimal = Field(..., gt=0, description="Stop price for stop loss")
    limit_price: Optional[Decimal] = Field(
        None, gt=0, description="Limit price for stop loss (makes it a stop-limit)"
    )


class OptionLegRequest(AlpacaBaseModel):
    """Option leg for multi-leg orders."""

    symbol: str = Field(..., description="Option symbol")
    ratio_qty: float = Field(..., description="Ratio quantity for this leg")
    side: Optional[OrderSide] = Field(None, description="Order side")
    position_intent: Optional[PositionIntent] = Field(
        None, description="Position intent"
    )


class OrderRequest(AlpacaBaseModel):
    """Request model for creating an order."""

    symbol: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Symbol to trade"
    )
    qty: Optional[Decimal] = Field(None, gt=0, description="Number of shares")
    notional: Optional[Decimal] = Field(None, gt=0, description="Dollar amount to trade")
    side: Optional[OrderSide] = Field(None, description="Buy or sell")
    type: OrderType = Field(..., description="Order type")
    time_in_force: TimeInForce = Field(..., description="Time in force")
    limit_price: Optional[Decimal] = Field(None, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop price")
    trail_price: Optional[Decimal] = Field(
        None, gt=0, description="Trail price for trailing stop"
    )
    trail_percent: Optional[Decimal] = Field(
        None, gt=0, description="Trail percent for trailing stop"
    )
    extended_hours: bool = Field(False, description="Allow extended hours trading")
    client_order_id: Optional[str] = Field(
        None, max_length=48, description="Client order ID"
    )
    order_class: Optional[OrderClass] = Field(None, description="Order class")
    take_profit: Optional[TakeProfitRequest] = Field(
        None, description="Take profit configuration for bracket orders"
    )
    stop_loss: Optional[StopLossRequest] = Field(
        None, description="Stop loss configuration for bracket orders"
    )
    position_intent: Optional[PositionIntent] = Field(
        None, description="Position intent for options"
    )
    legs: Optional[list[OptionLegRequest]] = Field(
        None, description="Option legs for multi-leg orders"
    )


class Order(AlpacaBaseModel):
    """Response model for order data."""

    id: str = Field(..., description="Order ID")
    client_order_id: str = Field(..., description="Client order ID")
    created_at: datetime = Field(..., description="Order creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp")
    filled_at: Optional[datetime] = Field(None, description="Fill timestamp")
    expired_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    canceled_at: Optional[datetime] = Field(None, description="Cancellation timestamp")
    failed_at: Optional[datetime] = Field(None, description="Failure timestamp")
    replaced_at: Optional[datetime] = Field(None, description="Replacement timestamp")
    replaced_by: Optional[str] = Field(None, description="ID of replacing order")
    replaces: Optional[str] = Field(None, description="ID of replaced order")
    asset_id: str = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Symbol")
    asset_class: AssetClass = Field(..., description="Asset class")
    notional: Optional[Decimal] = Field(None, description="Notional value")
    qty: Optional[Decimal] = Field(None, description="Quantity ordered")
    filled_qty: Decimal = Field(..., description="Quantity filled")
    filled_avg_price: Optional[Decimal] = Field(None, description="Average fill price")
    order_class: Optional[OrderClass] = Field(None, description="Order class")
    order_type: OrderType = Field(..., alias="type", description="Order type")
    side: OrderSide = Field(..., description="Order side")
    time_in_force: TimeInForce = Field(..., description="Time in force")
    limit_price: Optional[Decimal] = Field(None, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, description="Stop price")
    status: OrderStatus = Field(..., description="Order status")
    extended_hours: bool = Field(False, description="Extended hours enabled")
    legs: Optional[list["Order"]] = Field(None, description="Order legs for complex orders")
    trail_percent: Optional[Decimal] = Field(None, description="Trail percent")
    trail_price: Optional[Decimal] = Field(None, description="Trail price")
    hwm: Optional[Decimal] = Field(None, description="High water mark for trailing stop")

    @field_validator("order_class", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None for order_class.

        The Alpaca API returns an empty string for simple orders
        rather than null or 'simple'.
        """
        if v == "":
            return None
        return v


class ReplaceOrderRequest(AlpacaBaseModel):
    """Request model for replacing an existing order."""

    qty: Optional[int] = Field(None, gt=0, description="New quantity")
    time_in_force: Optional[TimeInForce] = Field(None, description="New time in force")
    limit_price: Optional[Decimal] = Field(None, gt=0, description="New limit price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="New stop price")
    trail: Optional[Decimal] = Field(None, gt=0, description="New trail value")
    client_order_id: Optional[str] = Field(
        None, max_length=48, description="New client order ID"
    )


class ClosePositionRequest(AlpacaBaseModel):
    """Request model for closing a position."""

    qty: Optional[str] = Field(None, description="Number of shares to liquidate")
    percentage: Optional[str] = Field(
        None, description="Percentage of shares to liquidate"
    )


# ============================================
# POSITION MODELS
# ============================================


class Position(AlpacaBaseModel):
    """Position information for a held asset."""

    asset_id: str = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Symbol")
    exchange: str = Field(..., description="Exchange")
    asset_class: AssetClass = Field(..., description="Asset class")
    asset_marginable: bool = Field(..., description="Whether asset is marginable")
    qty: Decimal = Field(..., description="Quantity held")
    avg_entry_price: Decimal = Field(..., description="Average entry price")
    side: PositionSide = Field(..., description="Position side (long/short)")
    market_value: Decimal = Field(..., description="Current market value")
    cost_basis: Decimal = Field(..., description="Cost basis")
    unrealized_pl: Decimal = Field(..., description="Unrealized profit/loss")
    unrealized_plpc: Decimal = Field(
        ..., description="Unrealized profit/loss percentage"
    )
    unrealized_intraday_pl: Decimal = Field(
        ..., description="Unrealized intraday profit/loss"
    )
    unrealized_intraday_plpc: Decimal = Field(
        ..., description="Unrealized intraday profit/loss percentage"
    )
    current_price: Decimal = Field(..., description="Current price")
    lastday_price: Decimal = Field(..., description="Previous day's closing price")
    change_today: Decimal = Field(..., description="Price change today percentage")
    qty_available: Decimal = Field(..., description="Quantity available for trading")


# ============================================
# ASSET MODELS
# ============================================


class Asset(AlpacaBaseModel):
    """Asset information."""

    id: str = Field(..., description="Asset ID")
    asset_class: AssetClass = Field(..., alias="class", description="Asset class")
    exchange: str = Field(..., description="Primary exchange")
    symbol: str = Field(..., description="Symbol")
    name: str = Field(..., description="Asset name")
    status: AssetStatus = Field(..., description="Asset status")
    tradable: bool = Field(..., description="Whether asset is tradable")
    marginable: bool = Field(..., description="Whether asset is marginable")
    shortable: bool = Field(..., description="Whether asset is shortable")
    easy_to_borrow: bool = Field(..., description="Whether asset is easy to borrow")
    fractionable: bool = Field(..., description="Whether fractional trading is allowed")
    maintenance_margin_requirement: Optional[Decimal] = Field(
        None, description="Maintenance margin requirement"
    )
    min_order_size: Optional[Decimal] = Field(None, description="Minimum order size")
    min_trade_increment: Optional[Decimal] = Field(
        None, description="Minimum trade increment"
    )
    price_increment: Optional[Decimal] = Field(None, description="Price increment")


# ============================================
# MARKET DATA MODELS
# ============================================


class Bar(AlpacaBaseModel):
    """OHLCV bar data."""

    t: datetime = Field(..., alias="timestamp", description="Bar timestamp")
    o: Decimal = Field(..., alias="open", description="Open price")
    h: Decimal = Field(..., alias="high", description="High price")
    l: Decimal = Field(..., alias="low", description="Low price")
    c: Decimal = Field(..., alias="close", description="Close price")
    v: int = Field(..., alias="volume", description="Volume")
    n: Optional[int] = Field(None, alias="trade_count", description="Trade count")
    vw: Optional[Decimal] = Field(None, alias="vwap", description="VWAP")


class Quote(AlpacaBaseModel):
    """Quote data."""

    t: datetime = Field(..., alias="timestamp", description="Quote timestamp")
    ax: str = Field(..., alias="ask_exchange", description="Ask exchange")
    ap: Decimal = Field(..., alias="ask_price", description="Ask price")
    as_: int = Field(..., alias="as", description="Ask size")
    bx: str = Field(..., alias="bid_exchange", description="Bid exchange")
    bp: Decimal = Field(..., alias="bid_price", description="Bid price")
    bs: int = Field(..., alias="bid_size", description="Bid size")
    c: Optional[list[str]] = Field(None, alias="conditions", description="Conditions")
    z: Optional[str] = Field(None, alias="tape", description="Tape")


class Trade(AlpacaBaseModel):
    """Trade data."""

    t: datetime = Field(..., alias="timestamp", description="Trade timestamp")
    x: str = Field(..., alias="exchange", description="Exchange")
    p: Decimal = Field(..., alias="price", description="Price")
    s: int = Field(..., alias="size", description="Size")
    c: Optional[list[str]] = Field(None, alias="conditions", description="Conditions")
    i: int = Field(..., alias="trade_id", description="Trade ID")
    z: Optional[str] = Field(None, alias="tape", description="Tape")


class Snapshot(AlpacaBaseModel):
    """Market snapshot with latest quote, trade, and bars."""

    latest_trade: Optional[Trade] = Field(None, description="Latest trade")
    latest_quote: Optional[Quote] = Field(None, description="Latest quote")
    minute_bar: Optional[Bar] = Field(None, description="Latest minute bar")
    daily_bar: Optional[Bar] = Field(None, description="Current daily bar")
    prev_daily_bar: Optional[Bar] = Field(None, description="Previous daily bar")


class BarsRequest(AlpacaBaseModel):
    """Request parameters for historical bars."""

    symbol: Optional[str] = Field(None, description="Single symbol")
    symbols: Optional[list[str]] = Field(None, description="Multiple symbols")
    timeframe: Timeframe = Field(..., description="Bar timeframe")
    start: datetime = Field(..., description="Start timestamp")
    end: Optional[datetime] = Field(None, description="End timestamp")
    limit: int = Field(1000, ge=1, le=10000, description="Maximum number of bars")
    adjustment: Literal["raw", "split", "dividend", "all"] = Field(
        "raw", description="Price adjustment type"
    )
    feed: DataFeed = Field(DataFeed.IEX, description="Data feed source")
    sort: Literal["asc", "desc"] = Field("asc", description="Sort order")


class TradesRequest(AlpacaBaseModel):
    """Request parameters for historical trades."""

    symbol: Optional[str] = Field(None, description="Single symbol")
    symbols: Optional[list[str]] = Field(None, description="Multiple symbols")
    start: datetime = Field(..., description="Start timestamp")
    end: Optional[datetime] = Field(None, description="End timestamp")
    limit: int = Field(1000, ge=1, le=10000, description="Maximum number of trades")
    feed: DataFeed = Field(DataFeed.IEX, description="Data feed source")
    sort: Literal["asc", "desc"] = Field("asc", description="Sort order")


class QuotesRequest(AlpacaBaseModel):
    """Request parameters for historical quotes."""

    symbol: Optional[str] = Field(None, description="Single symbol")
    symbols: Optional[list[str]] = Field(None, description="Multiple symbols")
    start: datetime = Field(..., description="Start timestamp")
    end: Optional[datetime] = Field(None, description="End timestamp")
    limit: int = Field(1000, ge=1, le=10000, description="Maximum number of quotes")
    feed: DataFeed = Field(DataFeed.IEX, description="Data feed source")
    sort: Literal["asc", "desc"] = Field("asc", description="Sort order")


# ============================================
# BROKER API MODELS
# ============================================


class ActivityType(str, Enum):
    """Account activity types.
    
    These represent different types of transactions and events
    that can occur in an account.
    """

    FILL = "FILL"  # Order fill
    TRANS = "TRANS"  # Cash transaction (deposit/withdrawal)
    MISC = "MISC"  # Miscellaneous
    ACATC = "ACATC"  # ACAT cash deposit
    ACATS = "ACATS"  # ACAT securities deposit
    CSD = "CSD"  # Cash settlement deposit
    CSW = "CSW"  # Cash settlement withdrawal
    DIV = "DIV"  # Dividend
    DIVCGL = "DIVCGL"  # Dividend (capital gains long term)
    DIVCGS = "DIVCGS"  # Dividend (capital gains short term)
    DIVNRA = "DIVNRA"  # Dividend NRA withheld
    DIVROC = "DIVROC"  # Dividend return of capital
    DIVTXEX = "DIVTXEX"  # Dividend tax exempt
    FEE = "FEE"  # Fee
    INT = "INT"  # Interest
    JNLC = "JNLC"  # Journal cash
    JNLS = "JNLS"  # Journal securities
    MA = "MA"  # Merger/Acquisition
    NC = "NC"  # Name change
    OPASN = "OPASN"  # Option assignment
    OPEXP = "OPEXP"  # Option expiration
    OPXRC = "OPXRC"  # Option exercise
    PTC = "PTC"  # Price/trade correction
    PTR = "PTR"  # Paper trade
    REORG = "REORG"  # Reorganization
    SC = "SC"  # Symbol change
    SPIN = "SPIN"  # Spinoff
    SPLIT = "SPLIT"  # Stock split
    SSO = "SSO"  # Stock spinoff
    SSP = "SSP"  # Stock split


class NonTradeActivity(AlpacaBaseModel):
    """Non-trade activity model (NTA).
    
    Represents non-trade activities like dividends, transfers, etc.
    """

    id: str = Field(..., description="Activity ID")
    account_id: str = Field(..., description="Account ID")
    activity_type: ActivityType = Field(..., description="Activity type")
    activity_date: date = Field(..., alias="date", description="Activity date")
    net_amount: Decimal = Field(..., description="Net amount")
    symbol: Optional[str] = Field(None, description="Symbol if applicable")
    qty: Optional[Decimal] = Field(None, description="Quantity if applicable")
    per_share_amount: Optional[Decimal] = Field(
        None, description="Per share amount if applicable"
    )
    description: Optional[str] = Field(None, description="Activity description")
    status: Optional[str] = Field(None, description="Activity status")


class TradeActivity(AlpacaBaseModel):
    """Trade activity model (TA).
    
    Represents trade/fill activities.
    """

    id: str = Field(..., description="Activity ID")
    account_id: str = Field(..., description="Account ID")
    activity_type: Literal["FILL"] = Field("FILL", description="Activity type")
    transaction_time: datetime = Field(..., description="Transaction timestamp")
    fill_type: str = Field(..., alias="type", description="Transaction type (fill, partial_fill)")
    price: Decimal = Field(..., description="Execution price")
    qty: Decimal = Field(..., description="Executed quantity")
    side: OrderSide = Field(..., description="Order side")
    symbol: str = Field(..., description="Symbol")
    leaves_qty: Decimal = Field(..., description="Remaining quantity")
    order_id: str = Field(..., description="Order ID")
    cum_qty: Decimal = Field(..., description="Cumulative quantity filled")
    order_status: Optional[OrderStatus] = Field(None, description="Order status")


class ListActivitiesRequest(AlpacaBaseModel):
    """Request parameters for listing account activities."""

    activity_types: Optional[list[ActivityType]] = Field(
        None, description="Filter by activity types"
    )
    filter_date: Optional[date] = Field(
        None, alias="date", description="Filter by specific date"
    )
    until: Optional[datetime] = Field(None, description="Filter activities before this time")
    after: Optional[datetime] = Field(None, description="Filter activities after this time")
    direction: Optional[Literal["asc", "desc"]] = Field(
        None, description="Sort direction"
    )
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    page_size: Optional[int] = Field(
        None, ge=1, le=100, description="Number of results per page"
    )
    page_token: Optional[str] = Field(None, description="Pagination token")


class PDTStatus(AlpacaBaseModel):
    """Pattern Day Trader status response."""

    is_pattern_day_trader: bool = Field(
        ..., description="Whether account is flagged as PDT"
    )
    day_trade_count: int = Field(
        ..., description="Number of day trades in the rolling 5-day period"
    )
    last_day_trade_date: Optional[datetime] = Field(
        None, description="Date of last day trade"
    )


class CloseAccountResponse(AlpacaBaseModel):
    """Response model for closing an account."""

    id: str = Field(..., description="Account ID")
    status: str = Field(..., description="Account status after closure")


class Contact(AlpacaBaseModel):
    """Contact information for broker account."""

    email_address: str = Field(..., description="Email address")
    phone_number: str = Field(..., description="Phone number")
    street_address: list[str] = Field(..., description="Street address lines")
    unit: Optional[str] = Field(None, description="Unit/apartment number")
    city: str = Field(..., description="City")
    state: Optional[str] = Field(None, description="State/province")
    postal_code: str = Field(..., description="Postal code")
    country: str = Field("USA", description="Country code")


class UpdatableContact(AlpacaBaseModel):
    """Updatable contact information for broker account."""

    email_address: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    street_address: Optional[list[str]] = Field(None, description="Street address lines")
    unit: Optional[str] = Field(None, description="Unit/apartment number")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country code")


class Identity(AlpacaBaseModel):
    """Identity information for broker account."""

    given_name: str = Field(..., min_length=1, description="First name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    family_name: str = Field(..., min_length=1, description="Last name")
    date_of_birth: str = Field(
        ..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date of birth (YYYY-MM-DD)"
    )
    tax_id: Optional[str] = Field(None, description="Tax ID (SSN/ITIN)")
    tax_id_type: Optional[TaxIdType] = Field(None, description="Tax ID type")
    country_of_citizenship: str = Field("USA", description="Country of citizenship")
    country_of_birth: Optional[str] = Field(None, description="Country of birth")
    country_of_tax_residence: str = Field("USA", description="Country of tax residence")
    funding_source: Optional[list[FundingSource]] = Field(
        None, description="Source(s) of funding"
    )
    visa_type: Optional[str] = Field(None, description="Visa type if applicable")
    visa_expiration_date: Optional[str] = Field(
        None, description="Visa expiration date"
    )
    date_of_departure_from_usa: Optional[str] = Field(
        None, description="Date of departure from USA"
    )
    permanent_resident: Optional[bool] = Field(
        None, description="Whether permanent resident"
    )


class UpdatableIdentity(AlpacaBaseModel):
    """Updatable identity information for broker account."""

    given_name: Optional[str] = Field(None, description="First name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    family_name: Optional[str] = Field(None, description="Last name")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD)")
    tax_id: Optional[str] = Field(None, description="Tax ID (SSN/ITIN)")
    tax_id_type: Optional[TaxIdType] = Field(None, description="Tax ID type")
    country_of_citizenship: Optional[str] = Field(None, description="Country of citizenship")
    country_of_birth: Optional[str] = Field(None, description="Country of birth")
    country_of_tax_residence: Optional[str] = Field(None, description="Country of tax residence")
    funding_source: Optional[list[FundingSource]] = Field(
        None, description="Source(s) of funding"
    )
    visa_type: Optional[str] = Field(None, description="Visa type if applicable")
    visa_expiration_date: Optional[str] = Field(
        None, description="Visa expiration date"
    )
    date_of_departure_from_usa: Optional[str] = Field(
        None, description="Date of departure from USA"
    )
    permanent_resident: Optional[bool] = Field(
        None, description="Whether permanent resident"
    )


class Disclosures(AlpacaBaseModel):
    """Disclosures for broker account creation."""

    is_control_person: bool = Field(
        ..., description="Is a control person of a publicly traded company"
    )
    is_affiliated_exchange_or_finra: bool = Field(
        ..., description="Is affiliated with exchange or FINRA"
    )
    is_politically_exposed: bool = Field(..., description="Is politically exposed person")
    immediate_family_exposed: bool = Field(
        ..., description="Has immediate family member who is politically exposed"
    )
    employment_status: Optional[str] = Field(None, description="Employment status")
    employer_name: Optional[str] = Field(None, description="Employer name")
    employer_address: Optional[str] = Field(None, description="Employer address")
    employment_position: Optional[str] = Field(None, description="Employment position")


class UpdatableDisclosures(AlpacaBaseModel):
    """Updatable disclosures for broker account."""

    is_control_person: Optional[bool] = Field(
        None, description="Is a control person of a publicly traded company"
    )
    is_affiliated_exchange_or_finra: Optional[bool] = Field(
        None, description="Is affiliated with exchange or FINRA"
    )
    is_politically_exposed: Optional[bool] = Field(None, description="Is politically exposed person")
    immediate_family_exposed: Optional[bool] = Field(
        None, description="Has immediate family member who is politically exposed"
    )
    employment_status: Optional[str] = Field(None, description="Employment status")
    employer_name: Optional[str] = Field(None, description="Employer name")
    employer_address: Optional[str] = Field(None, description="Employer address")
    employment_position: Optional[str] = Field(None, description="Employment position")


class Agreement(AlpacaBaseModel):
    """Agreement for broker account creation."""

    agreement: Literal[
        "margin_agreement",
        "account_agreement",
        "customer_agreement",
        "crypto_agreement",
    ] = Field(..., description="Agreement type")
    signed_at: datetime = Field(..., description="Signature timestamp")
    ip_address: str = Field(..., description="IP address at signing")
    revision: Optional[str] = Field(None, description="Agreement revision")


class TrustedContact(AlpacaBaseModel):
    """Trusted contact for broker account."""

    given_name: str = Field(..., description="First name")
    family_name: str = Field(..., description="Last name")
    email_address: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    street_address: Optional[list[str]] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")


class UpdatableTrustedContact(AlpacaBaseModel):
    """Updatable trusted contact for broker account."""

    given_name: Optional[str] = Field(None, description="First name")
    family_name: Optional[str] = Field(None, description="Last name")
    email_address: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    street_address: Optional[list[str]] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: Optional[str] = Field(None, description="Country")


class AccountDocument(AlpacaBaseModel):
    """Document for broker account."""

    document_type: DocumentType = Field(..., description="Document type")
    document_sub_type: Optional[str] = Field(None, description="Document sub-type")
    content: str = Field(..., description="Base64 encoded document content")
    mime_type: str = Field(..., description="MIME type of document")


class CreateAccountRequest(AlpacaBaseModel):
    """Request model for creating a broker account."""

    contact: Contact = Field(..., description="Contact information")
    identity: Identity = Field(..., description="Identity information")
    disclosures: Disclosures = Field(..., description="Disclosures")
    agreements: list[Agreement] = Field(..., description="Signed agreements")
    documents: Optional[list[AccountDocument]] = Field(
        None, description="Supporting documents"
    )
    trusted_contact: Optional[TrustedContact] = Field(
        None, description="Trusted contact"
    )
    enabled_assets: Optional[list[AssetClass]] = Field(
        None, description="List of enabled asset classes"
    )
    account_type: Optional[AccountType] = Field(None, description="Account type")
    account_sub_type: Optional[AccountSubType] = Field(None, description="Account sub-type")
    currency: Optional[SupportedCurrencies] = Field(None, description="Account currency")


class UpdateAccountRequest(AlpacaBaseModel):
    """Request model for updating a broker account."""

    contact: Optional[UpdatableContact] = Field(None, description="Contact information")
    identity: Optional[UpdatableIdentity] = Field(None, description="Identity information")
    disclosures: Optional[UpdatableDisclosures] = Field(None, description="Disclosures")
    trusted_contact: Optional[UpdatableTrustedContact] = Field(
        None, description="Trusted contact"
    )


class BrokerAccount(AlpacaBaseModel):
    """Response model for broker account."""

    id: str = Field(..., description="Account ID")
    account_number: str = Field(..., description="Account number")
    status: AccountStatus = Field(..., description="Account status")
    crypto_status: Optional[AccountStatus] = Field(
        None, description="Crypto trading status"
    )
    currency: str = Field(..., description="Account currency")
    last_equity: Decimal = Field(..., description="Last equity value")
    created_at: datetime = Field(..., description="Creation timestamp")
    contact: Optional[Contact] = Field(None, description="Contact information")
    identity: Optional[Identity] = Field(None, description="Identity information")
    disclosures: Optional[Disclosures] = Field(None, description="Disclosures")
    agreements: Optional[list[Agreement]] = Field(None, description="Agreements")
    trusted_contact: Optional[TrustedContact] = Field(None, description="Trusted contact")
    account_type: Optional[AccountType] = Field(None, description="Account type")
    trading_configurations: Optional[dict[str, Any]] = Field(
        None, description="Trading configurations"
    )


class Transfer(AlpacaBaseModel):
    """Response model for a fund transfer."""

    id: str = Field(..., description="Transfer ID")
    relationship_id: Optional[str] = Field(None, description="ACH relationship ID")
    account_id: str = Field(..., description="Account ID")
    type: TransferType = Field(..., description="Transfer type")
    status: TransferStatus = Field(..., description="Transfer status")
    amount: Decimal = Field(..., description="Transfer amount")
    direction: TransferDirection = Field(..., description="Transfer direction")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    reason: Optional[str] = Field(None, description="Status reason")
    requested_amount: Optional[Decimal] = Field(None, description="Requested amount")
    fee: Optional[Decimal] = Field(None, description="Transfer fee")
    fee_payment_method: Optional[FeePaymentMethod] = Field(None, description="Fee payment method")


class TransferRequest(AlpacaBaseModel):
    """Request model for creating an ACH transfer."""

    transfer_type: TransferType = Field(..., description="Transfer type")
    relationship_id: str = Field(..., description="ACH relationship ID")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    direction: TransferDirection = Field(..., description="Transfer direction")
    timing: Optional[TransferTiming] = Field(None, description="Transfer timing")
    fee_payment_method: Optional[FeePaymentMethod] = Field(
        None, description="Fee payment method"
    )


class GetTransfersRequest(AlpacaBaseModel):
    """Request parameters for listing transfers."""

    direction: Optional[TransferDirection] = Field(None, description="Filter by direction")
    limit: Optional[int] = Field(None, ge=1, description="Maximum number of transfers")
    offset: Optional[int] = Field(None, ge=0, description="Number of transfers to skip")


class ACHRelationship(AlpacaBaseModel):
    """Response model for ACH relationship."""

    id: str = Field(..., description="Relationship ID")
    account_id: str = Field(..., description="Account ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    status: str = Field(..., description="Relationship status")
    account_owner_name: str = Field(..., description="Bank account owner name")
    bank_account_type: BankAccountType = Field(..., description="Bank account type")
    bank_account_number: str = Field(..., description="Bank account number (masked)")
    bank_routing_number: str = Field(..., description="Bank routing number")
    nickname: Optional[str] = Field(None, description="Relationship nickname")


class ACHRelationshipRequest(AlpacaBaseModel):
    """Request model for creating ACH relationship."""

    account_owner_name: str = Field(..., min_length=1, description="Account owner name")
    bank_account_type: BankAccountType = Field(..., description="Bank account type")
    bank_account_number: str = Field(..., min_length=4, description="Bank account number")
    bank_routing_number: str = Field(
        ..., min_length=9, max_length=9, description="Bank routing number"
    )
    nickname: Optional[str] = Field(None, description="Relationship nickname")


class CreatePlaidRelationshipRequest(AlpacaBaseModel):
    """Request model for creating a Plaid-based ACH relationship."""

    processor_token: str = Field(..., description="Plaid processor token")


class CreateBankRequest(AlpacaBaseModel):
    """Request model for creating a bank for wire transfers."""

    name: str = Field(..., description="Bank name")
    bank_code_type: BankCodeType = Field(..., description="Bank code type")
    bank_code: str = Field(..., description="Bank code (ABA routing or BIC/SWIFT)")
    account_number: str = Field(..., description="Bank account number")
    country: Optional[str] = Field(None, description="Country code")
    state_province: Optional[str] = Field(None, description="State/province")
    postal_code: Optional[str] = Field(None, description="Postal code")
    city: Optional[str] = Field(None, description="City")
    street_address: Optional[str] = Field(None, description="Street address")


class CreateBankTransferRequest(AlpacaBaseModel):
    """Request model for creating a bank (wire) transfer."""

    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    direction: TransferDirection = Field(..., description="Transfer direction")
    timing: Optional[TransferTiming] = Field(None, description="Transfer timing")
    fee_payment_method: Optional[FeePaymentMethod] = Field(
        None, description="Fee payment method"
    )
    bank_id: str = Field(..., description="Bank ID")
    transfer_type: TransferType = Field(TransferType.WIRE, description="Transfer type")
    additional_information: Optional[str] = Field(
        None, description="Additional wire transfer information"
    )


class Journal(AlpacaBaseModel):
    """Response model for journal entry."""

    id: str = Field(..., description="Journal ID")
    to_account: str = Field(..., description="Destination account ID")
    from_account: str = Field(..., description="Source account ID")
    entry_type: JournalEntryType = Field(..., description="Journal entry type")
    status: JournalStatus = Field(..., description="Journal status")
    symbol: Optional[str] = Field(None, description="Symbol for security journals")
    qty: Optional[Decimal] = Field(None, description="Quantity for security journals")
    price: Optional[Decimal] = Field(None, description="Price for security journals")
    net_amount: Decimal = Field(..., description="Net amount")
    description: Optional[str] = Field(None, description="Journal description")
    settle_date: Optional[date] = Field(None, description="Settlement date")
    system_date: Optional[date] = Field(None, description="System date")
    transmitter_name: Optional[str] = Field(None, description="Transmitter name")
    transmitter_account_number: Optional[str] = Field(
        None, description="Transmitter account number"
    )
    transmitter_address: Optional[str] = Field(None, description="Transmitter address")
    transmitter_financial_institution: Optional[str] = Field(
        None, description="Transmitter financial institution"
    )
    transmitter_timestamp: Optional[datetime] = Field(
        None, description="Transmitter timestamp"
    )


class JournalRequest(AlpacaBaseModel):
    """Request model for creating a journal entry."""

    to_account: str = Field(..., description="Destination account ID")
    from_account: str = Field(..., description="Source account ID")
    entry_type: JournalEntryType = Field(..., description="Journal entry type")
    amount: Optional[Decimal] = Field(
        None, gt=0, description="Amount for cash journals"
    )
    symbol: Optional[str] = Field(None, description="Symbol for security journals")
    qty: Optional[Decimal] = Field(
        None, gt=0, description="Quantity for security journals"
    )
    description: Optional[str] = Field(
        None, max_length=1024, description="Journal description"
    )
    transmitter_name: Optional[str] = Field(None, description="Transmitter name")
    transmitter_account_number: Optional[str] = Field(
        None, description="Transmitter account number"
    )
    transmitter_address: Optional[str] = Field(None, description="Transmitter address")
    transmitter_financial_institution: Optional[str] = Field(
        None, description="Transmitter financial institution"
    )
    transmitter_timestamp: Optional[str] = Field(
        None, description="Transmitter timestamp"
    )
    currency: Optional[SupportedCurrencies] = Field(None, description="Currency")


class BatchJournalEntry(AlpacaBaseModel):
    """Entry for batch journal operations."""

    to_account: str = Field(..., description="Destination account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: Optional[str] = Field(None, description="Entry description")


class ReverseBatchJournalEntry(AlpacaBaseModel):
    """Entry for reverse batch journal operations."""

    from_account: str = Field(..., description="Source account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: Optional[str] = Field(None, description="Entry description")


class CreateBatchJournalRequest(AlpacaBaseModel):
    """Request model for creating a batch journal."""

    entry_type: JournalEntryType = Field(..., description="Journal entry type")
    from_account: str = Field(..., description="Source account ID")
    entries: list[BatchJournalEntry] = Field(..., description="Batch entries")


class CreateReverseBatchJournalRequest(AlpacaBaseModel):
    """Request model for creating a reverse batch journal."""

    entry_type: JournalEntryType = Field(..., description="Journal entry type")
    to_account: str = Field(..., description="Destination account ID")
    entries: list[ReverseBatchJournalEntry] = Field(..., description="Batch entries")


class GetJournalsRequest(AlpacaBaseModel):
    """Request parameters for listing journals."""

    after: Optional[date] = Field(None, description="Filter journals after this date")
    before: Optional[date] = Field(None, description="Filter journals before this date")
    status: Optional[JournalStatus] = Field(None, description="Filter by status")
    entry_type: Optional[JournalEntryType] = Field(None, description="Filter by entry type")
    to_account: Optional[str] = Field(None, description="Filter by destination account")
    from_account: Optional[str] = Field(None, description="Filter by source account")


class GetTradeDocumentsRequest(AlpacaBaseModel):
    """Request parameters for listing trade documents."""

    start: Optional[date] = Field(None, description="Start date")
    end: Optional[date] = Field(None, description="End date")
    type: Optional[str] = Field(None, description="Document type filter")


class Document(AlpacaBaseModel):
    """Response model for account document metadata."""

    id: str = Field(..., description="Document ID")
    name: Optional[str] = Field(None, description="Document name")
    type: str = Field(..., description="Document type")
    sub_type: Optional[str] = Field(None, description="Document sub-type")
    document_date: Optional[date] = Field(None, alias="date", description="Document date")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")


class ListDocumentsRequest(AlpacaBaseModel):
    """Request parameters for listing account documents."""

    start: Optional[date] = Field(None, description="Start date filter")
    end: Optional[date] = Field(None, description="End date filter")
    type: Optional[str] = Field(None, description="Document type filter")


class UploadDocumentRequest(AlpacaBaseModel):
    """Request model for uploading a document."""

    document_type: DocumentType = Field(..., description="Document type")
    document_sub_type: Optional[str] = Field(None, description="Document sub-type")
    content: str = Field(..., description="Base64 encoded document content")
    mime_type: str = Field(..., description="MIME type of document")


# ============================================
# TRADING REQUEST MODELS
# ============================================


class CreateWatchlistRequest(AlpacaBaseModel):
    """Request model for creating a watchlist."""

    name: str = Field(..., description="Watchlist name")
    symbols: list[str] = Field(..., description="Symbols to watch")


class UpdateWatchlistRequest(AlpacaBaseModel):
    """Request model for updating a watchlist."""

    name: Optional[str] = Field(None, description="New watchlist name")
    symbols: Optional[list[str]] = Field(None, description="New symbols list")


class GetPortfolioHistoryRequest(AlpacaBaseModel):
    """Request parameters for portfolio history."""

    period: Optional[str] = Field(
        None, description="Duration (e.g., 1D, 1W, 1M, 1A)"
    )
    timeframe: Optional[str] = Field(
        None, description="Resolution (1Min, 5Min, 15Min, 1H, 1D)"
    )
    intraday_reporting: Optional[str] = Field(
        None, description="Intraday reporting timestamps"
    )
    start: Optional[datetime] = Field(None, description="Start timestamp")
    pnl_reset: Optional[str] = Field(None, description="PnL reset baseline")
    end: Optional[datetime] = Field(None, description="End timestamp")
    date_end: Optional[date] = Field(None, description="End date")
    extended_hours: Optional[bool] = Field(None, description="Include extended hours")
    cashflow_types: Optional[str] = Field(
        None, description="Cashflow activities to include"
    )


class GetCalendarRequest(AlpacaBaseModel):
    """Request parameters for market calendar."""

    start: Optional[date] = Field(None, description="Start date")
    end: Optional[date] = Field(None, description="End date")


class GetCorporateAnnouncementsRequest(AlpacaBaseModel):
    """Request parameters for corporate announcements."""

    ca_types: list[CorporateActionType] = Field(
        ..., description="Corporate action types"
    )
    since: date = Field(..., description="Start date (inclusive)")
    until: date = Field(..., description="End date (inclusive)")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    cusip: Optional[str] = Field(None, description="Filter by CUSIP")
    date_type: Optional[CorporateActionDateType] = Field(
        None, description="Date type for filtering"
    )


class GetOptionContractsRequest(AlpacaBaseModel):
    """Request parameters for option contracts."""

    underlying_symbols: Optional[list[str]] = Field(
        None, description="Underlying symbols"
    )
    status: Optional[AssetStatus] = Field(
        AssetStatus.ACTIVE, description="Contract status"
    )
    expiration_date: Optional[date] = Field(None, description="Exact expiration date")
    expiration_date_gte: Optional[date] = Field(
        None, description="Expiration date >= this"
    )
    expiration_date_lte: Optional[date] = Field(
        None, description="Expiration date <= this"
    )
    root_symbol: Optional[str] = Field(None, description="Option root symbol")
    type: Optional[ContractType] = Field(None, description="Contract type (call/put)")
    style: Optional[ExerciseStyle] = Field(
        None, description="Exercise style (american/european)"
    )
    strike_price_gte: Optional[str] = Field(None, description="Strike price >= this")
    strike_price_lte: Optional[str] = Field(None, description="Strike price <= this")
    limit: Optional[int] = Field(None, ge=1, le=10000, description="Results limit")
    page_token: Optional[str] = Field(None, description="Pagination token")


# ============================================
# LIST REQUEST MODELS
# ============================================


class ListOrdersRequest(AlpacaBaseModel):
    """Request parameters for listing orders."""

    status: QueryOrderStatus = Field(
        QueryOrderStatus.OPEN, description="Order status filter"
    )
    limit: int = Field(50, ge=1, le=500, description="Maximum number of orders")
    after: Optional[datetime] = Field(None, description="Filter orders after this timestamp")
    until: Optional[datetime] = Field(None, description="Filter orders until this timestamp")
    direction: Sort = Field(Sort.DESC, description="Sort direction")
    nested: bool = Field(True, description="Include nested orders")
    symbols: Optional[list[str]] = Field(None, description="Filter by symbols")
    side: Optional[OrderSide] = Field(None, description="Filter by side")


class ListAccountsRequest(AlpacaBaseModel):
    """Request parameters for listing broker accounts."""

    query: Optional[str] = Field(None, description="Search query")
    created_after: Optional[date] = Field(
        None, description="Filter accounts created after"
    )
    created_before: Optional[date] = Field(
        None, description="Filter accounts created before"
    )
    status: Optional[AccountStatus] = Field(None, description="Filter by status")
    sort: Sort = Field(Sort.DESC, description="Sort direction")
    entities: Optional[list[AccountEntities]] = Field(
        None, description="Related entities to include"
    )


class ListPositionsRequest(AlpacaBaseModel):
    """Request parameters for listing positions."""

    # Currently no specific parameters, but included for consistency
    pass


class ListAssetsRequest(AlpacaBaseModel):
    """Request parameters for listing assets."""

    status: Optional[AssetStatus] = Field(None, description="Filter by status")
    asset_class: Optional[AssetClass] = Field(None, description="Filter by asset class")
    exchange: Optional[str] = Field(None, description="Filter by exchange")
    attributes: Optional[str] = Field(None, description="Filter by attributes")


# Backward compatibility alias
OrderUpdate = ReplaceOrderRequest