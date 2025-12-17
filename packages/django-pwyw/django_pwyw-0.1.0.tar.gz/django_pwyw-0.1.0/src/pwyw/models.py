from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import TextChoices, QuerySet
from django.db.models import Q
from django.utils.translation import gettext as _
from django.utils import timezone

# Django-PayWhatYouWant - a library for free selectable payments
# Copyright (C) 2025 Christian González
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


class PriceSuggestion(models.Model):
    """Stores suggested pricing options for pay-what-you-want products.

    You can subclass this model and add a custom "product" if you want to
    support more than one product.

    Attributes:
        label: Optional descriptive label, like "Minimum price".
        amount: Suggested price amount.
        is_active: Whether this price option is currently active.
        sort_order: Display ordering priority (lower values first).
    """

    label = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "amount"]

    def __str__(self) -> str:  # pragma: no cover - admin/representation
        return f"{self.label or self.amount} ({self.amount} {getattr(settings, 'PWYW_CURRENCY', 'EUR')})"


class SubscriptionQuerySet(models.QuerySet):
    def active(self) -> "Subscription | None":
        """Returns the *one* active subscription, if any, or None"""
        now = timezone.now()
        return self.filter(Q(expired_at__isnull=True) | Q(expired_at__gt=now)).first()

    def inactive(self) -> QuerySet["Subscription"]:
        """Returns all inactive subscriptions, if any, or an empty QuerySet"""
        now = timezone.now()
        return self.exclude(Q(expired_at__isnull=True) | Q(expired_at__gt=now))


class Subscription(models.Model):
    """Manages user subscription payment amounts.

    You can subclass this model and add a custom "product" if you want to
    support more than one product.

    Attributes:
        user: The subscribed user.
        amount: payment amount per period.
    billing_period: Billing period frequency (daily, weekly, monthly, quarterly, yearly).
    active: Whether the subscription is active.
    created_at: Subscription creation timestamp.
    updated_at: Last update timestamp.
    """

    class BillingPeriodChoices(TextChoices):
        """Billing period frequency choices for subscriptions."""

        DAILY = "daily", _("Daily")
        WEEKLY = "weekly", _("Weekly")
        MONTHLY = "monthly", _("Monthly")
        QUARTERLY = "quarterly", _("Quarterly")
        YEARLY = "yearly", _("Yearly")

    # Manager with helpful filters (active/inactive) that work across DBs
    objects = models.Manager.from_queryset(SubscriptionQuerySet)()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pwyw_subscriptions",
    )
    amount = models.DecimalField(
        max_digits=9, decimal_places=2, default=Decimal("0.00")
    )
    billing_period = models.CharField(
        max_length=20,
        choices=BillingPeriodChoices,
        default=BillingPeriodChoices.MONTHLY,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_active(self) -> bool:
        """Whether the subscription is currently active."""
        return (
            self.expired_at is None or self.expired_at > timezone.now()
        ) and self.user.is_active

    def __str__(self) -> str:  # pragma: no cover
        return _("Subscription ({user}, {amount}/{period})").format(
            user=self.user, amount=self.amount, period=self.get_billing_period_display()
        )

    def save(self, *args, **kwargs) -> None:
        if self.amount == 0:
            raise ValueError(_("The amount cannot be zero."))
        # if there is another open subscription for the same user, expire it at the
        # same timestamp THIS Subscription is saved.
        super().save(*args, **kwargs)
        Subscription.objects.filter(user_id=self.user_id).exclude(pk=self.pk).update(
            expired_at=self.created_at
        )


class BalanceTransaction(models.Model):
    """Records balance changes for user accounts.

    Attributes:
        user: The user associated with this transaction.
        created_at: Transaction creation timestamp.
        amount: Transaction amount.
        type: Transaction type (deposit, debit, or adjustment).
        approved: Whether the transaction has been approved.
        note: Optional transaction note.
    """

    TYPE_DEPOSIT = "deposit"
    TYPE_DEBIT = "debit"
    TYPE_ADJUSTMENT = "adjustment"

    class TypeChoices(TextChoices):
        """Transaction type choices for balance operations."""

        TYPE_DEPOSIT = _("Deposit")
        TYPE_DEBIT = _("Debit")
        TYPE_ADJUSTMENT = _("Adjustment")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pwyw_transactions",
    )
    created_at = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TypeChoices)
    approved = models.BooleanField(default=False)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} {self.type} {self.amount} on {self.created_at:%Y-%m-%d}"

    @staticmethod
    def balance_for(user) -> Decimal:
        qs = BalanceTransaction.objects.filter(user=user, approved=True)
        total = qs.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")
        return total
