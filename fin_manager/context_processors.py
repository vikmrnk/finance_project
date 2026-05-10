from datetime import timedelta
from django.utils import timezone

from .models import Subscription


def subscription_notifications(request):
    if not request.user.is_authenticated:
        return {'subscription_alerts_count': 0, 'subscription_alerts': []}

    today = timezone.now().date()
    alerts_qs = Subscription.objects.filter(
        user=request.user,
        next_payment_date__gte=today,
        next_payment_date__lte=today + timedelta(days=7),
    ).order_by('next_payment_date', 'name')

    seen_date = request.session.get('subscription_alerts_seen_on')
    unread_count = 0 if seen_date == today.isoformat() else alerts_qs.count()

    alerts = []
    for item in alerts_qs[:8]:
        alerts.append({
            'name': item.name,
            'amount': item.amount,
            'next_payment_date': item.next_payment_date,
            'days_left': (item.next_payment_date - today).days,
        })

    return {'subscription_alerts_count': unread_count, 'subscription_alerts': alerts}
