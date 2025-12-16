"""AlpacaFarmer - A minimal Python wrapper for Alpaca Markets API."""

__version__ = "0.1.0"

# Auth
from alpacafarmer.auth import AlpacaAuth, Environment

# Clients
from alpacafarmer.client import BrokerClient, MarketDataClient, TraderClient

# Exceptions
from alpacafarmer.exceptions import (
    AlpacaError,
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

# Models - Enums
from alpacafarmer.models import (
    AccountStatus,
    ActivityType,
    AssetClass,
    AssetStatus,
    BankAccountType,
    DataFeed,
    FundingSource,
    JournalEntryType,
    JournalStatus,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    TaxIdType,
    Timeframe,
    TimeInForce,
    TransferDirection,
    TransferStatus,
    TransferType,
)

# Models - Account
from alpacafarmer.models import Account, AccountConfiguration

# Models - Orders
from alpacafarmer.models import ListOrdersRequest, Order, OrderRequest, OrderUpdate

# Models - Positions
from alpacafarmer.models import ListPositionsRequest, Position

# Models - Assets
from alpacafarmer.models import Asset, ListAssetsRequest

# Models - Market Data
from alpacafarmer.models import (
    Bar,
    BarsRequest,
    Quote,
    QuotesRequest,
    Snapshot,
    Trade,
    TradesRequest,
)

# Models - Broker
from alpacafarmer.models import (
    ACHRelationship,
    ACHRelationshipRequest,
    Agreement,
    BrokerAccount,
    CloseAccountResponse,
    Contact,
    CreateAccountRequest,
    Disclosures,
    Identity,
    Journal,
    JournalRequest,
    ListAccountsRequest,
    ListActivitiesRequest,
    NonTradeActivity,
    PDTStatus,
    TradeActivity,
    Transfer,
    TransferRequest,
    TrustedContact,
    UpdatableContact,
    UpdatableDisclosures,
    UpdatableIdentity,
    UpdatableTrustedContact,
    UpdateAccountRequest,
)

__all__ = [
    # Version
    "__version__",
    # Auth
    "AlpacaAuth",
    "Environment",
    # Clients
    "TraderClient",
    "BrokerClient",
    "MarketDataClient",
    # Exceptions
    "AlpacaError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    # Enums
    "ActivityType",
    "OrderSide",
    "OrderType",
    "TimeInForce",
    "OrderStatus",
    "AssetClass",
    "AssetStatus",
    "PositionSide",
    "AccountStatus",
    "Timeframe",
    "DataFeed",
    "TransferDirection",
    "TransferType",
    "TransferStatus",
    "BankAccountType",
    "JournalEntryType",
    "JournalStatus",
    "FundingSource",
    "TaxIdType",
    # Account Models
    "Account",
    "AccountConfiguration",
    # Order Models
    "OrderRequest",
    "Order",
    "OrderUpdate",
    "ListOrdersRequest",
    # Position Models
    "Position",
    "ListPositionsRequest",
    # Asset Models
    "Asset",
    "ListAssetsRequest",
    # Market Data Models
    "BarsRequest",
    "Bar",
    "QuotesRequest",
    "Quote",
    "TradesRequest",
    "Trade",
    "Snapshot",
    # Broker Models
    "Contact",
    "Identity",
    "Disclosures",
    "Agreement",
    "TrustedContact",
    "UpdatableContact",
    "UpdatableIdentity",
    "UpdatableDisclosures",
    "UpdatableTrustedContact",
    "CreateAccountRequest",
    "UpdateAccountRequest",
    "BrokerAccount",
    "ListAccountsRequest",
    "Transfer",
    "TransferRequest",
    "ACHRelationship",
    "ACHRelationshipRequest",
    "Journal",
    "JournalRequest",
    # Activity Models
    "TradeActivity",
    "NonTradeActivity",
    "ListActivitiesRequest",
    "PDTStatus",
    "CloseAccountResponse",
]