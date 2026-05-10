from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
import json

from .models import (
    Account, 
    Transaction, 
    Budget, 
    Category, 
    Liability, 
    Investments, 
    Subscription
)
from .forms import (
    CustomUserCreationForm, 
    UserUpdateForm,
    AccountForm, 
    TransactionForm, 
    BudgetForm, 
    CategoryForm, 
    LiabilityForm, 
    InvestmentForm, 
    SubscriptionForm
)

# Create your views here.

# @login_required(login_url='/signin')

def home(request):
    return render(request, 'fin_manager/home.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default account and categories for the new user
            account = Account.objects.create(
                name=f"{user.username}'s Account", 
                user=user
            )
            
            # Create default expense categories
            default_expense_categories = [
                {'name': 'Food & Dining', 'icon': 'utensils'},
                {'name': 'Transportation', 'icon': 'car'},
                {'name': 'Entertainment', 'icon': 'film'},
                {'name': 'Housing', 'icon': 'home'},
                {'name': 'Utilities', 'icon': 'bolt'},
                {'name': 'Shopping', 'icon': 'shopping-cart'},
                {'name': 'Health', 'icon': 'medkit'},
                {'name': 'Personal', 'icon': 'user'},
            ]
            
            for category in default_expense_categories:
                Category.objects.create(
                    name=category['name'],
                    category_type='expense',
                    icon=category['icon'],
                    user=user
                )
                
            # Create default income categories
            default_income_categories = [
                {'name': 'Salary', 'icon': 'money-bill'},
                {'name': 'Bonus', 'icon': 'gift'},
                {'name': 'Investments', 'icon': 'chart-line'},
                {'name': 'Gifts', 'icon': 'gift'},
                {'name': 'Other', 'icon': 'coins'},
            ]
            
            for category in default_income_categories:
                Category.objects.create(
                    name=category['name'],
                    category_type='income',
                    icon=category['icon'],
                    user=user
                )
                
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Your account has been created with default categories.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required(login_url='/accounts/login/')
def account_settings(request):
    def _style_password_form(form):
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-control'

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)
            _style_password_form(password_form)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profile details were updated successfully.')
                return redirect('account_settings')
        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user, request.POST)
            _style_password_form(password_form)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('account_settings')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
        _style_password_form(password_form)

    return render(
        request,
        'fin_manager/account_settings.html',
        {'user_form': user_form, 'password_form': password_form},
    )


# Dashboard
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class DashboardView(TemplateView):
    template_name = 'fin_manager/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get accounts
        accounts = Account.objects.filter(user=user)
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or 0
        
        # Get recent transactions
        recent_transactions = Transaction.objects.filter(
            user=user
        ).order_by('-date', '-created_at')[:5]
        
        # Calculate monthly income vs expense
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expense = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=month_start
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get active budgets
        active_budgets = Budget.objects.filter(
            user=user,
            start_date__lte=now,
            end_date__gte=now.date() if now else None
        ).order_by('category__name')
        
        # Prepare budget data with spending percentage
        budget_data = []
        for budget in active_budgets:
            spent = budget.get_spent_amount()
            total = budget.amount
            if total > 0:
                percentage = int((spent / total) * 100)
            else:
                percentage = 0
                
            budget_data.append({
                'id': budget.id,
                'name': budget.name,
                'category': budget.category.name,
                'icon': budget.category.icon,
                'spent': spent,
                'total': total,
                'percentage': percentage,
                'status': 'danger' if percentage > 90 else 'warning' if percentage > 70 else 'success'
            })
        
        # Get upcoming liabilities
        upcoming_liabilities = Liability.objects.filter(
            user=user,
            end_date__gt=now.date(),
        ).order_by('end_date')[:3]
        
        # Get upcoming subscriptions
        upcoming_subscriptions = Subscription.objects.filter(
            user=user,
            next_payment_date__gt=now.date(),
        ).order_by('next_payment_date')[:3]
        
        # Get category spending breakdown
        category_spending = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=month_start
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Prepare data for charts
        expense_by_category = []
        for item in category_spending:
            if item['category__name']:
                expense_by_category.append({
                    'category': item['category__name'],
                    'amount': float(item['total'])
                })
        
        # Last 6 months income vs expense
        months_data = []
        for i in range(5, -1, -1):
            month_date = (now - timedelta(days=30 * i)).replace(day=1)
            month_end = month_date.replace(
                day=28 if month_date.month == 2 and not month_date.year % 4 == 0 
                else 29 if month_date.month == 2 
                else 30 if month_date.month in [4, 6, 9, 11] 
                else 31
            )
            
            month_income = Transaction.objects.filter(
                user=user,
                transaction_type='income',
                date__gte=month_date,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expense = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__gte=month_date,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            months_data.append({
                'month': month_date.strftime('%b %Y'),
                'income': float(month_income),
                'expense': float(month_expense)
            })
        
        context.update({
            'accounts': accounts,
            'total_balance': total_balance,
            'recent_transactions': recent_transactions,
            'monthly_income': monthly_income,
            'monthly_expense': monthly_expense,
            'monthly_savings': monthly_income - monthly_expense,
            'budget_data': budget_data,
            'upcoming_liabilities': upcoming_liabilities,
            'upcoming_subscriptions': upcoming_subscriptions,
            'expense_by_category': json.dumps(expense_by_category),
            'months_data': json.dumps(months_data)
        })
        
        return context

# Account views
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AccountListView(ListView):
    model = Account
    template_name = 'fin_manager/accounts/account_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AccountForm()
        return context

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'fin_manager/accounts/account_form.html'
    success_url = reverse_lazy('accounts')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AccountDetailView(DetailView):
    model = Account
    template_name = 'fin_manager/accounts/account_detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.object
        
        # Get recent transactions for this account
        recent_transactions = Transaction.objects.filter(
            account=account
        ).order_by('-date', '-created_at')[:10]
        
        context['recent_transactions'] = recent_transactions
        context['transaction_form'] = TransactionForm(user=self.request.user)
        
        return context

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'fin_manager/accounts/account_form.html'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('account_detail', kwargs={'pk': self.object.pk})

# Transaction views
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransactionListView(ListView):
    model = Transaction
    template_name = 'fin_manager/transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by date range if provided
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        # Filter by transaction type if provided
        transaction_type = self.request.GET.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        # Filter by account if provided
        account_id = self.request.GET.get('account')
        if account_id:
            queryset = queryset.filter(account_id=account_id)
            
        # Filter by category if provided
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by search term if provided
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(amount__icontains=search)
            )
            
        return queryset.order_by('-date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = Account.objects.filter(user=self.request.user)
        context['categories'] = Category.objects.filter(user=self.request.user)
        context['form'] = TransactionForm(user=self.request.user)
        
        # Add filters to context
        context['filters'] = {
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
            'type': self.request.GET.get('type', ''),
            'account': self.request.GET.get('account', ''),
            'category': self.request.GET.get('category', ''),
            'search': self.request.GET.get('search', '')
        }
        
        return context

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'fin_manager/transactions/transaction_form.html'
    success_url = reverse_lazy('transactions')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Transaction created successfully!')
        return response

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'fin_manager/transactions/transaction_form.html'
    success_url = reverse_lazy('transactions')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Transaction updated successfully!')
        return response

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'fin_manager/transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Transaction deleted successfully!')
        return response

# Budget views
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class BudgetListView(ListView):
    model = Budget
    template_name = 'fin_manager/budgets/budget_list.html'
    context_object_name = 'budgets'
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budget_data = []
        
        for budget in context['budgets']:
            spent = budget.get_spent_amount()
            total = budget.amount
            if total > 0:
                percentage = int((spent / total) * 100)
            else:
                percentage = 0
                
            budget_data.append({
                'budget': budget,
                'spent': spent,
                'remaining': budget.get_remaining_amount(),
                'percentage': percentage,
                'status': 'danger' if percentage > 90 else 'warning' if percentage > 70 else 'success'
            })
        
        context['budget_data'] = budget_data
        context['form'] = BudgetForm(user=self.request.user)
        return context

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class BudgetCreateView(CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'fin_manager/budgets/budget_form.html'
    success_url = reverse_lazy('budgets')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class BudgetUpdateView(UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'fin_manager/budgets/budget_form.html'
    success_url = reverse_lazy('budgets')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class BudgetDeleteView(DeleteView):
    model = Budget
    template_name = 'fin_manager/budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budgets')
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

# Category views
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = 'fin_manager/categories/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_categories'] = self.get_queryset().filter(category_type='expense')
        context['income_categories'] = self.get_queryset().filter(category_type='income')
        context['form'] = CategoryForm()
        return context

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'fin_manager/categories/category_form.html'
    success_url = reverse_lazy('categories')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'fin_manager/categories/category_form.html'
    success_url = reverse_lazy('categories')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'fin_manager/categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories')
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

# Analytics view
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class AnalyticsView(TemplateView):
    template_name = 'fin_manager/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get date range from query parameters or use default (last 6 months)
        end_date = timezone.now().date()
        start_date = self.request.GET.get('start_date')
        end_date_param = self.request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=180)
            
        if end_date_param:
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        
        # Get all transactions within date range
        transactions = Transaction.objects.filter(
            user=user, 
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate total income and expense
        total_income = transactions.filter(
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_expense = transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Get income by category
        income_by_category = transactions.filter(
            transaction_type='income'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Get expense by category
        expense_by_category = transactions.filter(
            transaction_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        # Prepare data for charts
        income_categories = []
        income_amounts = []
        for item in income_by_category:
            if item['category__name']:
                income_categories.append(item['category__name'])
                income_amounts.append(float(item['total']))
        
        expense_categories = []
        expense_amounts = []
        for item in expense_by_category:
            if item['category__name']:
                expense_categories.append(item['category__name'])
                expense_amounts.append(float(item['total']))
        
        # Get monthly data
        months = []
        month_income = []
        month_expense = []
        month_savings = []
        
        current_date = start_date.replace(day=1)
        end_of_range = end_date.replace(day=28)
        
        while current_date <= end_of_range:
            month_end = current_date.replace(
                day=28 if current_date.month == 2 and not current_date.year % 4 == 0 
                else 29 if current_date.month == 2 
                else 30 if current_date.month in [4, 6, 9, 11] 
                else 31
            )
            
            month_income_amount = transactions.filter(
                transaction_type='income',
                date__gte=current_date,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            month_expense_amount = transactions.filter(
                transaction_type='expense',
                date__gte=current_date,
                date__lte=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            months.append(current_date.strftime('%b %Y'))
            month_income.append(float(month_income_amount))
            month_expense.append(float(month_expense_amount))
            month_savings.append(float(month_income_amount - month_expense_amount))
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_income': total_income,
            'total_expense': total_expense,
            'total_savings': total_income - total_expense,
            'saving_rate': (total_income - total_expense) / total_income * 100 if total_income > 0 else 0,
            'income_categories': json.dumps(income_categories),
            'income_amounts': json.dumps(income_amounts),
            'expense_categories': json.dumps(expense_categories),
            'expense_amounts': json.dumps(expense_amounts),
            'months': json.dumps(months),
            'month_income': json.dumps(month_income),
            'month_expense': json.dumps(month_expense),
            'month_savings': json.dumps(month_savings),
        })
        
        return context

# Expense list view - Enhanced from the original
@method_decorator(login_required(login_url='/accounts/login/'), name='dispatch')
class ExpenseListView(FormView):
    template_name = 'expenses/expense_list.html'
    form_class = LiabilityForm
    success_url = '/expenses/'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        liability = form.save(commit=False)
        liability.user = self.request.user
        liability.save()
        
        messages.success(self.request, 'Liability added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's liabilities
        liabilities = Liability.objects.filter(user=user).order_by('end_date')
        
        # Create a dictionary to store expense data grouped by month
        expense_data = {}
        
        for liability in liabilities:
            year_month = liability.end_date.strftime('%Y-%m')
            
            if year_month not in expense_data:
                expense_data[year_month] = []
                
            expense_data[year_month].append({
                'id': liability.id,
                'name': liability.name,
                'amount': liability.amount,
                'remaining_amount': liability.remaining_amount,
                'interest_rate': liability.interest_rate,
                'end_date': liability.end_date,
                'account': liability.account.name if liability.account else 'No Account',
                'liability_type': liability.get_liability_type_display(),
            })
        
        context['expense_data'] = expense_data
        return context
