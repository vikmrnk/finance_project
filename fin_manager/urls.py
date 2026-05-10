#from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('settings/', views.account_settings, name='account_settings'),
    
    # Account URLs
    path('accounts/', views.AccountListView.as_view(), name='accounts'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
    path('accounts/<int:pk>/update/', views.AccountUpdateView.as_view(), name='account_update'),
    
    # Transaction URLs
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/update/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    # Budget URLs
    path('budgets/', views.BudgetListView.as_view(), name='budgets'),
    path('budgets/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Analytics URL
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('subscriptions/', views.subscriptions_center, name='subscriptions'),
    path('notifications/subscriptions/read/', views.mark_subscription_notifications_read, name='notifications_subscriptions_read'),
    
    # Legacy URLs
    path('expenses/', views.ExpenseListView.as_view(), name='expenses'),
]
