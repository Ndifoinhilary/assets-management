import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Asset, AssetCategory, Transaction, Report
from .permissions import IsOwnerOrAdminPermission
from .serializers import (
    AssetDetailSerializer, AssetListSerializer, AssetCreateSerializer,
    AssetCategorySerializer, TransactionDetailSerializer,
    TransactionListSerializer, TransactionCreateSerializer,
    ReportSerializer, ReportCreateSerializer, UserSerializer
)
from .utils import (
    get_user_growth_data, get_asset_distribution_data,
    get_transaction_volume_data, get_portfolio_performance_data,
    get_asset_type_performance, get_top_assets_by_volume,
    get_transaction_trends
)

logger = logging.getLogger(__name__)
User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListUsersAPIView(GenericAPIView):
    """
    API view to list all users.
    You must be authenticated to access this view.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="List all users in the system",
        responses={
            200: openapi.Response("List of users retrieved successfully"),
            401: openapi.Response("Authentication credentials were not provided"),
        }
    )
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        logger.info("There are %d users in the system", users.count())
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="List all asset categories",
        description="Retrieve a list of all asset categories with optional filtering",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search categories by name or description'
            ),
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by parent category ID'
            ),
        ],
        responses={200: AssetCategorySerializer(many=True)}
    ),
    create=extend_schema(
        summary="Create a new asset category",
        description="Create a new asset category with the provided information",
        request=AssetCategorySerializer,
        responses={
            201: AssetCategorySerializer,
            400: "Bad Request - Validation errors"
        },
        examples=[
            OpenApiExample(
                "Category Creation",
                value={
                    "name": "Technology Stocks",
                    "description": "Technology sector stocks",
                    "parent": None,
                    "icon": "tech-icon",
                    "color": "#007bff"
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get asset category details",
        description="Retrieve detailed information about a specific asset category"
    ),
    update=extend_schema(
        summary="Update asset category",
        description="Update an existing asset category"
    ),
    destroy=extend_schema(
        summary="Delete asset category",
        description="Delete an asset category (soft delete)"
    )
)
class AssetCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing asset categories

    Provides CRUD operations for asset categories with hierarchical support.
    """
    queryset = AssetCategory.objects.filter(is_active=True)
    serializer_class = AssetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="List all assets",
        description="Retrieve a paginated list of all assets with optional filtering and searching",
        parameters=[
            OpenApiParameter(
                name='asset_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by asset type (STOCK, BOND, CRYPTO, etc.)'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by asset status (ACTIVE, INACTIVE, etc.)'
            ),
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by category ID'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search assets by name, symbol, or description'
            ),
            OpenApiParameter(
                name='min_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Minimum price filter'
            ),
            OpenApiParameter(
                name='max_price',
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
        ],
        responses={200: AssetListSerializer(many=True)}
    ),
    create=extend_schema(
        summary="Create a new asset",
        description="Add a new asset to the system with comprehensive information",
        request=AssetCreateSerializer,
        responses={
            201: AssetDetailSerializer,
            400: "Bad Request - Validation errors"
        },
        examples=[
            OpenApiExample(
                "Stock Creation",
                value={
                    "name": "Apple Inc.",
                    "symbol": "AAPL",
                    "asset_type": "STOCK",
                    "description": "Technology company that designs and manufactures consumer electronics",
                    "company_name": "Apple Inc.",
                    "current_price": "150.25",
                    "currency": "USD",
                    "market_cap": "2400000000000",
                    "risk_level": "MEDIUM",
                    "exchange": "NASDAQ"
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Get asset details",
        description="Retrieve comprehensive information about a specific asset including transaction history"
    ),
    update=extend_schema(
        summary="Update asset information",
        description="Update an existing asset's information"
    ),
    destroy=extend_schema(
        summary="Delete asset",
        description="Remove an asset from the system (soft delete)"
    )
)
class AssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for comprehensive asset management

    Provides full CRUD operations for assets with advanced filtering,
    searching, and analytics capabilities.
    """
    queryset = Asset.objects.filter(is_active=True).select_related('category')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_type', 'status', 'category', 'risk_level', 'currency']
    search_fields = ['name', 'symbol', 'description', 'company_name']
    ordering_fields = ['name', 'symbol', 'current_price', 'market_cap', 'created_at']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Return the appropriate serializer based on action"""
        if self.action == 'list':
            return AssetListSerializer
        elif self.action == 'create':
            return AssetCreateSerializer
        return AssetDetailSerializer

    def get_queryset(self):
        """Enhanced queryset with custom filtering"""
        queryset = super().get_queryset()

        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            try:
                queryset = queryset.filter(current_price__gte=Decimal(min_price))
            except (ValueError, TypeError):
                pass  # Invalid price format, ignore filter

        if max_price:
            try:
                queryset = queryset.filter(current_price__lte=Decimal(max_price))
            except (ValueError, TypeError):
                pass  # Invalid price format, ignore filter

        return queryset

    def create(self, request, *args, **kwargs):
        """Create an asset with enhanced error handling"""
        try:
            logger.info(f"Creating new asset: {request.data.get('name')} ({request.data.get('symbol')})")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            asset = serializer.save()

            response_serializer = AssetDetailSerializer(asset, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating asset: {str(e)}")
            return Response(
                {
                    'error': 'Failed to create asset',
                    'details': str(e) if request.user.is_staff else 'Invalid data provided'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Update asset price",
        description="Update the current price of an asset and optionally the day high/low",
        request={
            'type': 'object',
            'properties': {
                'price': {'type': 'number', 'format': 'decimal'},
                'update_high_low': {'type': 'boolean', 'default': True}
            },
            'required': ['price']
        },
        responses={
            200: AssetDetailSerializer,
            400: "Bad Request",
            404: "Asset not found"
        }
    )
    @action(detail=True, methods=['post'])
    def update_price(self, request, pk=None):
        """Update asset price with day high/low tracking"""
        try:
            asset = self.get_object()
            new_price = request.data.get('price')
            update_high_low = request.data.get('update_high_low', True)

            if not new_price:
                return Response(
                    {'error': 'Price is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                new_price = Decimal(str(new_price))
                if new_price <= 0:
                    raise ValueError("Price must be positive")
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid price format'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            asset.update_price(new_price, update_high_low)

            serializer = AssetDetailSerializer(asset, context={'request': request})
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error updating price for asset {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to update price'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Get asset statistics",
        description="Retrieve comprehensive statistics for a specific asset",
        responses={200: {
            'type': 'object',
            'properties': {
                'total_volume': {'type': 'number'},
                'transaction_count': {'type': 'integer'},
                'avg_transaction_size': {'type': 'number'},
                'price_performance': {'type': 'object'},
                'recent_transactions': {'type': 'array'}
            }
        }}
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get comprehensive asset statistics"""
        try:
            asset = self.get_object()

            transactions = asset.transactions.filter(status='COMPLETED')
            total_volume = transactions.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            transaction_count = transactions.count()

            avg_transaction_size = total_volume / transaction_count if transaction_count > 0 else Decimal('0')

            recent_transactions = transactions.order_by('-transaction_date')[:10]
            recent_transactions_data = TransactionListSerializer(
                recent_transactions, many=True, context={'request': request}
            ).data

            buy_volume = transactions.filter(
                transaction_type='BUY'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            sell_volume = transactions.filter(
                transaction_type='SELL'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            return Response({
                'asset': AssetListSerializer(asset, context={'request': request}).data,
                'statistics': {
                    'total_volume': total_volume,
                    'transaction_count': transaction_count,
                    'avg_transaction_size': avg_transaction_size,
                    'buy_volume': buy_volume,
                    'sell_volume': sell_volume,
                    'buy_sell_ratio': float(buy_volume / sell_volume) if sell_volume > 0 else None
                },
                'recent_transactions': recent_transactions_data
            })

        except Exception as e:
            logger.error(f"Error getting statistics for asset {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve statistics'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    list=extend_schema(
        summary="List transactions",
        description="Retrieve a paginated list of transactions with comprehensive filtering",
        parameters=[
            OpenApiParameter(
                name='user',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by user ID'
            ),
            OpenApiParameter(
                name='asset',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by asset ID'
            ),
            OpenApiParameter(
                name='transaction_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by transaction type (BUY, SELL, etc.)'
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by transaction status'
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter transactions from this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter transactions to this date (YYYY-MM-DD)'
            ),
        ]
    ),
    create=extend_schema(
        summary="Record a new transaction",
        description="Create a new transaction record with comprehensive validation",
        request=TransactionCreateSerializer,
        responses={
            201: TransactionDetailSerializer,
            400: "Bad Request - Validation errors"
        },
        examples=[
            OpenApiExample(
                "Buy Transaction",
                value={
                    "asset": "uuid-here",
                    "transaction_type": "BUY",
                    "quantity": "100",
                    "price_per_unit": "150.25",
                    "fees": "9.99",
                    "order_type": "MARKET",
                    "notes": "Monthly investment",
                    "broker": "Interactive Brokers"
                }
            )
        ]
    )
)
class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for comprehensive transaction management

    Handles all transaction operations including creation, retrieval,
    and analytics with proper validation and error handling.
    """
    queryset = Transaction.objects.select_related('asset', 'user').filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'asset', 'order_type']
    search_fields = ['asset__name', 'asset__symbol', 'notes', 'external_id']
    ordering_fields = ['transaction_date', 'created_at', 'total_amount']
    ordering = ['-transaction_date', '-created_at']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Return the appropriate serializer based on action"""
        if self.action == 'list':
            return TransactionListSerializer
        elif self.action == 'create':
            return TransactionCreateSerializer
        return TransactionDetailSerializer

    def get_queryset(self):
        """queryset with user filtering and date range"""
        # Handle schema generation for drf-yasg
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()

        queryset = super().get_queryset()

        # Check if user is authenticated first
        if not self.request.user.is_authenticated:
            return queryset.none()

        # User-specific filtering (non-admin users see only their transactions)
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            # Admin can filter by specific user
            user_id = self.request.query_params.get('user')
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        # Date range filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            try:
                queryset = queryset.filter(transaction_date__date__gte=date_from)
            except ValueError:
                pass  # Invalid date format, ignore filter

        if date_to:
            try:
                queryset = queryset.filter(transaction_date__date__lte=date_to)
            except ValueError:
                pass  # Invalid date format, ignore filter

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a transaction with enhanced validation and logging"""
        try:
            logger.info(f"Recording new transaction for user: {request.user.username}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            transaction = serializer.save()

            # Return detailed serializer for response
            response_serializer = TransactionDetailSerializer(
                transaction, context={'request': request}
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            return Response(
                {
                    'error': 'Failed to record transaction',
                    'details': str(e) if request.user.is_staff else 'Invalid transaction data'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Get user's transaction summary",
        description="Retrieve transaction summary statistics for the current user",
        responses={200: {
            'type': 'object',
            'properties': {
                'total_transactions': {'type': 'integer'},
                'total_volume': {'type': 'number'},
                'buy_volume': {'type': 'number'},
                'sell_volume': {'type': 'number'},
                'recent_transactions': {'type': 'array'}
            }
        }}
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary for the current user"""
        try:
            user_transactions = Transaction.objects.filter(
                user=request.user,
                is_active=True
            )

            completed_transactions = user_transactions.filter(status='COMPLETED')

            total_transactions = completed_transactions.count()
            total_volume = completed_transactions.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')

            buy_volume = completed_transactions.filter(
                transaction_type='BUY'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            sell_volume = completed_transactions.filter(
                transaction_type='SELL'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

            recent_transactions = user_transactions.order_by('-transaction_date')[:5]
            recent_data = TransactionListSerializer(
                recent_transactions, many=True, context={'request': request}
            ).data

            return Response({
                'summary': {
                    'total_transactions': total_transactions,
                    'total_volume': total_volume,
                    'buy_volume': buy_volume,
                    'sell_volume': sell_volume,
                    'net_volume': buy_volume - sell_volume,
                    'pending_transactions': user_transactions.filter(status='PENDING').count()
                },
                'recent_transactions': recent_data
            })

        except Exception as e:
            logger.error(f"Error getting transaction summary: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve transaction summary'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    list=extend_schema(
        summary="List reports",
        description="Retrieve a list of generated reports for the current user"
    ),
    create=extend_schema(
        summary="Generate a new report",
        description="Create and generate a new report with specified parameters",
        request=ReportCreateSerializer
    )
)
class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for report management and generation

    Handles report creation, retrieval, and status tracking.
    You can only get your own report created or login as admin to get all reports in the system
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status', 'format']
    search_fields = ['title', 'description']
    ordering_fields = ['generated_at', 'completed_at']
    ordering = ['-generated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filter reports by user unless admin"""
        # Handle schema generation for drf-yasg
        if getattr(self, 'swagger_fake_view', False):
            return Report.objects.none()

        queryset = Report.objects.filter(is_active=True)

        # Check if user is authenticated first
        if not self.request.user.is_authenticated:
            return queryset.none()

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            user_id = self.request.query_params.get('user')
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_serializer_class(self):
        """Return the appropriate serializer based on action"""
        if self.action == 'create':
            return ReportCreateSerializer
        return ReportSerializer


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics and dashboard graph data

    Provides comprehensive analytics data for dashboard visualization,
    including user growth, asset distribution, transaction trends, and more.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get analytics dashboard graphs",
        operation_description="""
        Retrieve comprehensive graph data for analytics dashboard with customizable time periods.

        This endpoint provides various types of analytics data including:
        - User growth trends over time
        - Asset distribution by type and value  
        - Transaction volume and frequency
        - Portfolio performance metrics
        - Asset type performance analysis
        - Top assets by trading volume
        - Transaction trends and patterns

        You can filter by time period (1-365 days) and optionally request specific graph types.
        """,
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description='Number of days for time-based graphs (1-365, default: 30)',
                type=openapi.TYPE_INTEGER,
                default=30,
                minimum=1,
                maximum=365,
                required=False,
            ),
            openapi.Parameter(
                'graph_type',
                openapi.IN_QUERY,
                description='Specific graph type to retrieve. If not provided, returns all graph data.',
                type=openapi.TYPE_STRING,
                enum=[
                    'user_growth',
                    'asset_distribution',
                    'transaction_volume',
                    'portfolio_performance',
                    'asset_type_performance',
                    'top_assets',
                    'transaction_trends'
                ],
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description='Analytics data successfully retrieved',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user_growth': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='User registration trends over time',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                    'new_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        ),
                        'asset_distribution': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Distribution of assets by type and value',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'asset_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'total_value': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                  format=openapi.FORMAT_DECIMAL),
                                }
                            )
                        ),
                        'transaction_volume': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Transaction volume and frequency over time',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                    'volume': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        ),
                        'portfolio_performance': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Portfolio performance metrics by user',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'portfolio_value': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                      format=openapi.FORMAT_DECIMAL),
                                    'performance_percentage': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                             format=openapi.FORMAT_FLOAT),
                                }
                            )
                        ),
                        'asset_type_performance': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Performance metrics grouped by asset type',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'asset_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'avg_performance': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                      format=openapi.FORMAT_FLOAT),
                                    'total_volume': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                   format=openapi.FORMAT_DECIMAL),
                                }
                            )
                        ),
                        'top_assets': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Most actively traded assets by volume',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'asset_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'asset_symbol': openapi.Schema(type=openapi.TYPE_STRING),
                                    'trading_volume': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                     format=openapi.FORMAT_DECIMAL),
                                    'transaction_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                }
                            )
                        ),
                        'transaction_trends': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Transaction patterns and trends by type',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'transaction_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'volume': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
                                }
                            )
                        ),
                        'summary': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Summary statistics for the requested period',
                            properties={
                                'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'total_assets': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'total_transactions': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'total_volume': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_DECIMAL),
                                'date_range': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'start_date': openapi.Schema(type=openapi.TYPE_STRING,
                                                                     format=openapi.FORMAT_DATETIME),
                                        'end_date': openapi.Schema(type=openapi.TYPE_STRING,
                                                                   format=openapi.FORMAT_DATETIME),
                                        'days': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    }
                                )
                            }
                        )
                    }
                ),
                examples={
                    'application/json': {
                        "user_growth": [
                            {"date": "2024-01-01", "new_users": 5, "total_users": 150},
                            {"date": "2024-01-02", "new_users": 8, "total_users": 158}
                        ],
                        "asset_distribution": [
                            {"asset_type": "STOCK", "count": 45, "total_value": 125000},
                            {"asset_type": "CRYPTO", "count": 30, "total_value": 85000}
                        ],
                        "transaction_volume": [
                            {"date": "2024-01-01", "volume": 15000, "count": 25},
                            {"date": "2024-01-02", "volume": 18000, "count": 30}
                        ],
                        "summary": {
                            "total_users": 150,
                            "total_assets": 75,
                            "total_transactions": 1200,
                            "total_volume": 2500000,
                            "date_range": {
                                "start_date": "2024-01-01T00:00:00Z",
                                "end_date": "2024-01-31T23:59:59Z",
                                "days": 30
                            }
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Bad Request - Invalid parameters',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Days parameter must be between 1 and 365'
                        )
                    }
                )
            ),
            401: openapi.Response(
                description='Unauthorized - Authentication required',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Authentication credentials were not provided.'
                        )
                    }
                )
            ),
            500: openapi.Response(
                description='Internal Server Error',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Failed to generate analytics data'
                        ),
                        'details': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example='Internal server error'
                        )
                    }
                )
            )
        },
        tags=['Analytics']
    )
    @action(detail=False, methods=['get'])
    def graphs(self, request):
        """
        Return comprehensive graph data for dashboard

        This is the main endpoint for analytics dashboard data.
        Supports filtering by time period and specific graph types.
        """
        try:
            # Get parameters
            days = int(request.query_params.get('days', 30))
            graph_type = request.query_params.get('graph_type')

            # Validate days parameter
            if days < 1 or days > 365:
                return Response(
                    {'error': 'Days parameter must be between 1 and 365'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate date range
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)

            response_data = {}

            # If a specific graph type requested, return only that
            if graph_type:
                if graph_type == 'user_growth':
                    response_data['user_growth'] = get_user_growth_data(start_date, end_date)
                elif graph_type == 'asset_distribution':
                    response_data['asset_distribution'] = get_asset_distribution_data()
                elif graph_type == 'transaction_volume':
                    response_data['transaction_volume'] = get_transaction_volume_data(start_date, end_date)
                elif graph_type == 'portfolio_performance':
                    response_data['portfolio_performance'] = get_portfolio_performance_data()
                elif graph_type == 'asset_type_performance':
                    response_data['asset_type_performance'] = get_asset_type_performance()
                elif graph_type == 'top_assets':
                    response_data['top_assets'] = get_top_assets_by_volume()
                elif graph_type == 'transaction_trends':
                    response_data['transaction_trends'] = get_transaction_trends(start_date, end_date)
                else:
                    return Response(
                        {'error': f'Unknown graph type: {graph_type}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Return all graph data
                response_data.update({
                    'user_growth': get_user_growth_data(start_date, end_date),
                    'asset_distribution': get_asset_distribution_data(),
                    'transaction_volume': get_transaction_volume_data(start_date, end_date),
                    'portfolio_performance': get_portfolio_performance_data(),
                    'asset_type_performance': get_asset_type_performance(),
                    'top_assets': get_top_assets_by_volume(),
                    'transaction_trends': get_transaction_trends(start_date, end_date)
                })

            response_data['summary'] = {
                'total_users': User.objects.filter(is_active=True).count(),
                'total_assets': Asset.objects.filter(is_active=True).count(),
                'total_transactions': Transaction.objects.filter(is_active=True).count(),
                'total_volume': Transaction.objects.filter(
                    status='COMPLETED',
                    is_active=True
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }

            logger.info(f"Successfully generated analytics data for {days} days")
            return Response(response_data)

        except ValueError as e:
            logger.error(f"Invalid parameter in analytics request: {str(e)}")
            return Response(
                {'error': 'Invalid parameters provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error generating analytics data: {str(e)}")
            return Response(
                {
                    'error': 'Failed to generate analytics data',
                    'details': str(e) if request.user.is_staff else 'Internal server error'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Get available graph types",
        operation_description="Retrieve list of available graph types for analytics dashboard",
        responses={
            200: openapi.Response(
                description='List of available graph types',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'available_graphs': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'key': openapi.Schema(type=openapi.TYPE_STRING),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            )
                        )
                    }
                ),
                examples={
                    'application/json': {
                        "available_graphs": [
                            {
                                "key": "user_growth",
                                "name": "User Growth",
                                "description": "User registration trends over time"
                            },
                            {
                                "key": "asset_distribution",
                                "name": "Asset Distribution",
                                "description": "Distribution of assets by type and value"
                            }
                        ]
                    }
                }
            )
        },
        tags=['Analytics']
    )
    @action(detail=False, methods=['get'])
    def available_graphs(self, request):
        """Get a list of available graph types"""
        graphs = [
            {
                'key': 'user_growth',
                'name': 'User Growth',
                'description': 'User registration trends over time'
            },
            {
                'key': 'asset_distribution',
                'name': 'Asset Distribution',
                'description': 'Distribution of assets by type and value'
            },
            {
                'key': 'transaction_volume',
                'name': 'Transaction Volume',
                'description': 'Transaction volume and frequency over time'
            },
            {
                'key': 'portfolio_performance',
                'name': 'Portfolio Performance',
                'description': 'Individual user portfolio performance metrics'
            },
            {
                'key': 'asset_type_performance',
                'name': 'Asset Type Performance',
                'description': 'Performance metrics grouped by asset type'
            },
            {
                'key': 'top_assets',
                'name': 'Top Assets',
                'description': 'Most actively traded assets by volume'
            },
            {
                'key': 'transaction_trends',
                'name': 'Transaction Trends',
                'description': 'Transaction patterns and trends by type'
            }
        ]

        return Response({'available_graphs': graphs})
