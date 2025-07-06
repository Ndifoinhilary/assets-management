from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet, AssetCategoryViewSet, TransactionViewSet,
    ReportViewSet, AnalyticsViewSet, ListUsersAPIView
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'categories', AssetCategoryViewSet, basename='asset-categories')
router.register(r'assets', AssetViewSet, basename='assets')
router.register(r'transactions', TransactionViewSet, basename='transactions')
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),

    # Additional endpoints can be added here

    path('users/', ListUsersAPIView.as_view()),
]