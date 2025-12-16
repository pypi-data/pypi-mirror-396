"""API client classes for Alpaca Markets APIs.

This module provides three main client classes:
- TraderClient: For individual traders using the Trading API
- BrokerClient: For broker dealers managing customer accounts
- MarketDataClient: For accessing real-time and historical market data
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from alpacafarmer.auth import AlpacaAuth
from alpacafarmer.http import BaseHTTPClient
from alpacafarmer.models import (
    # Account models
    Account,
    # Activity models
    ActivityType,
    CloseAccountResponse,
    ListActivitiesRequest,
    NonTradeActivity,
    PDTStatus,
    TradeActivity,
    # Asset models
    Asset,
    ListAssetsRequest,
    # Broker models
    ACHRelationship,
    ACHRelationshipRequest,
    BrokerAccount,
    CreateAccountRequest,
    Document,
    Journal,
    JournalRequest,
    ListAccountsRequest,
    ListDocumentsRequest,
    Transfer,
    TransferRequest,
    UpdateAccountRequest,
    # Market data models
    Bar,
    BarsRequest,
    DataFeed,
    Quote,
    QuotesRequest,
    Snapshot,
    Trade,
    TradesRequest,
    # Order models
    ListOrdersRequest,
    Order,
    OrderRequest,
    OrderUpdate,
    # Position models
    Position,
)


class TraderClient(BaseHTTPClient):
    """Client for Alpaca Trading API (individual traders).
    
    This client provides methods for:
    - Account information retrieval
    - Order management (create, list, cancel, replace)
    - Position management (list, close)
    - Asset information retrieval
    
    Examples:
        >>> auth = AlpacaAuth(api_key="key", secret_key="secret")
        >>> async with TraderClient(auth) as client:
        ...     account = await client.get_account()
        ...     print(account.buying_power)
    """

    def __init__(self, auth: AlpacaAuth) -> None:
        """Initialize the TraderClient.
        
        Args:
            auth: AlpacaAuth instance for authentication.
        """
        base_url = auth.get_base_url("trading")
        super().__init__(auth=auth, base_url=base_url)

    # ========================================
    # Account Methods
    # ========================================

    async def get_account(self) -> Account:
        """Get the trading account information.
        
        Returns:
            Account object with current account details.
        """
        response = await self._get("/v2/account")
        return Account.model_validate(response)

    # ========================================
    # Order Methods
    # ========================================

    async def create_order(self, request: OrderRequest) -> Order:
        """Create a new order.
        
        Args:
            request: OrderRequest with order parameters.
            
        Returns:
            Created Order object.
        """
        response = await self._post(
            "/v2/orders",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return Order.model_validate(response)

    async def get_order(self, order_id: str) -> Order:
        """Get an order by its ID.
        
        Args:
            order_id: The order ID.
            
        Returns:
            Order object.
        """
        response = await self._get(f"/v2/orders/{order_id}")
        return Order.model_validate(response)

    async def get_order_by_client_id(self, client_order_id: str) -> Order:
        """Get an order by client order ID.
        
        Args:
            client_order_id: The client-specified order ID.
            
        Returns:
            Order object.
        """
        response = await self._get(
            "/v2/orders:by_client_order_id",
            params={"client_order_id": client_order_id},
        )
        return Order.model_validate(response)

    async def list_orders(
        self, request: Optional[ListOrdersRequest] = None
    ) -> list[Order]:
        """List orders with optional filtering.
        
        Args:
            request: Optional ListOrdersRequest with filter parameters.
            
        Returns:
            List of Order objects.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
            # Convert symbols list to comma-separated string
            if "symbols" in params and params["symbols"]:
                params["symbols"] = ",".join(params["symbols"])
        
        response = await self._get("/v2/orders", params=params if params else None)
        return [Order.model_validate(order) for order in response]

    async def cancel_order(self, order_id: str) -> None:
        """Cancel an order by its ID.
        
        Args:
            order_id: The order ID to cancel.
        """
        await self._delete(f"/v2/orders/{order_id}")

    async def cancel_all_orders(self) -> list[Order]:
        """Cancel all open orders.
        
        Returns:
            List of canceled Order objects.
        """
        response = await self._delete("/v2/orders")
        if isinstance(response, list):
            return [Order.model_validate(order) for order in response]
        return []

    async def replace_order(self, order_id: str, request: OrderUpdate) -> Order:
        """Replace (modify) an existing order.
        
        Args:
            order_id: The order ID to replace.
            request: OrderUpdate with new order parameters.
            
        Returns:
            New Order object that replaced the original.
        """
        response = await self._patch(
            f"/v2/orders/{order_id}",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return Order.model_validate(response)

    # ========================================
    # Position Methods
    # ========================================

    async def list_positions(self) -> list[Position]:
        """List all open positions.
        
        Returns:
            List of Position objects.
        """
        response = await self._get("/v2/positions")
        return [Position.model_validate(pos) for pos in response]

    async def get_position(self, symbol: str) -> Position:
        """Get an open position by symbol.
        
        Args:
            symbol: The asset symbol.
            
        Returns:
            Position object.
        """
        response = await self._get(f"/v2/positions/{symbol}")
        return Position.model_validate(response)

    async def close_position(
        self,
        symbol: str,
        qty: Optional[Decimal] = None,
        percentage: Optional[Decimal] = None,
    ) -> Order:
        """Close a position (full or partial).
        
        Args:
            symbol: The asset symbol.
            qty: Optional quantity to close. If not provided, closes full position.
            percentage: Optional percentage of position to close (0-100).
            
        Returns:
            Order object for the closing order.
        """
        params: dict[str, Any] = {}
        if qty is not None:
            params["qty"] = str(qty)
        if percentage is not None:
            params["percentage"] = str(percentage)
        
        response = await self._delete(
            f"/v2/positions/{symbol}",
            params=params if params else None,
        )
        return Order.model_validate(response)

    async def close_all_positions(self, cancel_orders: bool = False) -> list[Order]:
        """Close all open positions.
        
        Args:
            cancel_orders: Whether to cancel open orders before closing positions.
            
        Returns:
            List of Order objects for closing orders.
        """
        params = {"cancel_orders": str(cancel_orders).lower()}
        response = await self._delete("/v2/positions", params=params)
        if isinstance(response, list):
            return [Order.model_validate(order) for order in response]
        return []

    # ========================================
    # Asset Methods
    # ========================================

    async def list_assets(
        self, request: Optional[ListAssetsRequest] = None
    ) -> list[Asset]:
        """List available assets.
        
        Args:
            request: Optional ListAssetsRequest with filter parameters.
            
        Returns:
            List of Asset objects.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
        
        response = await self._get("/v2/assets", params=params if params else None)
        return [Asset.model_validate(asset) for asset in response]

    async def get_asset(self, symbol_or_id: str) -> Asset:
        """Get asset information by symbol or asset ID.
        
        Args:
            symbol_or_id: The asset symbol or asset ID.
            
        Returns:
            Asset object.
        """
        response = await self._get(f"/v2/assets/{symbol_or_id}")
        return Asset.model_validate(response)


class BrokerClient(BaseHTTPClient):
    """Client for Alpaca Broker API (broker dealers).
    
    This client provides methods for:
    - Account management (create, list, update, delete)
    - Trading on behalf of accounts
    - Funding operations (ACH relationships, transfers)
    - Journal entries between accounts
    
    Examples:
        >>> auth = AlpacaAuth(api_key="key", secret_key="secret")
        >>> async with BrokerClient(auth) as client:
        ...     accounts = await client.list_accounts()
        ...     print(len(accounts))
    """

    def __init__(self, auth: AlpacaAuth) -> None:
        """Initialize the BrokerClient.
        
        Args:
            auth: AlpacaAuth instance for authentication.
        """
        base_url = auth.get_base_url("broker")
        super().__init__(auth=auth, base_url=base_url)

    # ========================================
    # Account Methods
    # ========================================

    async def create_account(self, request: CreateAccountRequest) -> BrokerAccount:
        """Create a new brokerage account.
        
        Args:
            request: CreateAccountRequest with account details.
            
        Returns:
            Created BrokerAccount object.
        """
        response = await self._post(
            "/v1/accounts",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return BrokerAccount.model_validate(response)

    async def get_account(self, account_id: str) -> BrokerAccount:
        """Get a brokerage account by ID.
        
        Args:
            account_id: The account ID.
            
        Returns:
            BrokerAccount object.
        """
        response = await self._get(f"/v1/accounts/{account_id}")
        return BrokerAccount.model_validate(response)

    async def list_accounts(
        self, request: Optional[ListAccountsRequest] = None
    ) -> list[BrokerAccount]:
        """List brokerage accounts with optional filtering.
        
        Args:
            request: Optional ListAccountsRequest with filter parameters.
            
        Returns:
            List of BrokerAccount objects.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
        
        response = await self._get("/v1/accounts", params=params if params else None)
        return [BrokerAccount.model_validate(account) for account in response]

    async def update_account(
        self, account_id: str, request: UpdateAccountRequest
    ) -> BrokerAccount:
        """Update an existing brokerage account.
        
        Args:
            account_id: The account ID to update.
            request: UpdateAccountRequest with updated account details.
            
        Returns:
            Updated BrokerAccount object.
        """
        response = await self._patch(
            f"/v1/accounts/{account_id}",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return BrokerAccount.model_validate(response)

    async def delete_account(self, account_id: str) -> None:
        """Delete (close) a brokerage account.
        
        Args:
            account_id: The account ID to delete.
        """
        await self._delete(f"/v1/accounts/{account_id}")

    # ========================================
    # Trading Methods (on behalf of accounts)
    # ========================================

    async def create_order(self, account_id: str, request: OrderRequest) -> Order:
        """Create an order on behalf of an account.
        
        Args:
            account_id: The account ID to place the order for.
            request: OrderRequest with order parameters.
            
        Returns:
            Created Order object.
        """
        response = await self._post(
            f"/v1/trading/accounts/{account_id}/orders",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return Order.model_validate(response)

    async def get_orders(self, account_id: str) -> list[Order]:
        """Get orders for an account.
        
        Args:
            account_id: The account ID.
            
        Returns:
            List of Order objects.
        """
        response = await self._get(f"/v1/trading/accounts/{account_id}/orders")
        return [Order.model_validate(order) for order in response]

    async def cancel_order(self, account_id: str, order_id: str) -> None:
        """Cancel an order for an account.
        
        Args:
            account_id: The account ID.
            order_id: The order ID to cancel.
        """
        await self._delete(f"/v1/trading/accounts/{account_id}/orders/{order_id}")

    # ========================================
    # Funding Methods
    # ========================================

    async def create_ach_relationship(
        self, account_id: str, request: ACHRelationshipRequest
    ) -> ACHRelationship:
        """Create an ACH relationship for an account.
        
        Args:
            account_id: The account ID.
            request: ACHRelationshipRequest with bank account details.
            
        Returns:
            Created ACHRelationship object.
        """
        response = await self._post(
            f"/v1/accounts/{account_id}/ach_relationships",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return ACHRelationship.model_validate(response)

    async def get_ach_relationships(self, account_id: str) -> list[ACHRelationship]:
        """Get ACH relationships for an account.
        
        Args:
            account_id: The account ID.
            
        Returns:
            List of ACHRelationship objects.
        """
        response = await self._get(f"/v1/accounts/{account_id}/ach_relationships")
        return [ACHRelationship.model_validate(rel) for rel in response]

    async def delete_ach_relationship(
        self, account_id: str, relationship_id: str
    ) -> None:
        """Delete an ACH relationship.
        
        Args:
            account_id: The account ID.
            relationship_id: The ACH relationship ID to delete.
        """
        await self._delete(
            f"/v1/accounts/{account_id}/ach_relationships/{relationship_id}"
        )

    async def create_transfer(
        self, account_id: str, request: TransferRequest
    ) -> Transfer:
        """Create a fund transfer for an account.
        
        Args:
            account_id: The account ID.
            request: TransferRequest with transfer details.
            
        Returns:
            Created Transfer object.
        """
        response = await self._post(
            f"/v1/accounts/{account_id}/transfers",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return Transfer.model_validate(response)

    async def get_transfers(self, account_id: str) -> list[Transfer]:
        """Get transfers for an account.
        
        Args:
            account_id: The account ID.
            
        Returns:
            List of Transfer objects.
        """
        response = await self._get(f"/v1/accounts/{account_id}/transfers")
        return [Transfer.model_validate(transfer) for transfer in response]

    # ========================================
    # Journal Methods
    # ========================================

    async def create_journal(self, request: JournalRequest) -> Journal:
        """Create a journal entry between accounts.
        
        Args:
            request: JournalRequest with journal details.
            
        Returns:
            Created Journal object.
        """
        response = await self._post(
            "/v1/journals",
            json=request.model_dump(mode="json", exclude_none=True, by_alias=True),
        )
        return Journal.model_validate(response)

    async def get_journals(self) -> list[Journal]:
        """Get all journal entries.
        
        Returns:
            List of Journal objects.
        """
        response = await self._get("/v1/journals")
        return [Journal.model_validate(journal) for journal in response]

    # ========================================
    # Document Methods
    # ========================================

    async def list_documents(
        self,
        account_id: str,
        request: Optional[ListDocumentsRequest] = None,
    ) -> list[Document]:
        """List documents for an account.
        
        Retrieves a list of documents (statements, confirmations, etc.)
        available for a specific account.
        
        Args:
            account_id: The account ID.
            request: Optional ListDocumentsRequest with filter parameters.
            
        Returns:
            List of Document objects with metadata.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
        
        response = await self._get(
            f"/v1/accounts/{account_id}/documents",
            params=params if params else None,
        )
        return [Document.model_validate(doc) for doc in response]

    async def get_document(self, account_id: str, document_id: str) -> Document:
        """Get a specific document's metadata.
        
        Args:
            account_id: The account ID.
            document_id: The document ID.
            
        Returns:
            Document object with metadata.
        """
        response = await self._get(
            f"/v1/accounts/{account_id}/documents/{document_id}"
        )
        return Document.model_validate(response)

    async def download_document(self, account_id: str, document_id: str) -> bytes:
        """Download a document's content.
        
        Retrieves the actual content of a document (PDF, etc.).
        
        Args:
            account_id: The account ID.
            document_id: The document ID.
            
        Returns:
            Raw document content as bytes.
        """
        return await self._get_bytes(
            f"/v1/accounts/{account_id}/documents/{document_id}/download"
        )

    # ========================================
    # Account Activities Methods
    # ========================================

    async def list_account_activities(
        self,
        request: Optional[ListActivitiesRequest] = None,
    ) -> list[TradeActivity | NonTradeActivity]:
        """List account activities across all accounts.
        
        Retrieves a list of activities for all accounts managed by the broker.
        Activities include trades, dividends, transfers, and other account events.
        
        Args:
            request: Optional ListActivitiesRequest with filter parameters.
            
        Returns:
            List of TradeActivity or NonTradeActivity objects.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
            # Convert activity_types list to comma-separated string
            if "activity_types" in params and params["activity_types"]:
                params["activity_types"] = ",".join(params["activity_types"])
        
        response = await self._get(
            "/v1/accounts/activities",
            params=params if params else None,
        )
        
        # Parse activities based on activity_type
        activities: list[TradeActivity | NonTradeActivity] = []
        for activity in response:
            if activity.get("activity_type") == "FILL":
                activities.append(TradeActivity.model_validate(activity))
            else:
                activities.append(NonTradeActivity.model_validate(activity))
        return activities

    async def list_account_activities_by_type(
        self,
        activity_type: ActivityType,
        request: Optional[ListActivitiesRequest] = None,
    ) -> list[TradeActivity | NonTradeActivity]:
        """List account activities of a specific type.
        
        Retrieves activities filtered by a specific activity type.
        
        Args:
            activity_type: The type of activity to filter by.
            request: Optional ListActivitiesRequest with additional filter parameters.
            
        Returns:
            List of TradeActivity or NonTradeActivity objects.
        """
        params: dict[str, Any] = {}
        if request:
            params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
            # Remove activity_types as we're filtering by URL path
            params.pop("activity_types", None)
        
        response = await self._get(
            f"/v1/accounts/activities/{activity_type.value}",
            params=params if params else None,
        )
        
        # Parse activities based on activity_type
        activities: list[TradeActivity | NonTradeActivity] = []
        for activity in response:
            if activity.get("activity_type") == "FILL":
                activities.append(TradeActivity.model_validate(activity))
            else:
                activities.append(NonTradeActivity.model_validate(activity))
        return activities

    # ========================================
    # PDT Status Methods
    # ========================================

    async def get_pdt_status(self, account_id: str) -> PDTStatus:
        """Get Pattern Day Trader status for an account.
        
        Retrieves the PDT status, including whether the account is flagged
        as a pattern day trader and the current day trade count.
        
        Args:
            account_id: The account ID to check PDT status for.
            
        Returns:
            PDTStatus object with PDT information.
        """
        response = await self._get(
            f"/v1/trading/accounts/{account_id}/account/pdt/status"
        )
        return PDTStatus.model_validate(response)

    # ========================================
    # Account Actions Methods
    # ========================================

    async def close_account(self, account_id: str) -> CloseAccountResponse:
        """Close (terminate) a brokerage account.
        
        Before closing an account, you must:
        1. Close all open positions
        2. Withdraw all funds from the account
        
        This is different from delete_account which removes the account.
        This endpoint initiates the account closure process.
        
        Args:
            account_id: The account ID to close.
            
        Returns:
            CloseAccountResponse with the closure status.
        """
        response = await self._post(
            f"/v1/accounts/{account_id}/actions/close"
        )
        return CloseAccountResponse.model_validate(response)


class MarketDataClient(BaseHTTPClient):
    """Client for Alpaca Market Data API.
    
    This client provides methods for:
    - Historical and latest bars (OHLCV data)
    - Historical and latest quotes (bid/ask data)
    - Historical and latest trades
    - Market snapshots
    
    Examples:
        >>> auth = AlpacaAuth(api_key="key", secret_key="secret")
        >>> async with MarketDataClient(auth) as client:
        ...     snapshot = await client.get_snapshot("AAPL")
        ...     print(snapshot.latest_trade.p)
    """

    def __init__(self, auth: AlpacaAuth) -> None:
        """Initialize the MarketDataClient.
        
        Args:
            auth: AlpacaAuth instance for authentication.
        """
        base_url = auth.get_base_url("data")
        super().__init__(auth=auth, base_url=base_url)

    # ========================================
    # Bars Methods
    # ========================================

    async def get_bars(self, request: BarsRequest) -> dict[str, list[Bar]]:
        """Get historical bars for multiple symbols.
        
        Args:
            request: BarsRequest with query parameters.
            
        Returns:
            Dictionary mapping symbols to lists of Bar objects.
        """
        params = self._build_market_data_params(request)
        response = await self._get("/v2/stocks/bars", params=params)
        
        result: dict[str, list[Bar]] = {}
        bars_data = response.get("bars", {})
        for symbol, bars in bars_data.items():
            result[symbol] = [Bar.model_validate(bar) for bar in bars]
        return result

    async def get_bars_single(self, symbol: str, request: BarsRequest) -> list[Bar]:
        """Get historical bars for a single symbol.
        
        Args:
            symbol: The asset symbol.
            request: BarsRequest with query parameters.
            
        Returns:
            List of Bar objects.
        """
        params = self._build_market_data_params(request)
        response = await self._get(f"/v2/stocks/{symbol}/bars", params=params)
        
        bars_data = response.get("bars", [])
        return [Bar.model_validate(bar) for bar in bars_data]

    async def get_latest_bars(
        self,
        symbols: list[str],
        feed: Optional[DataFeed] = None,
    ) -> dict[str, Bar]:
        """Get latest bars for multiple symbols.
        
        Args:
            symbols: List of asset symbols.
            feed: Optional data feed (IEX or SIP).
            
        Returns:
            Dictionary mapping symbols to Bar objects.
        """
        params: dict[str, Any] = {"symbols": ",".join(symbols)}
        if feed:
            params["feed"] = feed.value if isinstance(feed, DataFeed) else feed
        
        response = await self._get("/v2/stocks/bars/latest", params=params)
        
        result: dict[str, Bar] = {}
        bars_data = response.get("bars", {})
        for symbol, bar in bars_data.items():
            result[symbol] = Bar.model_validate(bar)
        return result

    # ========================================
    # Quotes Methods
    # ========================================

    async def get_quotes(self, request: QuotesRequest) -> dict[str, list[Quote]]:
        """Get historical quotes for multiple symbols.
        
        Args:
            request: QuotesRequest with query parameters.
            
        Returns:
            Dictionary mapping symbols to lists of Quote objects.
        """
        params = self._build_market_data_params(request)
        response = await self._get("/v2/stocks/quotes", params=params)
        
        result: dict[str, list[Quote]] = {}
        quotes_data = response.get("quotes", {})
        for symbol, quotes in quotes_data.items():
            result[symbol] = [Quote.model_validate(quote) for quote in quotes]
        return result

    async def get_latest_quotes(
        self,
        symbols: list[str],
        feed: Optional[DataFeed] = None,
    ) -> dict[str, Quote]:
        """Get latest quotes for multiple symbols.
        
        Args:
            symbols: List of asset symbols.
            feed: Optional data feed (IEX or SIP).
            
        Returns:
            Dictionary mapping symbols to Quote objects.
        """
        params: dict[str, Any] = {"symbols": ",".join(symbols)}
        if feed:
            params["feed"] = feed.value if isinstance(feed, DataFeed) else feed
        
        response = await self._get("/v2/stocks/quotes/latest", params=params)
        
        result: dict[str, Quote] = {}
        quotes_data = response.get("quotes", {})
        for symbol, quote in quotes_data.items():
            result[symbol] = Quote.model_validate(quote)
        return result

    # ========================================
    # Trades Methods
    # ========================================

    async def get_trades(self, request: TradesRequest) -> dict[str, list[Trade]]:
        """Get historical trades for multiple symbols.
        
        Args:
            request: TradesRequest with query parameters.
            
        Returns:
            Dictionary mapping symbols to lists of Trade objects.
        """
        params = self._build_market_data_params(request)
        response = await self._get("/v2/stocks/trades", params=params)
        
        result: dict[str, list[Trade]] = {}
        trades_data = response.get("trades", {})
        for symbol, trades in trades_data.items():
            result[symbol] = [Trade.model_validate(trade) for trade in trades]
        return result

    async def get_latest_trades(
        self,
        symbols: list[str],
        feed: Optional[DataFeed] = None,
    ) -> dict[str, Trade]:
        """Get latest trades for multiple symbols.
        
        Args:
            symbols: List of asset symbols.
            feed: Optional data feed (IEX or SIP).
            
        Returns:
            Dictionary mapping symbols to Trade objects.
        """
        params: dict[str, Any] = {"symbols": ",".join(symbols)}
        if feed:
            params["feed"] = feed.value if isinstance(feed, DataFeed) else feed
        
        response = await self._get("/v2/stocks/trades/latest", params=params)
        
        result: dict[str, Trade] = {}
        trades_data = response.get("trades", {})
        for symbol, trade in trades_data.items():
            result[symbol] = Trade.model_validate(trade)
        return result

    # ========================================
    # Snapshot Methods
    # ========================================

    async def get_snapshots(
        self,
        symbols: list[str],
        feed: Optional[DataFeed] = None,
    ) -> dict[str, Snapshot]:
        """Get market snapshots for multiple symbols.
        
        Args:
            symbols: List of asset symbols.
            feed: Optional data feed (IEX or SIP).
            
        Returns:
            Dictionary mapping symbols to Snapshot objects.
        """
        params: dict[str, Any] = {"symbols": ",".join(symbols)}
        if feed:
            params["feed"] = feed.value if isinstance(feed, DataFeed) else feed
        
        response = await self._get("/v2/stocks/snapshots", params=params)
        
        result: dict[str, Snapshot] = {}
        for symbol, snapshot in response.items():
            result[symbol] = Snapshot.model_validate(snapshot)
        return result

    async def get_snapshot(
        self,
        symbol: str,
        feed: Optional[DataFeed] = None,
    ) -> Snapshot:
        """Get market snapshot for a single symbol.
        
        Args:
            symbol: The asset symbol.
            feed: Optional data feed (IEX or SIP).
            
        Returns:
            Snapshot object.
        """
        params: dict[str, Any] = {}
        if feed:
            params["feed"] = feed.value if isinstance(feed, DataFeed) else feed
        
        response = await self._get(
            f"/v2/stocks/{symbol}/snapshot",
            params=params if params else None,
        )
        return Snapshot.model_validate(response)

    # ========================================
    # Helper Methods
    # ========================================

    def _build_market_data_params(
        self, request: BarsRequest | QuotesRequest | TradesRequest
    ) -> dict[str, Any]:
        """Build query parameters for market data requests.
        
        Args:
            request: Request object (BarsRequest, QuotesRequest, or TradesRequest).
            
        Returns:
            Dictionary of query parameters.
        """
        params = request.model_dump(mode="json", exclude_none=True, by_alias=True)
        
        # Convert symbols list to comma-separated string
        if "symbols" in params and params["symbols"]:
            params["symbols"] = ",".join(params["symbols"])
        
        # Note: datetime fields are already serialized to ISO format strings
        # by model_dump(mode="json"), so no need to call .isoformat()
        
        # Convert timeframe enum value
        if "timeframe" in params:
            params["timeframe"] = (
                params["timeframe"].value
                if hasattr(params["timeframe"], "value")
                else params["timeframe"]
            )
        
        # Convert feed enum value
        if "feed" in params:
            params["feed"] = (
                params["feed"].value
                if hasattr(params["feed"], "value")
                else params["feed"]
            )
        
        return params