from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from core.models import BaseModel

User = get_user_model()


class AssetCategory(BaseModel):
    """
    Asset categories for better organization and classification
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("name"),
        help_text=_("Name of the asset category")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("Description of the asset category")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("parent category"),
        help_text=_("Parent category for hierarchical organization")
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("icon"),
        help_text=_("Icon class or identifier for UI display")
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name=_("color"),
        help_text=_("Hex color code for UI display")
    )

    class Meta:
        verbose_name_plural = "Asset Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        """Validate that a parent is not self"""
        if self.parent == self:
            raise ValidationError(_("Category cannot be its own parent"))

    def get_full_path(self):
        """Get the full category path (parent > child)"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class Asset(BaseModel):
    """
     Asset model with comprehensive tracking and validation
    """
    ASSET_TYPES = [
        ('STOCK', _('Stock')),
        ('BOND', _('Bond')),
        ('CRYPTO', _('Cryptocurrency')),
        ('REAL_ESTATE', _('Real Estate')),
        ('COMMODITY', _('Commodity')),
        ('CASH', _('Cash')),
        ('ETF', _('Exchange Traded Fund')),
        ('MUTUAL_FUND', _('Mutual Fund')),
        ('DERIVATIVE', _('Derivative')),
        ('OTHER', _('Other'))
    ]

    STATUS_CHOICES = [
        ('ACTIVE', _('Active')),
        ('INACTIVE', _('Inactive')),
        ('PENDING', _('Pending')),
        ('SUSPENDED', _('Suspended')),
        ('DELISTED', _('Delisted')),
        ('SOLD', _('Sold'))
    ]

    RISK_LEVELS = [
        ('LOW', _('Low Risk')),
        ('MEDIUM', _('Medium Risk')),
        ('HIGH', _('High Risk')),
        ('VERY_HIGH', _('Very High Risk'))
    ]

    name = models.CharField(
        max_length=200,
        verbose_name=_("name"),
        help_text=_("Full name of the asset"),
        db_index=True
    )
    symbol = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_("symbol"),
        help_text=_("Unique symbol or ticker for the asset"),
        db_index=True
    )
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPES,
        verbose_name=_("asset type"),
        help_text=_("Type of asset (stock, bond, crypto, etc.)"),
        db_index=True
    )
    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets',
        verbose_name=_("category"),
        help_text=_("Asset category for organization")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("Detailed description of the asset")
    )
    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("company name"),
        help_text=_("Name of the issuing company or entity")
    )
    website_url = models.URLField(
        blank=True,
        verbose_name=_("website URL"),
        help_text=_("Official website URL")
    )

    current_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("current price"),
        help_text=_("Current market price of the asset")
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("currency"),
        help_text=_("Currency code (e.g., USD, EUR, GBP)")
    )
    market_cap = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("market cap"),
        help_text=_("Total market capitalization of the asset")
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVELS,
        default='MEDIUM',
        verbose_name=_("risk level"),
        help_text=_("Risk assessment of the asset")
    )
    beta = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name=_("beta"),
        help_text=_("Beta coefficient measuring volatility relative to market")
    )
    dividend_yield = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name=_("dividend yield"),
        help_text=_("Annual dividend yield percentage")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name=_("status"),
        help_text=_("Current status of the asset"),
        db_index=True
    )
    exchange = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("exchange"),
        help_text=_("Stock exchange or trading platform")
    )
    isin = models.CharField(
        max_length=12,
        blank=True,
        unique=True,
        null=True,
        verbose_name=_("ISIN"),
        help_text=_("International Securities Identification Number")
    )

    price_last_updated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("price last updated"),
        help_text=_("When the price was last updated")
    )
    day_high = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("day high"),
        help_text=_("Highest price today")
    )
    day_low = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("day low"),
        help_text=_("Lowest price today")
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['asset_type']),
            models.Index(fields=['status']),
            models.Index(fields=['current_price']),
            models.Index(fields=['market_cap']),
        ]

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def clean(self):
        """Custom validation"""
        super().clean()

        if self.day_high and self.day_low and self.day_high < self.day_low:
            raise ValidationError(_("Day high cannot be less than day low"))

        if self.isin and len(self.isin) != 12:
            raise ValidationError(_("ISIN must be exactly 12 characters"))

    def update_price(self, new_price, update_high_low=True):
        """Update the asset price and optionally day high/low"""
        self.current_price = new_price
        self.price_last_updated = timezone.now()

        if update_high_low:
            if not self.day_high or new_price > self.day_high:
                self.day_high = new_price
            if not self.day_low or new_price < self.day_low:
                self.day_low = new_price

        self.save(update_fields=[
            'current_price', 'price_last_updated', 'day_high', 'day_low'
        ])

    def get_total_volume(self):
        """Get total trading volume for this asset"""
        from django.db.models import Sum
        return self.transactions.filter(
            status='COMPLETED'
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')

    def get_transaction_count(self):
        """Get the total number of completed transactions"""
        return self.transactions.filter(status='COMPLETED').count()


class Transaction(BaseModel):
    """
     Transaction model with comprehensive tracking and validation
    """
    TRANSACTION_TYPES = [
        ('BUY', _('Buy')),
        ('SELL', _('Sell')),
        ('TRANSFER_IN', _('Transfer In')),
        ('TRANSFER_OUT', _('Transfer Out')),
        ('DIVIDEND', _('Dividend')),
        ('SPLIT', _('Stock Split')),
        ('MERGE', _('Merger')),
        ('SPIN_OFF', _('Spin-off')),
        ('RIGHTS', _('Rights Issue')),
        ('BONUS', _('Bonus Issue'))
    ]

    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('CANCELLED', _('Cancelled')),
        ('PARTIALLY_FILLED', _('Partially Filled'))
    ]

    ORDER_TYPES = [
        ('MARKET', _('Market Order')),
        ('LIMIT', _('Limit Order')),
        ('STOP', _('Stop Order')),
        ('STOP_LIMIT', _('Stop Limit Order'))
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("user"),
        help_text=_("User who made the transaction")
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_("asset"),
        help_text=_("Asset involved in the transaction")
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name=_("transaction type"),
        help_text=_("Type of transaction"),
        db_index=True
    )

    # Financial Details
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))],
        verbose_name=_("quantity"),
        help_text=_("Number of units transacted")
    )
    price_per_unit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("price per unit"),
        help_text=_("Price per unit at the time of transaction")
    )
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_("total amount"),
        help_text=_("Total transaction amount including fees")
    )
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("fees"),
        help_text=_("Transaction fees charged")
    )
    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("tax"),
        help_text=_("Tax amount for the transaction")
    )

    order_type = models.CharField(
        max_length=15,
        choices=ORDER_TYPES,
        default='MARKET',
        verbose_name=_("order type"),
        help_text=_("Type of order placed")
    )
    limit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("limit price"),
        help_text=_("Limit price for limit orders")
    )
    stop_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name=_("stop price"),
        help_text=_("Stop price for stop orders")
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name=_("status"),
        help_text=_("Current status of the transaction"),
        db_index=True
    )
    transaction_date = models.DateTimeField(
        verbose_name=_("transaction date"),
        help_text=_("Date and time when the transaction occurred"),
        db_index=True,
        default=timezone.now
    )
    settlement_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("settlement date"),
        help_text=_("Date when the transaction settles")
    )

    notes = models.TextField(
        blank=True,
        verbose_name=_("notes"),
        help_text=_("Additional notes about the transaction")
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("external ID"),
        help_text=_("External system transaction ID")
    )
    broker = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("broker"),
        help_text=_("Broker or exchange used for the transaction")
    )

    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['asset', 'transaction_date']),
            models.Index(fields=['status', 'transaction_date']),
            models.Index(fields=['transaction_type', 'transaction_date']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.asset.symbol} by {self.user.username}"

    def clean(self):
        """Custom validation"""
        super().clean()

        # Validate order type-specific fields
        if self.order_type in ['LIMIT', 'STOP_LIMIT'] and not self.limit_price:
            raise ValidationError(_("Limit price is required for limit orders"))

        if self.order_type in ['STOP', 'STOP_LIMIT'] and not self.stop_price:
            raise ValidationError(_("Stop price is required for stop orders"))

        # Validate transaction date
        if self.transaction_date > timezone.now():
            raise ValidationError(_("Transaction date cannot be in the future"))

    def save(self, *args, **kwargs):
        """Calculate the total amount if not provided"""
        if not self.total_amount:
            gross_amount = self.quantity * self.price_per_unit
            self.total_amount = gross_amount + self.fees + self.tax

        super().save(*args, **kwargs)

    def get_net_amount(self):
        """Get net amount after fees and taxes"""
        if self.transaction_type == 'BUY':
            return self.total_amount
        else:  # SELL
            return self.total_amount - self.fees - self.tax

    def calculate_profit_loss(self, current_price=None):
        """Calculate profit/loss for this transaction"""
        if self.transaction_type not in ['BUY', 'SELL']:
            return None

        if not current_price:
            current_price = self.asset.current_price

        if self.transaction_type == 'BUY':
            current_value = self.quantity * current_price
            return current_value - self.total_amount
        else:  # SELL

            return None


class Report(BaseModel):
    """
     Report model with better organization and metadata
    """
    REPORT_TYPES = [
        ('PORTFOLIO_SUMMARY', _('Portfolio Summary')),
        ('PERFORMANCE', _('Performance Report')),
        ('TAX_REPORT', _('Tax Report')),
        ('TRANSACTION_HISTORY', _('Transaction History')),
        ('ASSET_ALLOCATION', _('Asset Allocation')),
        ('MONTHLY_SUMMARY', _('Monthly Summary')),
        ('QUARTERLY_SUMMARY', _('Quarterly Summary')),
        ('YEARLY_SUMMARY', _('Yearly Summary')),
        ('CUSTOM', _('Custom Report'))
    ]

    STATUS_CHOICES = [
        ('GENERATING', _('Generating')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('EXPIRED', _('Expired'))
    ]

    FORMAT_CHOICES = [
        ('JSON', _('JSON')),
        ('PDF', _('PDF')),
        ('CSV', _('CSV')),
        ('XLSX', _('Excel'))
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name=_("user"),
        help_text=_("User who owns the report")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("title"),
        help_text=_("Title of the report")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("Description of the report content")
    )
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPES,
        verbose_name=_("report type"),
        help_text=_("Type of report"),
        db_index=True
    )

    data = models.JSONField(
        verbose_name=_("data"),
        help_text=_("Report data stored as JSON")
    )
    parameters = models.JSONField(
        default=dict,
        verbose_name=_("parameters"),
        help_text=_("Parameters used to generate the report")
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default='JSON',
        verbose_name=_("format"),
        help_text=_("Report output format")
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='GENERATING',
        verbose_name=_("status"),
        help_text=_("Current status of the report"),
        db_index=True
    )
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("generated at"),
        help_text=_("Date and time when the report was generated")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("completed at"),
        help_text=_("Date and time when the report generation was completed")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("expires at"),
        help_text=_("Date and time when the report expires")
    )

    # Period Information
    period_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("period start"),
        help_text=_("Start date of the report period")
    )
    period_end = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("period end"),
        help_text=_("End date of the report period")
    )

    file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True,
        verbose_name=_("file"),
        help_text=_("Generated report file")
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("file size"),
        help_text=_("Size of the generated file in bytes")
    )

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['user', 'report_type']),
            models.Index(fields=['status', 'generated_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def is_expired(self):
        """Check if the report has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def mark_completed(self):
        """Mark the report as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self, error_message=None):
        """Mark the report as failed"""
        self.status = 'FAILED'
        if error_message:
            self.data = {'error': error_message}
        self.save(update_fields=['status', 'data'])