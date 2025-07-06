from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import Asset, AssetCategory, Transaction, Report

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for basic user information
    """
    full_name = serializers.SerializerMethodField()
    bio = serializers.CharField(source='profile.bio', read_only=True)
    profile_image = serializers.ImageField(source='profile.image', read_only=True)
    location = serializers.CharField(source='profile.location', read_only=True)
    city = serializers.CharField(source='profile.city', read_only=True)


    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'bio', 'profile_image', 'location', 'city']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        """Get the user's full name"""
        return f"{obj.first_name} {obj.last_name}".strip()


class AssetCategorySerializer(serializers.ModelSerializer):
    """
    Asset category serializer with hierarchy support
    """
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    asset_count = serializers.SerializerMethodField()
    subcategories = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = AssetCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_asset_count(self, obj):
        """Get a number of assets in this category"""
        return obj.assets.filter(is_active=True).count()

    def validate_parent(self, value):
        """Validate parent category"""
        if value and self.instance and value == self.instance:
            raise serializers.ValidationError("Category cannot be its own parent")
        return value


class AssetListSerializer(serializers.ModelSerializer):
    """
    Lightweight asset serializer for list views
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_volume = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'symbol', 'asset_type', 'current_price', 'currency',
            'market_cap', 'status', 'category_name',
            'total_volume', 'created_at'
        ]



    def get_total_volume(self, obj):
        """Get total trading volume"""
        return obj.get_total_volume()


class AssetDetailSerializer(serializers.ModelSerializer):
    """
    Detailed asset serializer with full information
    """
    category = AssetCategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    total_volume = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    price_updated_ago = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'price_last_updated',
            'day_high', 'day_low'
        ]

    def get_total_volume(self, obj):
        """Get total trading volume"""
        return obj.get_total_volume()

    def get_transaction_count(self, obj):
        """Get transaction count"""
        return obj.get_transaction_count()

    def get_price_updated_ago(self, obj):
        """Get time since price was last updated"""
        if obj.price_last_updated:
            delta = timezone.now() - obj.price_last_updated
            return delta.total_seconds()
        return None

    def validate_current_price(self, value):
        """Validate current price"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero")
        return value

    def validate_symbol(self, value):
        """Validate symbol uniqueness"""
        if self.instance:
            # Update case - exclude current instance
            if Asset.objects.filter(symbol=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Asset with this symbol already exists")
        else:
            # Create a case
            if Asset.objects.filter(symbol=value).exists():
                raise serializers.ValidationError("Asset with this symbol already exists")
        return value.upper()


class AssetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new assets
    """

    class Meta:
        model = Asset
        fields = [
            'name', 'symbol', 'asset_type', 'category', 'description',
            'company_name', 'website_url', 'current_price', 'currency',
           'risk_level'
        ]

    def validate_symbol(self, value):
        """Validate and format symbol"""
        symbol = value.upper().strip()
        if Asset.objects.filter(symbol=symbol).exists():
            raise serializers.ValidationError("Asset with this symbol already exists")
        return symbol

    def create(self, validated_data):
        """Create asset with price update timestamp"""
        validated_data['price_last_updated'] = timezone.now()
        return super().create(validated_data)


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Lightweight transaction serializer for list views
    """
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    asset_symbol = serializers.CharField(source='asset.symbol', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    net_amount = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'asset_name', 'asset_symbol',
            'user_username', 'quantity', 'price_per_unit', 'total_amount',
            'net_amount', 'status', 'transaction_date', 'created_at'
        ]

    def get_net_amount(self, obj):
        """Get net transaction amount"""
        return obj.get_net_amount()


class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed transaction serializer
    """
    asset = AssetListSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    asset_id = serializers.UUIDField(write_only=True)
    user_id = serializers.UUIDField(write_only=True, required=False)
    net_amount = serializers.SerializerMethodField()
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'total_amount'
        ]

    def get_net_amount(self, obj):
        """Get net transaction amount"""
        return obj.get_net_amount()

    def get_profit_loss(self, obj):
        """Get profit/loss for the transaction"""
        return obj.calculate_profit_loss()

    def validate(self, data):
        """Cross-field validation"""
        # Set user to current user if not provided
        if not data.get('user_id'):
            request = self.context.get('request')
            if request and request.user:
                data['user_id'] = request.user.id

        # Validate order type-specific fields
        order_type = data.get('order_type', 'MARKET')
        if order_type in ['LIMIT', 'STOP_LIMIT'] and not data.get('limit_price'):
            raise serializers.ValidationError({
                'limit_price': 'Limit price is required for limit orders'
            })

        if order_type in ['STOP', 'STOP_LIMIT'] and not data.get('stop_price'):
            raise serializers.ValidationError({
                'stop_price': 'Stop price is required for stop orders'
            })

        # Validate transaction date
        transaction_date = data.get('transaction_date')
        if transaction_date and transaction_date > timezone.now():
            raise serializers.ValidationError({
                'transaction_date': 'Transaction date cannot be in the future'
            })

        return data

    def create(self, validated_data):
        """Create transaction with calculated total amount"""
        # Calculate the total amount if not provided
        quantity = validated_data['quantity']
        price_per_unit = validated_data['price_per_unit']
        fees = validated_data.get('fees', Decimal('0'))
        tax = validated_data.get('tax', Decimal('0'))

        gross_amount = quantity * price_per_unit
        validated_data['total_amount'] = gross_amount + fees + tax

        return super().create(validated_data)


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating transactions
    """

    class Meta:
        model = Transaction
        fields = [
            'asset', 'transaction_type', 'quantity', 'price_per_unit',
            'fees', 'tax', 'order_type', 'limit_price', 'stop_price',
            'notes','broker'
        ]

    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value

    def validate_price_per_unit(self, value):
        """Validate price per unit"""
        if value <= 0:
            raise serializers.ValidationError("Price per unit must be greater than zero")
        return value

    def create(self, validated_data):
        """Create transaction with user from request"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user

        # Set a transaction date if not provided
        if not validated_data.get('transaction_date'):
            validated_data['transaction_date'] = timezone.now()

        return super().create(validated_data)


class ReportSerializer(serializers.ModelSerializer):
    """
    Report serializer with status and metadata
    """
    user = UserSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = [
            'id', 'generated_at', 'completed_at', 'file_size'
        ]

    def get_is_expired(self, obj):
        """Check if a report is expired"""
        return obj.is_expired()

    def get_file_size_mb(self, obj):
        """Get file size in MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None

    def get_duration(self, obj):
        """Get to report generation duration"""
        if obj.completed_at and obj.generated_at:
            delta = obj.completed_at - obj.generated_at
            return delta.total_seconds()
        return None


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new reports
    """

    class Meta:
        model = Report
        fields = [
            'title', 'description', 'report_type', 'format',
            'parameters', 'period_start', 'period_end'
        ]

    def create(self, validated_data):
        """Create a report with user from request"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user

        # Set initial status and data
        validated_data['status'] = 'GENERATING'
        validated_data['data'] = {}

        return super().create(validated_data)