from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from pwyw.models import Subscription

User = get_user_model()


@pytest.mark.django_db
def test_0_subscription_not_possible():
    user = User.objects.create(username="kate")
    with pytest.raises(ValueError):
        Subscription.objects.create(user=user, amount=Decimal("0.00"))


@pytest.mark.django_db
def test_is_active_property_respects_expiry_and_user_state():
    user = User.objects.create(username="anna", is_active=True)

    # No expiry -> active
    sub = Subscription.objects.create(user=user, amount=Decimal("5.00"))
    assert sub.is_active is True

    # Future expiry -> still active
    future = timezone.now() + timezone.timedelta(days=1)
    sub.expired_at = future
    sub.save()
    assert sub.is_active is True

    # Past expiry -> inactive
    past = timezone.now() - timezone.timedelta(days=1)
    sub.expired_at = past
    sub.save()
    assert sub.is_active is False

    # Even with future expiry, deactivating user makes it inactive
    sub.expired_at = None
    sub.save()
    user.is_active = False
    user.save(update_fields=["is_active"])
    assert sub.is_active is False


@pytest.mark.django_db
def test_saving_new_subscription_expires_older_ones_for_same_user():
    user = User.objects.create(username="max")

    first = Subscription.objects.create(user=user, amount=Decimal("3.00"))
    assert first.expired_at is None

    # Create a second subscription for the same user
    before = timezone.now()
    second = Subscription.objects.create(user=user, amount=Decimal("7.50"))

    # Old one should be expired; new one active
    first.refresh_from_db()
    second.refresh_from_db()

    assert second.expired_at is None
    assert first.expired_at is not None
    # Expiry should be at or after the time we created the second one
    assert first.expired_at >= before

    # Creating a third one should expire all previous ones, but not affect others' users
    other_user = User.objects.create(username="sue")
    other_sub = Subscription.objects.create(user=other_user, amount=Decimal("9.99"))

    third = Subscription.objects.create(user=user, amount=Decimal("2.00"))

    first.refresh_from_db()
    second.refresh_from_db()
    other_sub.refresh_from_db()
    third.refresh_from_db()

    assert third.expired_at is None
    assert first.expired_at is not None and first.expired_at <= timezone.now()
    assert second.expired_at is not None and second.expired_at <= timezone.now()
    # Other user's subscription remains untouched
    assert other_sub.expired_at is None
