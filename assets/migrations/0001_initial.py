# Generated by Django 5.2.4 on 2025-07-06 10:52

import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the record', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this record is active', verbose_name='is active')),
                ('name', models.CharField(help_text='Name of the asset category', max_length=100, unique=True, verbose_name='name')),
                ('description', models.TextField(blank=True, help_text='Description of the asset category', verbose_name='description')),
                ('icon', models.CharField(blank=True, help_text='Icon class or identifier for UI display', max_length=50, verbose_name='icon')),
                ('color', models.CharField(default='#007bff', help_text='Hex color code for UI display', max_length=7, verbose_name='color')),
                ('parent', models.ForeignKey(blank=True, help_text='Parent category for hierarchical organization', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='assets.assetcategory', verbose_name='parent category')),
            ],
            options={
                'verbose_name_plural': 'Asset Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the record', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this record is active', verbose_name='is active')),
                ('name', models.CharField(db_index=True, help_text='Full name of the asset', max_length=200, verbose_name='name')),
                ('symbol', models.CharField(db_index=True, help_text='Unique symbol or ticker for the asset', max_length=20, unique=True, verbose_name='symbol')),
                ('asset_type', models.CharField(choices=[('STOCK', 'Stock'), ('BOND', 'Bond'), ('CRYPTO', 'Cryptocurrency'), ('REAL_ESTATE', 'Real Estate'), ('COMMODITY', 'Commodity'), ('CASH', 'Cash'), ('ETF', 'Exchange Traded Fund'), ('MUTUAL_FUND', 'Mutual Fund'), ('DERIVATIVE', 'Derivative'), ('OTHER', 'Other')], db_index=True, help_text='Type of asset (stock, bond, crypto, etc.)', max_length=20, verbose_name='asset type')),
                ('description', models.TextField(blank=True, help_text='Detailed description of the asset', verbose_name='description')),
                ('company_name', models.CharField(blank=True, help_text='Name of the issuing company or entity', max_length=200, verbose_name='company name')),
                ('website_url', models.URLField(blank=True, help_text='Official website URL', verbose_name='website URL')),
                ('current_price', models.DecimalField(decimal_places=2, help_text='Current market price of the asset', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='current price')),
                ('currency', models.CharField(default='USD', help_text='Currency code (e.g., USD, EUR, GBP)', max_length=3, verbose_name='currency')),
                ('market_cap', models.DecimalField(blank=True, decimal_places=2, help_text='Total market capitalization of the asset', max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='market cap')),
                ('risk_level', models.CharField(choices=[('LOW', 'Low Risk'), ('MEDIUM', 'Medium Risk'), ('HIGH', 'High Risk'), ('VERY_HIGH', 'Very High Risk')], default='MEDIUM', help_text='Risk assessment of the asset', max_length=10, verbose_name='risk level')),
                ('beta', models.DecimalField(blank=True, decimal_places=3, help_text='Beta coefficient measuring volatility relative to market', max_digits=5, null=True, verbose_name='beta')),
                ('dividend_yield', models.DecimalField(blank=True, decimal_places=2, help_text='Annual dividend yield percentage', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))], verbose_name='dividend yield')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('PENDING', 'Pending'), ('SUSPENDED', 'Suspended'), ('DELISTED', 'Delisted'), ('SOLD', 'Sold')], db_index=True, default='ACTIVE', help_text='Current status of the asset', max_length=20, verbose_name='status')),
                ('exchange', models.CharField(blank=True, help_text='Stock exchange or trading platform', max_length=100, verbose_name='exchange')),
                ('isin', models.CharField(blank=True, help_text='International Securities Identification Number', max_length=12, null=True, unique=True, verbose_name='ISIN')),
                ('price_last_updated', models.DateTimeField(blank=True, help_text='When the price was last updated', null=True, verbose_name='price last updated')),
                ('day_high', models.DecimalField(blank=True, decimal_places=2, help_text='Highest price today', max_digits=15, null=True, verbose_name='day high')),
                ('day_low', models.DecimalField(blank=True, decimal_places=2, help_text='Lowest price today', max_digits=15, null=True, verbose_name='day low')),
                ('category', models.ForeignKey(blank=True, help_text='Asset category for organization', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='assets.assetcategory', verbose_name='category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the record', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this record is active', verbose_name='is active')),
                ('title', models.CharField(help_text='Title of the report', max_length=200, verbose_name='title')),
                ('description', models.TextField(blank=True, help_text='Description of the report content', verbose_name='description')),
                ('report_type', models.CharField(choices=[('PORTFOLIO_SUMMARY', 'Portfolio Summary'), ('PERFORMANCE', 'Performance Report'), ('TAX_REPORT', 'Tax Report'), ('TRANSACTION_HISTORY', 'Transaction History'), ('ASSET_ALLOCATION', 'Asset Allocation'), ('MONTHLY_SUMMARY', 'Monthly Summary'), ('QUARTERLY_SUMMARY', 'Quarterly Summary'), ('YEARLY_SUMMARY', 'Yearly Summary'), ('CUSTOM', 'Custom Report')], db_index=True, help_text='Type of report', max_length=30, verbose_name='report type')),
                ('data', models.JSONField(help_text='Report data stored as JSON', verbose_name='data')),
                ('parameters', models.JSONField(default=dict, help_text='Parameters used to generate the report', verbose_name='parameters')),
                ('format', models.CharField(choices=[('JSON', 'JSON'), ('PDF', 'PDF'), ('CSV', 'CSV'), ('XLSX', 'Excel')], default='JSON', help_text='Report output format', max_length=10, verbose_name='format')),
                ('status', models.CharField(choices=[('GENERATING', 'Generating'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('EXPIRED', 'Expired')], db_index=True, default='GENERATING', help_text='Current status of the report', max_length=15, verbose_name='status')),
                ('generated_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the report was generated', verbose_name='generated at')),
                ('completed_at', models.DateTimeField(blank=True, help_text='Date and time when the report generation was completed', null=True, verbose_name='completed at')),
                ('expires_at', models.DateTimeField(blank=True, help_text='Date and time when the report expires', null=True, verbose_name='expires at')),
                ('period_start', models.DateField(blank=True, help_text='Start date of the report period', null=True, verbose_name='period start')),
                ('period_end', models.DateField(blank=True, help_text='End date of the report period', null=True, verbose_name='period end')),
                ('file', models.FileField(blank=True, help_text='Generated report file', null=True, upload_to='reports/', verbose_name='file')),
                ('file_size', models.BigIntegerField(blank=True, help_text='Size of the generated file in bytes', null=True, verbose_name='file size')),
                ('user', models.ForeignKey(help_text='User who owns the report', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the record', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the record was created', verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the record was last updated', verbose_name='updated at')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this record is active', verbose_name='is active')),
                ('transaction_type', models.CharField(choices=[('BUY', 'Buy'), ('SELL', 'Sell'), ('TRANSFER_IN', 'Transfer In'), ('TRANSFER_OUT', 'Transfer Out'), ('DIVIDEND', 'Dividend'), ('SPLIT', 'Stock Split'), ('MERGE', 'Merger'), ('SPIN_OFF', 'Spin-off'), ('RIGHTS', 'Rights Issue'), ('BONUS', 'Bonus Issue')], db_index=True, help_text='Type of transaction', max_length=20, verbose_name='transaction type')),
                ('quantity', models.DecimalField(decimal_places=8, help_text='Number of units transacted', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('1E-8'))], verbose_name='quantity')),
                ('price_per_unit', models.DecimalField(decimal_places=2, help_text='Price per unit at the time of transaction', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='price per unit')),
                ('total_amount', models.DecimalField(decimal_places=2, help_text='Total transaction amount including fees', max_digits=20, verbose_name='total amount')),
                ('fees', models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Transaction fees charged', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='fees')),
                ('tax', models.DecimalField(decimal_places=2, default=Decimal('0'), help_text='Tax amount for the transaction', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='tax')),
                ('order_type', models.CharField(choices=[('MARKET', 'Market Order'), ('LIMIT', 'Limit Order'), ('STOP', 'Stop Order'), ('STOP_LIMIT', 'Stop Limit Order')], default='MARKET', help_text='Type of order placed', max_length=15, verbose_name='order type')),
                ('limit_price', models.DecimalField(blank=True, decimal_places=2, help_text='Limit price for limit orders', max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='limit price')),
                ('stop_price', models.DecimalField(blank=True, decimal_places=2, help_text='Stop price for stop orders', max_digits=15, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='stop price')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled'), ('PARTIALLY_FILLED', 'Partially Filled')], db_index=True, default='PENDING', help_text='Current status of the transaction', max_length=20, verbose_name='status')),
                ('transaction_date', models.DateTimeField(db_index=True, help_text='Date and time when the transaction occurred', verbose_name='transaction date')),
                ('settlement_date', models.DateField(blank=True, help_text='Date when the transaction settles', null=True, verbose_name='settlement date')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about the transaction', verbose_name='notes')),
                ('external_id', models.CharField(blank=True, help_text='External system transaction ID', max_length=100, verbose_name='external ID')),
                ('broker', models.CharField(blank=True, help_text='Broker or exchange used for the transaction', max_length=100, verbose_name='broker')),
                ('asset', models.ForeignKey(help_text='Asset involved in the transaction', on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='assets.asset', verbose_name='asset')),
                ('user', models.ForeignKey(help_text='User who made the transaction', on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'ordering': ['-transaction_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='assetcategory',
            index=models.Index(fields=['name'], name='assets_asse_name_a8ecf6_idx'),
        ),
        migrations.AddIndex(
            model_name='assetcategory',
            index=models.Index(fields=['parent'], name='assets_asse_parent__a16aad_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['symbol'], name='assets_asse_symbol_71b57b_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['asset_type'], name='assets_asse_asset_t_529092_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['status'], name='assets_asse_status_347ce9_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['current_price'], name='assets_asse_current_260563_idx'),
        ),
        migrations.AddIndex(
            model_name='asset',
            index=models.Index(fields=['market_cap'], name='assets_asse_market__e5b267_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['user', 'report_type'], name='assets_repo_user_id_81e1ff_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['status', 'generated_at'], name='assets_repo_status_c269c4_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['expires_at'], name='assets_repo_expires_a43c20_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['user', 'transaction_date'], name='assets_tran_user_id_2603d0_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['asset', 'transaction_date'], name='assets_tran_asset_i_f7eee3_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['status', 'transaction_date'], name='assets_tran_status_c0365c_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type', 'transaction_date'], name='assets_tran_transac_d2e2c2_idx'),
        ),
    ]
