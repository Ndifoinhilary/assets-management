from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta, datetime
import logging

from .models import Transaction, Asset

logger = logging.getLogger(__name__)
User = get_user_model()


def get_asset_distribution_data():
    """
    Get distribution of assets by type with enhanced metrics

    Returns:
        list: Asset distribution data with counts and values
    """
    try:
        distribution = Asset.objects.filter(is_active=True).values('asset_type').annotate(
            count=Count('id'),
            total_value=Sum('current_price'),
            avg_price=Avg('current_price'),
            market_cap_total=Sum('market_cap')
        ).order_by('-count')

        # Convert Decimal to float for JSON serialization
        result = []
        for item in distribution:
            result.append({
                'asset_type': item['asset_type'],
                'count': item['count'],
                'total_value': float(item['total_value'] or 0),
                'avg_price': float(item['avg_price'] or 0),
                'market_cap_total': float(item['market_cap_total'] or 0)
            })

        return result

    except Exception as e:
        logger.error(f"Error in get_asset_distribution_data: {str(e)}")
        return []


def get_transaction_volume_data(start_date, end_date):
    """
    Get transaction volume over time with improved aggregation

    Args:
        start_date (datetime): Start date for the period
        end_date (datetime): End date for the period

    Returns:
        list: Daily transaction volume data
    """
    try:
        # Use Django's date truncation for better performance
        volume_by_date = Transaction.objects.filter(
            transaction_date__range=[start_date, end_date],
            status='COMPLETED',
            is_active=True
        ).extra(
            select={'date': 'DATE(transaction_date)'}
        ).values('date').annotate(
            volume=Sum('total_amount'),
            count=Count('id'),
            buy_volume=Sum('total_amount', filter=Q(transaction_type='BUY')),
            sell_volume=Sum('total_amount', filter=Q(transaction_type='SELL')),
            avg_transaction_size=Avg('total_amount')
        ).order_by('date')

        # Convert to list with proper formatting
        result = []
        for item in volume_by_date:
            result.append({
                'date': item['date'].isoformat() if item['date'] else None,
                'volume': float(item['volume'] or 0),
                'count': item['count'],
                'buy_volume': float(item['buy_volume'] or 0),
                'sell_volume': float(item['sell_volume'] or 0),
                'avg_transaction_size': float(item['avg_transaction_size'] or 0)
            })

        return result

    except Exception as e:
        logger.error(f"Error in get_transaction_volume_data: {str(e)}")
        return []


def get_portfolio_performance_data():
    """
    Get portfolio performance by user with comprehensive metrics

    Returns:
        list: User portfolio performance data
    """
    try:
        performance = []

        # Get users who have completed transactions
        active_users = User.objects.filter(
            transactions__status='COMPLETED',
            transactions__is_active=True,
            is_active=True
        ).distinct()

        for user in active_users:
            user_transactions = Transaction.objects.filter(
                user=user,
                status='COMPLETED',
                is_active=True
            )

            # Calculate buy and sell totals
            buy_data = user_transactions.filter(transaction_type='BUY').aggregate(
                total=Sum('total_amount'),
                count=Count('id'),
                avg_size=Avg('total_amount')
            )

            sell_data = user_transactions.filter(transaction_type='SELL').aggregate(
                total=Sum('total_amount'),
                count=Count('id'),
                avg_size=Avg('total_amount')
            )

            buy_total = buy_data['total'] or 0
            sell_total = sell_data['total'] or 0
            net_investment = buy_total - sell_total

            # Calculate portfolio metrics
            total_transactions = user_transactions.count()

            performance.append({
                'user_id': str(user.id),
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'total_invested': float(buy_total),
                'total_returns': float(sell_total),
                'net_position': float(net_investment),
                'total_transactions': total_transactions,
                'buy_transactions': buy_data['count'] or 0,
                'sell_transactions': sell_data['count'] or 0,
                'avg_buy_size': float(buy_data['avg_size'] or 0),
                'avg_sell_size': float(sell_data['avg_size'] or 0),
                'roi_percentage': float((sell_total - buy_total) / buy_total * 100) if buy_total > 0 else 0
            })

        # Sort by net position descending
        performance.sort(key=lambda x: x['net_position'], reverse=True)

        return performance

    except Exception as e:
        logger.error(f"Error in get_portfolio_performance_data: {str(e)}")
        return []


def get_asset_type_performance():
    """
    Get performance metrics by asset type with enhanced analytics

    Returns:
        list: Asset type performance data
    """
    try:
        performance = Asset.objects.filter(is_active=True).values('asset_type').annotate(
            total_volume=Sum(
                'transactions__total_amount',
                filter=Q(transactions__status='COMPLETED', transactions__is_active=True)
            ),
            avg_price=Avg('current_price'),
            transaction_count=Count(
                'transactions',
                filter=Q(transactions__status='COMPLETED', transactions__is_active=True)
            ),
            asset_count=Count('id'),
            total_market_cap=Sum('market_cap'),
            min_price=Min('current_price'),
            max_price=Max('current_price')
        ).order_by('-total_volume')

        # Convert to proper format
        result = []
        for item in performance:
            if item['total_volume']:  # Only include types with transactions
                result.append({
                    'asset_type': item['asset_type'],
                    'total_volume': float(item['total_volume']),
                    'avg_price': float(item['avg_price'] or 0),
                    'transaction_count': item['transaction_count'],
                    'asset_count': item['asset_count'],
                    'total_market_cap': float(item['total_market_cap'] or 0),
                    'min_price': float(item['min_price'] or 0),
                    'max_price': float(item['max_price'] or 0),
                    'avg_volume_per_asset': float(item['total_volume'] / item['asset_count']) if item[
                                                                                                     'asset_count'] > 0 else 0
                })

        return result

    except Exception as e:
        logger.error(f"Error in get_asset_type_performance: {str(e)}")
        return []


def get_top_assets_by_volume(limit=10):
    """
    Get top assets by trading volume with comprehensive metrics

    Args:
        limit (int): Number of top assets to return

    Returns:
        list: Top assets data
    """
    try:
        top_assets = Asset.objects.filter(is_active=True).annotate(
            total_volume=Sum(
                'transactions__total_amount',
                filter=Q(transactions__status='COMPLETED', transactions__is_active=True)
            ),
            transaction_count=Count(
                'transactions',
                filter=Q(transactions__status='COMPLETED', transactions__is_active=True)
            ),
            buy_volume=Sum(
                'transactions__total_amount',
                filter=Q(
                    transactions__status='COMPLETED',
                    transactions__transaction_type='BUY',
                    transactions__is_active=True
                )
            ),
            sell_volume=Sum(
                'transactions__total_amount',
                filter=Q(
                    transactions__status='COMPLETED',
                    transactions__transaction_type='SELL',
                    transactions__is_active=True
                )
            ),
            avg_transaction_size=Avg(
                'transactions__total_amount',
                filter=Q(transactions__status='COMPLETED', transactions__is_active=True)
            )
        ).filter(total_volume__isnull=False).order_by('-total_volume')[:limit]

        result = []
        for asset in top_assets:
            buy_vol = asset.buy_volume or 0
            sell_vol = asset.sell_volume or 0

            result.append({
                'id': str(asset.id),
                'name': asset.name,
                'symbol': asset.symbol,
                'asset_type': asset.asset_type,
                'current_price': float(asset.current_price),
                'total_volume': float(asset.total_volume),
                'transaction_count': asset.transaction_count,
                'buy_volume': float(buy_vol),
                'sell_volume': float(sell_vol),
                'avg_transaction_size': float(asset.avg_transaction_size or 0),
                'volume_balance': float(buy_vol - sell_vol),
                'market_cap': float(asset.market_cap or 0),
                'risk_level': asset.risk_level
            })

        return result

    except Exception as e:
        logger.error(f"Error in get_top_assets_by_volume: {str(e)}")
        return []


def get_transaction_trends(start_date, end_date):
    """
    Get transaction trends by type with enhanced metrics

    Args:
        start_date (datetime): Start date for analysis
        end_date (datetime): End date for analysis

    Returns:
        list: Transaction trends data
    """
    try:
        trends = Transaction.objects.filter(
            transaction_date__range=[start_date, end_date],
            status='COMPLETED',
            is_active=True
        ).values('transaction_type').annotate(
            count=Count('id'),
            total_volume=Sum('total_amount'),
            avg_amount=Avg('total_amount'),
            avg_quantity=Avg('quantity'),
            total_fees=Sum('fees'),
            unique_users=Count('user', distinct=True),
            unique_assets=Count('asset', distinct=True)
        ).order_by('-total_volume')

        # Convert to proper format
        result = []
        for item in trends:
            result.append({
                'transaction_type': item['transaction_type'],
                'count': item['count'],
                'total_volume': float(item['total_volume'] or 0),
                'avg_amount': float(item['avg_amount'] or 0),
                'avg_quantity': float(item['avg_quantity'] or 0),
                'total_fees': float(item['total_fees'] or 0),
                'unique_users': item['unique_users'],
                'unique_assets': item['unique_assets'],
                'avg_volume_per_user': float((item['total_volume'] or 0) / item['unique_users']) if item[
                                                                                                        'unique_users'] > 0 else 0
            })

        return result

    except Exception as e:
        logger.error(f"Error in get_transaction_trends: {str(e)}")
        return []


def get_user_growth_data(start_date, end_date):
    """
    Get user registration growth over time with cumulative tracking

    Args:
        start_date (datetime): Start date for analysis
        end_date (datetime): End date for analysis

    Returns:
        list: User growth data by date
    """
    try:
        # Get daily user registrations
        users_by_date = User.objects.filter(
            date_joined__range=[start_date, end_date],
            is_active=True
        ).extra(
            select={'date': 'DATE(date_joined)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # Calculate cumulative growth
        total_users_before = User.objects.filter(
            date_joined__lt=start_date,
            is_active=True
        ).count()

        growth_data = []
        cumulative_total = total_users_before

        # Create a date-indexed dictionary for easy lookup
        registration_dict = {item['date']: item['count'] for item in users_by_date}

        # Fill in all dates in the range
        current_date = start_date.date()
        end_date_only = end_date.date()

        while current_date <= end_date_only:
            daily_count = registration_dict.get(current_date, 0)
            cumulative_total += daily_count

            growth_data.append({
                'date': current_date.isoformat(),
                'new_users': daily_count,
                'total_users': cumulative_total,
                'growth_rate': (daily_count / cumulative_total * 100) if cumulative_total > 0 else 0
            })

            current_date += timedelta(days=1)

        return growth_data

    except Exception as e:
        logger.error(f"Error in get_user_growth_data: {str(e)}")
        return []


def get_market_overview():
    """
    Get comprehensive market overview statistics

    Returns:
        dict: Market overview data
    """
    try:
        # Asset statistics
        asset_stats = Asset.objects.filter(is_active=True).aggregate(
            total_assets=Count('id'),
            total_market_cap=Sum('market_cap'),
            avg_price=Avg('current_price'),
            min_price=Min('current_price'),
            max_price=Max('current_price')
        )

        # Transaction statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        transaction_stats = Transaction.objects.filter(
            status='COMPLETED',
            is_active=True
        ).aggregate(
            total_transactions=Count('id'),
            total_volume=Sum('total_amount'),
            avg_transaction_size=Avg('total_amount')
        )

        # Recent activity
        recent_activity = {
            'today': Transaction.objects.filter(
                transaction_date__date=today,
                status='COMPLETED',
                is_active=True
            ).count(),
            'this_week': Transaction.objects.filter(
                transaction_date__date__gte=week_ago,
                status='COMPLETED',
                is_active=True
            ).count(),
            'this_month': Transaction.objects.filter(
                transaction_date__date__gte=month_ago,
                status='COMPLETED',
                is_active=True
            ).count()
        }

        return {
            'asset_statistics': {
                'total_assets': asset_stats['total_assets'],
                'total_market_cap': float(asset_stats['total_market_cap'] or 0),
                'avg_price': float(asset_stats['avg_price'] or 0),
                'price_range': {
                    'min': float(asset_stats['min_price'] or 0),
                    'max': float(asset_stats['max_price'] or 0)
                }
            },
            'transaction_statistics': {
                'total_transactions': transaction_stats['total_transactions'],
                'total_volume': float(transaction_stats['total_volume'] or 0),
                'avg_transaction_size': float(transaction_stats['avg_transaction_size'] or 0)
            },
            'recent_activity': recent_activity,
            'generated_at': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in get_market_overview: {str(e)}")
        return {}
