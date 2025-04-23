from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Sum

class Category(models.Model):
    CATEGORY_TYPES = (
        ('expense', 'Expense'),
        ('income', 'Income'),
    )
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'


class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit', 'Credit Card'),
        ('investment', 'Investment Account'),
        ('cash', 'Cash'),
    )
    
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='checking')
    currency = models.CharField(max_length=3, default='USD')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    saving_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    def update_balance(self):
        income = Transaction.objects.filter(
            account=self, 
            transaction_type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        expense = Transaction.objects.filter(
            account=self, 
            transaction_type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        self.balance = income - expense
        self.save()


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.description} ({self.amount})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.account.update_balance()


class Budget(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} Budget"
    
    def get_spent_amount(self):
        if self.category.category_type != 'expense':
            return 0
            
        transactions = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date or timezone.now().date(),
            transaction_type='expense'
        )
        
        return transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    def get_remaining_amount(self):
        return self.amount - self.get_spent_amount()


class Investments(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='investments', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Investments'


class Liability(models.Model):
    LIABILITY_TYPES = (
        ('loan', 'Loan'),
        ('credit', 'Credit Card'),
        ('mortgage', 'Mortgage'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    liability_type = models.CharField(max_length=20, choices=LIABILITY_TYPES, default='other')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='liabilities', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Liabilities'


class Subscription(models.Model):
    FREQUENCY_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
    )
    
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    next_payment_date = models.DateField(default=timezone.now)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='subscriptions', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name
