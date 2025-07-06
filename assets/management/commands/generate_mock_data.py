"""
Comprehensive mock data generator for asset management system
Works with a custom User model and all related models
"""

import random
import os
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
import io

from assets.models import Asset, AssetCategory, Transaction, Report
from accounts.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate comprehensive mock data for testing the asset management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=25,
            help='Number of users to create (default: 25)'
        )
        parser.add_argument(
            '--assets',
            type=int,
            default=100,
            help='Number of assets to create (default: 100)'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=500,
            help='Number of transactions to create (default: 500)'
        )
        parser.add_argument(
            '--reports',
            type=int,
            default=20,
            help='Number of reports to create (default: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a superuser account'
        )
        parser.add_argument(
            '--verified-users',
            type=float,
            default=0.8,
            help='Percentage of users to mark as verified (0.0-1.0, default: 0.8)'
        )

    def handle(self, *args, **options):
        """Execute the command"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting mock data generation...')
        )

        if options['clear']:
            self.clear_existing_data()

        # Create data in order of dependencies
        categories = self.create_asset_categories()
        users = self.create_users(options['users'], options['verified_users'])

        if options['create_superuser']:
            self.create_superuser()

        assets = self.create_assets(options['assets'], categories)
        transactions = self.create_transactions(options['transactions'], users, assets)
        reports = self.create_reports(options['reports'], users)

        # Display summary
        self.display_summary(users, assets, transactions, reports)

        self.stdout.write(
            self.style.SUCCESS('✅ Mock data generation completed successfully!')
        )

    def clear_existing_data(self):
        """Clear existing data"""
        self.stdout.write('🧹 Clearing existing data...')

        Report.objects.all().delete()
        Transaction.objects.all().delete()
        Asset.objects.all().delete()
        AssetCategory.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(
            self.style.WARNING('   Cleared all existing data')
        )

    def create_superuser(self):
        """Create a superuser account"""
        try:
            if not User.objects.filter(email='admin@example.com').exists():
                superuser = User.objects.create_user(
                    email='admin@example.com',
                    username='admin',
                    password='admin123',
                    first_name='System',
                    last_name='Administrator',
                    is_staff=True,
                    is_superuser=True,
                    is_verified=True,
                    is_active=True
                )

                # Create profile for superuser
                Profile.objects.create(
                    user=superuser,
                    bio='System administrator account for managing the asset management platform.',
                    location='Headquarters',
                    city='San Francisco'
                )

                self.stdout.write(
                    self.style.SUCCESS('   ✅ Created superuser: admin@example.com / admin123')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Error creating superuser: {str(e)}')
            )

    def create_asset_categories(self):
        """Create asset categories with realistic data"""
        self.stdout.write('📂 Creating asset categories...')

        categories_data = [
            {
                'name': 'Technology',
                'description': 'Technology and software companies including FAANG stocks, semiconductor companies, and emerging tech startups.',
                'color': '#007bff',
                'icon': 'fas fa-microchip'
            },
            {
                'name': 'Healthcare & Pharmaceuticals',
                'description': 'Healthcare providers, pharmaceutical companies, biotechnology firms, and medical device manufacturers.',
                'color': '#28a745',
                'icon': 'fas fa-heartbeat'
            },
            {
                'name': 'Financial Services',
                'description': 'Banks, insurance companies, investment firms, payment processors, and fintech companies.',
                'color': '#ffc107',
                'icon': 'fas fa-university'
            },
            {
                'name': 'Energy & Utilities',
                'description': 'Oil & gas companies, renewable energy firms, electric utilities, and energy infrastructure.',
                'color': '#dc3545',
                'icon': 'fas fa-bolt'
            },
            {
                'name': 'Consumer Goods',
                'description': 'Retail companies, consumer products, food & beverage, and e-commerce platforms.',
                'color': '#6f42c1',
                'icon': 'fas fa-shopping-cart'
            },
            {
                'name': 'Real Estate',
                'description': 'REITs, property development companies, real estate management, and infrastructure.',
                'color': '#20c997',
                'icon': 'fas fa-building'
            },
            {
                'name': 'Cryptocurrency',
                'description': 'Digital currencies, blockchain projects, DeFi protocols, and crypto infrastructure.',
                'color': '#fd7e14',
                'icon': 'fab fa-bitcoin'
            },
            {
                'name': 'Commodities',
                'description': 'Precious metals, agricultural products, oil futures, and commodity ETFs.',
                'color': '#795548',
                'icon': 'fas fa-coins'
            },
            {
                'name': 'Bonds & Fixed Income',
                'description': 'Government bonds, corporate bonds, municipal bonds, and fixed income securities.',
                'color': '#17a2b8',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'ETFs & Index Funds',
                'description': 'Exchange-traded funds, index funds, sector ETFs, and diversified investment vehicles.',
                'color': '#6c757d',
                'icon': 'fas fa-layer-group'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = AssetCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color'],
                    'icon': cat_data['icon']
                }
            )
            categories.append(category)

            if created:
                self.stdout.write(f'   ✅ Created category: {category.name}')

        return categories

    def create_users(self, count, verified_percentage):
        """Create users with profiles and realistic data"""
        self.stdout.write(f'👥 Creating {count} users...')

        # Sample user data
        first_names = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica',
            'William', 'Ashley', 'James', 'Amanda', 'Daniel', 'Stephanie', 'Matthew',
            'Jennifer', 'Christopher', 'Nicole', 'Andrew', 'Elizabeth', 'Joshua',
            'Heather', 'Kenneth', 'Samantha', 'Kevin', 'Rachel', 'Brian', 'Amy',
            'George', 'Angela', 'Timothy', 'Brenda', 'Ronald', 'Emma', 'Jason',
            'Olivia', 'Edward', 'Cynthia', 'Jeffrey', 'Marie', 'Ryan', 'Janet',
            'Jacob', 'Catherine', 'Gary', 'Frances', 'Nicholas', 'Christine'
        ]

        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green',
            'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell'
        ]

        cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis',
            'Seattle', 'Denver', 'Washington', 'Boston', 'El Paso', 'Nashville',
            'Detroit', 'Oklahoma City', 'Portland', 'Las Vegas', 'Memphis', 'Louisville',
            'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno', 'Sacramento',
            'Mesa', 'Kansas City', 'Atlanta', 'Long Beach', 'Colorado Springs',
            'Raleigh', 'Miami', 'Virginia Beach', 'Omaha', 'Oakland', 'Minneapolis',
            'Tulsa', 'Arlington', 'Tampa', 'New Orleans'
        ]

        locations = [
            'United States', 'Canada', 'United Kingdom', 'Germany', 'France',
            'Australia', 'Japan', 'South Korea', 'Singapore', 'Netherlands',
            'Switzerland', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Belgium',
            'Austria', 'Ireland', 'New Zealand', 'Luxembourg'
        ]

        bio_templates = [
            "Passionate investor with {years} years of experience in {specialty}. Love analyzing market trends and finding undervalued opportunities.",
            "Financial analyst specializing in {specialty}. Building a diversified portfolio focused on long-term growth and income generation.",
            "Tech entrepreneur turned investor. Particularly interested in {specialty} and emerging market opportunities.",
            "Retired professional with a focus on dividend investing and {specialty}. Enjoys sharing investment insights with the community.",
            "Young investor just starting the journey. Learning about {specialty} and building wealth for the future.",
            "Quantitative analyst with expertise in {specialty}. Data-driven approach to investment decisions and risk management.",
            "Value investor following Warren Buffett's principles. Focus on {specialty} and companies with strong competitive moats.",
            "Portfolio manager with institutional experience. Specializing in {specialty} and alternative investment strategies."
        ]

        specialties = [
            'technology stocks', 'value investing', 'growth investing', 'dividend stocks',
            'cryptocurrency', 'real estate', 'commodities', 'international markets',
            'small-cap stocks', 'ESG investing', 'momentum trading', 'index funds',
            'options trading', 'fixed income', 'emerging markets', 'healthcare stocks'
        ]

        users = []
        num_verified = int(count * verified_percentage)

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@example.com"

            # Ensure unique username and email
            counter = 1
            while User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1000, 9999)}"
                email = f"{username}@example.com"
                counter += 1
                if counter > 10:  # Prevent infinite loop
                    username = f"user{i}_{random.randint(10000, 99999)}"
                    email = f"{username}@example.com"
                    break

            # Determine if user should be verified
            is_verified = i < num_verified

            try:
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password='password123',  # Same password for all test users
                    first_name=first_name,
                    last_name=last_name,
                    is_verified=is_verified,
                    is_active=is_verified,  # Only verified users are active
                    date_joined=timezone.now() - timedelta(
                        days=random.randint(1, 365)
                    )
                )

                # Create profile
                specialty = random.choice(specialties)
                years = random.randint(1, 15)
                bio = random.choice(bio_templates).format(
                    years=years,
                    specialty=specialty
                )

                profile = Profile.objects.create(
                    user=user,
                    bio=bio,
                    location=random.choice(locations),
                    city=random.choice(cities)
                )

                # Optionally add profile image (mock)
                if random.random() < 0.3:  # 30% chance of having profile image
                    profile.profile_image = self.create_mock_profile_image(user)
                    profile.save()

                users.append(user)

                status = "✅ verified" if is_verified else "⏳ unverified"
                self.stdout.write(f'   👤 Created user: {email} ({status})')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error creating user {email}: {str(e)}')
                )

        return users

    def create_mock_profile_image(self, user):
        """Create a mock profile image"""
        try:
            # Create a simple colored square as profile image
            img = Image.new('RGB', (200, 200), color=(
                random.randint(100, 255),
                random.randint(100, 255),
                random.randint(100, 255)
            ))

            # Save to BytesIO
            img_io = io.BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)

            # Create ContentFile
            return ContentFile(
                img_io.getvalue(),
                name=f'profile_{user.id}.png'
            )
        except Exception:
            return None

    def create_assets(self, count, categories):
        """Create realistic assets with market data"""
        self.stdout.write(f'📈 Creating {count} assets...')

        # Real stock data for major companies
        real_stocks = [
            {'name': 'Apple Inc.', 'symbol': 'AAPL', 'price': 175.84, 'market_cap': 2800000000000, 'type': 'STOCK'},
            {'name': 'Microsoft Corporation', 'symbol': 'MSFT', 'price': 338.11, 'market_cap': 2500000000000,
             'type': 'STOCK'},
            {'name': 'Alphabet Inc.', 'symbol': 'GOOGL', 'price': 125.37, 'market_cap': 1600000000000, 'type': 'STOCK'},
            {'name': 'Amazon.com Inc.', 'symbol': 'AMZN', 'price': 146.80, 'market_cap': 1500000000000,
             'type': 'STOCK'},
            {'name': 'Tesla Inc.', 'symbol': 'TSLA', 'price': 248.50, 'market_cap': 790000000000, 'type': 'STOCK'},
            {'name': 'Meta Platforms Inc.', 'symbol': 'META', 'price': 296.73, 'market_cap': 750000000000,
             'type': 'STOCK'},
            {'name': 'NVIDIA Corporation', 'symbol': 'NVDA', 'price': 421.13, 'market_cap': 1040000000000,
             'type': 'STOCK'},
            {'name': 'Berkshire Hathaway Inc.', 'symbol': 'BRK-B', 'price': 348.42, 'market_cap': 760000000000,
             'type': 'STOCK'},
            {'name': 'JPMorgan Chase & Co.', 'symbol': 'JPM', 'price': 153.23, 'market_cap': 450000000000,
             'type': 'STOCK'},
            {'name': 'Johnson & Johnson', 'symbol': 'JNJ', 'price': 161.45, 'market_cap': 425000000000,
             'type': 'STOCK'},

            # Crypto
            {'name': 'Bitcoin', 'symbol': 'BTC', 'price': 43250.00, 'market_cap': 847000000000, 'type': 'CRYPTO'},
            {'name': 'Ethereum', 'symbol': 'ETH', 'price': 2421.33, 'market_cap': 291000000000, 'type': 'CRYPTO'},
            {'name': 'Binance Coin', 'symbol': 'BNB', 'price': 309.82, 'market_cap': 47000000000, 'type': 'CRYPTO'},
            {'name': 'Solana', 'symbol': 'SOL', 'price': 96.44, 'market_cap': 41000000000, 'type': 'CRYPTO'},
            {'name': 'Cardano', 'symbol': 'ADA', 'price': 0.48, 'market_cap': 17000000000, 'type': 'CRYPTO'},

            # ETFs
            {'name': 'SPDR S&P 500 ETF', 'symbol': 'SPY', 'price': 445.23, 'market_cap': 420000000000, 'type': 'ETF'},
            {'name': 'Invesco QQQ Trust', 'symbol': 'QQQ', 'price': 367.89, 'market_cap': 180000000000, 'type': 'ETF'},
            {'name': 'Vanguard Total Stock Market ETF', 'symbol': 'VTI', 'price': 231.45, 'market_cap': 280000000000,
             'type': 'ETF'},
            {'name': 'iShares Core S&P 500 ETF', 'symbol': 'IVV', 'price': 445.67, 'market_cap': 350000000000,
             'type': 'ETF'},
            {'name': 'Vanguard FTSE Developed Markets ETF', 'symbol': 'VEA', 'price': 48.23, 'market_cap': 95000000000,
             'type': 'ETF'},

            # Bonds
            {'name': 'iShares 20+ Year Treasury Bond ETF', 'symbol': 'TLT', 'price': 93.45, 'market_cap': 18000000000,
             'type': 'BOND'},
            {'name': 'Vanguard Total Bond Market ETF', 'symbol': 'BND', 'price': 74.89, 'market_cap': 85000000000,
             'type': 'BOND'},
            {'name': 'iShares Core U.S. Aggregate Bond ETF', 'symbol': 'AGG', 'price': 99.23, 'market_cap': 95000000000,
             'type': 'BOND'},

            # Commodities
            {'name': 'SPDR Gold Shares', 'symbol': 'GLD', 'price': 185.67, 'market_cap': 58000000000,
             'type': 'COMMODITY'},
            {'name': 'iShares Silver Trust', 'symbol': 'SLV', 'price': 21.34, 'market_cap': 12000000000,
             'type': 'COMMODITY'},
        ]

        exchanges = ['NYSE', 'NASDAQ', 'BATS', 'ARCA', 'CME', 'BINANCE', 'COINBASE']
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        risk_levels = ['LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
        status_choices = ['ACTIVE', 'INACTIVE', 'SUSPENDED', 'DELISTED']

        assets = []

        # Create real assets first
        for i, stock_data in enumerate(real_stocks):
            if i >= count:
                break

            # Assign category based on asset type and name
            category = self.assign_category(stock_data['name'], stock_data['type'], categories)

            try:
                asset = Asset.objects.create(
                    name=stock_data['name'],
                    symbol=stock_data['symbol'],
                    asset_type=stock_data['type'],
                    current_price=Decimal(str(stock_data['price'])),
                    currency='USD',
                    market_cap=Decimal(str(stock_data['market_cap'])) if stock_data['market_cap'] else None,
                    category=category,
                    exchange=random.choice(exchanges),
                    risk_level=self.determine_risk_level(stock_data['type']),
                    status='ACTIVE',
                    description=f"Real-world asset: {stock_data['name']}",
                    # Add some price variation
                    day_high=Decimal(str(stock_data['price'] * random.uniform(1.01, 1.05))),
                    day_low=Decimal(str(stock_data['price'] * random.uniform(0.95, 0.99))),
                    price_last_updated=timezone.now() - timedelta(minutes=random.randint(1, 60)),
                    beta=round(random.uniform(0.5, 2.0), 2) if stock_data['type'] == 'STOCK' else None,
                    dividend_yield=round(random.uniform(0, 5), 2) if stock_data['type'] in ['STOCK', 'ETF'] else None
                )
                assets.append(asset)
                self.stdout.write(f'   📊 Created real asset: {asset.symbol} - {asset.name}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error creating asset {stock_data["symbol"]}: {str(e)}')
                )

        # Create synthetic assets for remaining count
        remaining = count - len(real_stocks)
        if remaining > 0:
            self.stdout.write(f'   🎲 Creating {remaining} synthetic assets...')

            for i in range(remaining):
                asset_type = random.choice(['STOCK', 'BOND', 'CRYPTO', 'ETF', 'MUTUAL_FUND', 'COMMODITY'])
                symbol = self.generate_symbol(i + len(real_stocks))
                name = self.generate_asset_name(symbol, asset_type)

                # Price based on an asset type
                if asset_type == 'CRYPTO':
                    price = round(random.uniform(0.01, 50000), 2)
                elif asset_type in ['STOCK', 'ETF']:
                    price = round(random.uniform(10, 500), 2)
                elif asset_type == 'BOND':
                    price = round(random.uniform(50, 150), 2)
                else:
                    price = round(random.uniform(5, 1000), 2)

                market_cap = random.randint(1000000, 1000000000000) if asset_type != 'BOND' else None

                try:
                    asset = Asset.objects.create(
                        name=name,
                        symbol=symbol,
                        asset_type=asset_type,
                        current_price=Decimal(str(price)),
                        currency=random.choice(currencies),
                        market_cap=Decimal(str(market_cap)) if market_cap else None,
                        category=random.choice(categories),
                        exchange=random.choice(exchanges),
                        risk_level=random.choice(risk_levels),
                        status=random.choices(status_choices, weights=[85, 10, 3, 2])[0],
                        description=f"Synthetic {asset_type.lower()} asset for testing purposes",
                        day_high=Decimal(str(price * random.uniform(1.01, 1.08))),
                        day_low=Decimal(str(price * random.uniform(0.92, 0.99))),
                        price_last_updated=timezone.now() - timedelta(minutes=random.randint(1, 1440)),
                        beta=round(random.uniform(0.3, 2.5), 2) if asset_type == 'STOCK' else None,
                        dividend_yield=round(random.uniform(0, 8), 2) if asset_type in ['STOCK', 'ETF'] else None
                    )
                    assets.append(asset)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Error creating synthetic asset {symbol}: {str(e)}')
                    )

        return assets

    def assign_category(self, name, asset_type, categories):
        """Assign category based on asset name and type"""
        category_mapping = {
            'technology': ['Apple', 'Microsoft', 'Alphabet', 'Google', 'Tesla', 'NVIDIA', 'Meta', 'Amazon'],
            'healthcare': ['Johnson & Johnson', 'Pfizer', 'Merck', 'Abbott'],
            'financial': ['JPMorgan', 'Berkshire', 'Bank', 'Goldman'],
            'cryptocurrency': ['Bitcoin', 'Ethereum', 'Binance', 'Solana', 'Cardano'],
            'etfs': ['SPDR', 'Vanguard', 'iShares', 'Invesco', 'QQQ'],
            'bonds': ['Treasury', 'Bond', 'AGG', 'BND', 'TLT'],
            'commodities': ['Gold', 'Silver', 'Oil', 'GLD', 'SLV']
        }

        name_lower = name.lower()

        for category_key, keywords in category_mapping.items():
            if any(keyword.lower() in name_lower for keyword in keywords):
                category_name_map = {
                    'technology': 'Technology',
                    'healthcare': 'Healthcare & Pharmaceuticals',
                    'financial': 'Financial Services',
                    'cryptocurrency': 'Cryptocurrency',
                    'etfs': 'ETFs & Index Funds',
                    'bonds': 'Bonds & Fixed Income',
                    'commodities': 'Commodities'
                }

                category_name = category_name_map[category_key]
                return next((cat for cat in categories if cat.name == category_name), random.choice(categories))

        return random.choice(categories)

    def determine_risk_level(self, asset_type):
        """Determine risk level based on an asset type"""
        risk_mapping = {
            'BOND': 'LOW',
            'ETF': 'MEDIUM',
            'STOCK': random.choice(['MEDIUM', 'HIGH']),
            'CRYPTO': 'VERY_HIGH',
            'COMMODITY': 'HIGH',
            'MUTUAL_FUND': 'MEDIUM'
        }
        return risk_mapping.get(asset_type, 'MEDIUM')

    def generate_symbol(self, index):
        """Generate a unique symbol for synthetic assets"""
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if index < 26:
            return f"SYN{letters[index]}"
        elif index < 702:  # 26 + 26*26
            first = letters[(index - 26) // 26]
            second = letters[(index - 26) % 26]
            return f"SY{first}{second}"
        else:
            return f"S{index:04d}"

    def generate_asset_name(self, symbol, asset_type):
        """Generate a realistic name for synthetic assets"""
        prefixes = {
            'STOCK': ['Global', 'Advanced', 'Premier', 'Elite', 'Dynamic', 'Strategic', 'Innovative'],
            'CRYPTO': ['Crypto', 'Digital', 'Block', 'Chain', 'Defi', 'Meta', 'Quantum'],
            'ETF': ['Index', 'Select', 'Core', 'Total', 'Broad', 'Focus', 'Diversified'],
            'BOND': ['Treasury', 'Corporate', 'Municipal', 'High-Grade', 'Secure', 'Fixed'],
            'COMMODITY': ['Natural', 'Raw', 'Essential', 'Basic', 'Primary', 'Resource'],
            'MUTUAL_FUND': ['Growth', 'Value', 'Balanced', 'Income', 'Equity', 'Bond']
        }

        suffixes = {
            'STOCK': ['Corp', 'Inc', 'Ltd', 'Group', 'Holdings', 'Enterprises', 'Industries'],
            'CRYPTO': ['Coin', 'Token', 'Protocol', 'Network', 'Chain', 'Finance'],
            'ETF': ['ETF', 'Fund', 'Index', 'Trust'],
            'BOND': ['Bond', 'Note', 'Treasury', 'Debt'],
            'COMMODITY': ['Resources', 'Materials', 'Commodities', 'Trading'],
            'MUTUAL_FUND': ['Fund', 'Investment', 'Portfolio', 'Trust']
        }

        prefix = random.choice(prefixes.get(asset_type, prefixes['STOCK']))
        suffix = random.choice(suffixes.get(asset_type, suffixes['STOCK']))

        return f"{prefix} {symbol} {suffix}"

    def create_transactions(self, count, users, assets):
        """Create realistic transactions with proper relationships"""
        self.stdout.write(f'💰 Creating {count} transactions...')

        if not users or not assets:
            self.stdout.write(
                self.style.WARNING('   ⚠️ No users or assets available for transactions')
            )
            return []

        # Filter only verified and active users
        active_users = [user for user in users if user.is_verified and user.is_active]
        active_assets = [asset for asset in assets if asset.status == 'ACTIVE']

        if not active_users or not active_assets:
            self.stdout.write(
                self.style.WARNING('   ⚠️ No active users or assets available for transactions')
            )
            return []

        transaction_types = ['BUY', 'SELL', 'TRANSFER_IN', 'TRANSFER_OUT', 'DIVIDEND']
        order_types = ['MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT']
        status_choices = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED']

        # Weight towards completed transactions
        status_weights = [5, 5, 80, 5, 5]

        transactions = []

        for i in range(count):
            user = random.choice(active_users)
            asset = random.choice(active_assets)
            transaction_type = random.choice(transaction_types)

            # Generate realistic quantities based on asset price
            if asset.current_price > 1000:  # Expensive assets
                quantity = round(random.uniform(0.1, 10), 2)
            elif asset.current_price > 100:  # Moderate price assets
                quantity = round(random.uniform(1, 100), 0)
            else:  # Cheaper assets
                quantity = round(random.uniform(10, 1000), 0)

            # Price variation around current price
            price_variation = random.uniform(0.95, 1.05)
            price_per_unit = asset.current_price * Decimal(str(price_variation))

            # Calculate fees (0.1% to 1% of transaction value)
            gross_amount = Decimal(str(quantity)) * price_per_unit
            fee_percentage = random.uniform(0.001, 0.01)
            fees = gross_amount * Decimal(str(fee_percentage))

            # Tax (0% to 0.5% for most transactions)
            tax_percentage = random.uniform(0, 0.005)
            tax = gross_amount * Decimal(str(tax_percentage))

            # Random transaction date within last year
            days_ago = random.randint(1, 365)
            transaction_date = timezone.now() - timedelta(days=days_ago)

            # Settlement date (T+2 for stocks, immediate for crypto)
            if asset.asset_type in ['STOCK', 'ETF', 'BOND']:
                settlement_date = transaction_date.date() + timedelta(days=2)
            else:
                settlement_date = transaction_date.date()

            try:
                transaction = Transaction.objects.create(
                    user=user,
                    asset=asset,
                    transaction_type=transaction_type,
                    quantity=Decimal(str(quantity)),
                    price_per_unit=price_per_unit,
                    fees=fees,
                    tax=tax,
                    order_type=random.choice(order_types),
                    limit_price=price_per_unit * Decimal(
                        str(random.uniform(1.02, 1.10))) if random.random() < 0.3 else None,
                    stop_price=price_per_unit * Decimal(
                        str(random.uniform(0.90, 0.98))) if random.random() < 0.2 else None,
                    status=random.choices(status_choices, weights=status_weights)[0],
                    transaction_date=transaction_date,
                    settlement_date=settlement_date,
                    notes=self.generate_transaction_note(transaction_type, asset),
                    external_id=f"TXN{random.randint(100000, 999999)}",
                    broker=random.choice(
                        ['Interactive Brokers', 'Charles Schwab', 'Fidelity', 'E*TRADE', 'TD Ameritrade', 'Robinhood'])
                )

                transactions.append(transaction)

                if i % 50 == 0:  # Progress update every 50 transactions
                    self.stdout.write(f'   💳 Created {i + 1}/{count} transactions...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error creating transaction {i}: {str(e)}')
                )

        return transactions

    def generate_transaction_note(self, transaction_type, asset):
        """Generate realistic transaction notes"""
        notes = {
            'BUY': [
                f"Purchased {asset.name} based on strong Q3 earnings",
                f"Adding {asset.symbol} to diversify portfolio",
                f"Dollar-cost averaging into {asset.name}",
                f"Bought the dip on {asset.symbol}",
                f"Long-term investment in {asset.name}",
                f"Rebalancing portfolio - adding {asset.symbol}"
            ],
            'SELL': [
                f"Taking profits on {asset.name}",
                f"Sold {asset.symbol} to rebalance portfolio",
                f"Liquidating position in {asset.name}",
                f"Stop-loss triggered for {asset.symbol}",
                f"Sold {asset.name} before earnings announcement",
                f"Partial exit from {asset.symbol} position"
            ],
            'DIVIDEND': [
                f"Quarterly dividend payment from {asset.name}",
                f"Dividend reinvestment for {asset.symbol}",
                f"Regular income from {asset.name}"
            ],
            'TRANSFER_IN': [
                f"Transfer of {asset.symbol} from external broker",
                f"Asset transfer: {asset.name}",
                f"Consolidating {asset.symbol} holdings"
            ],
            'TRANSFER_OUT': [
                f"Transfer of {asset.symbol} to external account",
                f"Moving {asset.name} to different broker",
                f"Gift transfer of {asset.symbol}"
            ]
        }

        return random.choice(notes.get(transaction_type, [f"Transaction for {asset.name}"]))

    def create_reports(self, count, users):
        """Create sample reports for users"""
        self.stdout.write(f'📊 Creating {count} reports...')

        if not users:
            self.stdout.write(
                self.style.WARNING('   ⚠️ No users available for reports')
            )
            return []

        # Only create reports for verified users
        verified_users = [user for user in users if user.is_verified]

        if not verified_users:
            self.stdout.write(
                self.style.WARNING('   ⚠️ No verified users available for reports')
            )
            return []

        report_types = ['PORTFOLIO_SUMMARY', 'PERFORMANCE', 'TAX_REPORT', 'TRANSACTION_HISTORY', 'ASSET_ALLOCATION',
                        'MONTHLY_SUMMARY', 'QUARTERLY_SUMMARY', 'YEARLY_SUMMARY']
        formats = ['JSON', 'PDF', 'CSV', 'XLSX']
        status_choices = ['GENERATING', 'COMPLETED', 'FAILED', 'EXPIRED']
        status_weights = [5, 85, 5, 5]

        reports = []

        for i in range(count):
            user = random.choice(verified_users)
            report_type = random.choice(report_types)

            # Generate period dates
            end_date = timezone.now().date() - timedelta(days=random.randint(1, 30))

            if 'MONTHLY' in report_type:
                start_date = end_date - timedelta(days=30)
            elif 'QUARTERLY' in report_type:
                start_date = end_date - timedelta(days=90)
            elif 'YEARLY' in report_type:
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=random.randint(30, 180))

            try:
                report = Report.objects.create(
                    user=user,
                    title=self.generate_report_title(report_type, user),
                    description=self.generate_report_description(report_type),
                    report_type=report_type,
                    format=random.choice(formats),
                    status=random.choices(status_choices, weights=status_weights)[0],
                    data=self.generate_sample_report_data(report_type),
                    parameters={'period': f"{start_date} to {end_date}", 'user_id': str(user.id)},
                    period_start=start_date,
                    period_end=end_date,
                    generated_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                    completed_at=timezone.now() - timedelta(
                        days=random.randint(0, 29)) if random.random() < 0.8 else None,
                    expires_at=timezone.now() + timedelta(days=random.randint(30, 90)),
                    file_size=random.randint(1024, 5242880)  # 1KB to 5MB
                )

                reports.append(report)
                self.stdout.write(f'   📋 Created report: {report.title}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error creating report {i}: {str(e)}')
                )

        return reports

    def generate_report_title(self, report_type, user):
        """Generate descriptive report titles"""
        titles = {
            'PORTFOLIO_SUMMARY': f"Portfolio Summary for {user.get_full_name()}",
            'PERFORMANCE': f"Performance Analysis - {user.username}",
            'TAX_REPORT': f"Tax Report {timezone.now().year} - {user.get_full_name()}",
            'TRANSACTION_HISTORY': f"Transaction History - {user.username}",
            'ASSET_ALLOCATION': f"Asset Allocation Report - {user.get_full_name()}",
            'MONTHLY_SUMMARY': f"Monthly Summary - {timezone.now().strftime('%B %Y')}",
            'QUARTERLY_SUMMARY': f"Q{(timezone.now().month - 1) // 3 + 1} {timezone.now().year} Summary",
            'YEARLY_SUMMARY': f"Annual Report {timezone.now().year}"
        }

        return titles.get(report_type, f"Custom Report - {user.username}")

    def generate_report_description(self, report_type):
        """Generate report descriptions"""
        descriptions = {
            'PORTFOLIO_SUMMARY': "Comprehensive overview of current portfolio holdings, asset allocation, and performance metrics.",
            'PERFORMANCE': "Detailed analysis of investment performance, returns, and risk metrics over the specified period.",
            'TAX_REPORT': "Summary of taxable events, capital gains/losses, and dividend income for tax reporting purposes.",
            'TRANSACTION_HISTORY': "Complete record of all transactions including purchases, sales, and transfers.",
            'ASSET_ALLOCATION': "Breakdown of portfolio allocation across different asset classes and sectors.",
            'MONTHLY_SUMMARY': "Monthly performance summary including key metrics and market movements.",
            'QUARTERLY_SUMMARY': "Quarterly review of portfolio performance and strategic positioning.",
            'YEARLY_SUMMARY': "Annual performance review with comprehensive analysis and outlook."
        }

        return descriptions.get(report_type, "Custom generated report with user-specified parameters.")

    def generate_sample_report_data(self, report_type):
        """Generate sample data for reports"""
        if report_type == 'PORTFOLIO_SUMMARY':
            return {
                'total_value': round(random.uniform(10000, 500000), 2),
                'total_return': round(random.uniform(-20, 40), 2),
                'asset_count': random.randint(5, 50),
                'top_holdings': [
                    {'symbol': 'AAPL', 'value': 15000, 'percentage': 15.5},
                    {'symbol': 'MSFT', 'value': 12000, 'percentage': 12.3},
                    {'symbol': 'GOOGL', 'value': 8500, 'percentage': 8.7}
                ]
            }
        elif report_type == 'PERFORMANCE':
            return {
                'total_return': round(random.uniform(-15, 25), 2),
                'benchmark_return': round(random.uniform(-10, 20), 2),
                'volatility': round(random.uniform(5, 30), 2),
                'sharpe_ratio': round(random.uniform(0.5, 2.5), 2),
                'max_drawdown': round(random.uniform(-25, -5), 2)
            }
        else:
            return {
                'report_type': report_type,
                'generated_at': timezone.now().isoformat(),
                'status': 'completed',
                'summary': f"Sample {report_type.lower().replace('_', ' ')} data"
            }

    def display_summary(self, users, assets, transactions, reports):
        """Display creation summary"""
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('📈 MOCK DATA GENERATION SUMMARY'))
        self.stdout.write('=' * 50)
        self.stdout.write(f'👥 Users Created: {len(users)}')
        self.stdout.write(f'   - Verified: {len([u for u in users if u.is_verified])}')
        self.stdout.write(f'   - Unverified: {len([u for u in users if not u.is_verified])}')
        self.stdout.write(f'📊 Assets Created: {len(assets)}')
        self.stdout.write(f'   - Active: {len([a for a in assets if a.status == "ACTIVE"])}')
        self.stdout.write(f'   - Other: {len([a for a in assets if a.status != "ACTIVE"])}')
        self.stdout.write(f'💰 Transactions Created: {len(transactions)}')
        self.stdout.write(f'   - Completed: {len([t for t in transactions if t.status == "COMPLETED"])}')
        self.stdout.write(f'   - Other: {len([t for t in transactions if t.status != "COMPLETED"])}')
        self.stdout.write(f'📋 Reports Created: {len(reports)}')
        self.stdout.write('\n🔐 Test Account Credentials:')
        self.stdout.write('   Email: admin@example.com')
        self.stdout.write('   Password: admin123')
        self.stdout.write('\n💡 All test users have password: password123')
        self.stdout.write('=' * 50)