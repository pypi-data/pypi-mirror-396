from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.utils import timezone

from pwyw.models import BalanceTransaction, Subscription
from pwyw.utils import (
    build_payment_reference,
    build_epc_payload,
    charge_user_for_period,
    get_users_with_imminent_negative_balance,
)

User = get_user_model()


def test_build_payment_reference():
    user = User(username="john_doe", email="john@example.com", id=123)
    reference = build_payment_reference(user)

    assert reference == "PWYW john_doe"


def test_build_payment_reference_with_none_user():
    with pytest.raises(AssertionError):
        build_payment_reference(None)  # noqa


def test_build_epc_payload_minimal():
    payload = build_epc_payload(amount=Decimal("12.34"))
    expected_payload = (
        "BCD\n002\n2\nSCT\n\nChristian Gonzalez\nAT012345678901234567\nEUR12.34\n\n\n"
    )
    assert payload == expected_payload


def test_build_epc_payload_full():
    payload = build_epc_payload(
        amount=Decimal("100.50"),
        purpose="Donation",
        name="Test User",
        iban="DE12345678901234567890",
        bic="TESTBIC",
        currency="USD",
    )
    expected_payload = (
        "BCD\n"
        "002\n"
        "2\n"
        "SCT\n"
        "TESTBIC\n"
        "Test User\n"
        "DE12345678901234567890\n"
        "USD100.50\n"
        "\n"
        "Donation\n"
    )
    assert payload == expected_payload


def test_build_epc_payload_invalid_amount():
    with pytest.raises(ValueError):
        build_epc_payload(amount=Decimal("-1.00"))


# --- charge_user_for_period tests ---


@pytest.mark.django_db
def test_charge_user_for_period_creates_debit_transaction():
    user = User.objects.create(username="alice")
    Subscription.objects.create(user=user, amount=Decimal("12.34"))

    res = charge_user_for_period(user)

    assert res is True
    tx = BalanceTransaction.objects.get(user=user)
    assert tx.amount == Decimal("-12.34")
    # Choices use human-readable labels; stored value is the key
    assert tx.type == BalanceTransaction.TypeChoices.TYPE_DEBIT
    assert tx.approved is True
    assert "Subscription charge" in tx.note


@pytest.mark.django_db
def test_charge_user_for_period_no_subscription_returns_false():
    user = User.objects.create(username="bob")

    res = charge_user_for_period(user)

    assert res is False
    assert BalanceTransaction.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_charge_user_for_period_inactive_subscription_returns_false():
    user = User.objects.create(username="charlie")

    # Create an expired subscription (inactive)
    Subscription.objects.create(
        user=user,
        amount=Decimal("10.00"),
        expired_at=timezone.now() - timezone.timedelta(days=1),
    )

    res = charge_user_for_period(user)

    assert res is False
    assert BalanceTransaction.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_charge_user_for_period_anonymous_or_none_returns_false():
    assert charge_user_for_period(None) is False
    assert charge_user_for_period(AnonymousUser()) is False


@pytest.mark.django_db
def test_charge_user_for_period_allows_negative_balance():
    user = User.objects.create(username="erin")
    # Deposit 5.00 first
    BalanceTransaction.objects.create(
        user=user,
        amount=Decimal("5.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
        note="Initial deposit",
    )
    # Subscription of 10.00 should result in balance -5.00 after charge
    Subscription.objects.create(user=user, amount=Decimal("10.00"))

    assert charge_user_for_period(user) is True

    balance = BalanceTransaction.balance_for(user)
    assert balance == Decimal("-5.00")


@pytest.mark.django_db
def test_charge_user_for_period_error_handling(monkeypatch):
    user = User.objects.create(username="frank")
    Subscription.objects.create(user=user, amount=Decimal("3.50"))

    def boom(*args, **kwargs):
        raise RuntimeError("DB error")

    monkeypatch.setattr(BalanceTransaction.objects, "create", boom)

    res = charge_user_for_period(user)

    assert res is False
    # No transaction should have been created
    assert BalanceTransaction.objects.filter(user=user).count() == 0


# --- get_users_with_imminent_negative_balance tests ---


@pytest.mark.django_db
def test_imminent_negative_balance_user_below_amount_is_included():
    user = User.objects.create(username="gina")
    # Balance 5.00, subscription 10.00 -> would become -5.00
    BalanceTransaction.objects.create(
        user=user,
        amount=Decimal("5.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    Subscription.objects.create(user=user, amount=Decimal("10.00"))

    users = get_users_with_imminent_negative_balance()
    assert user in users


@pytest.mark.django_db
def test_imminent_negative_balance_user_with_sufficient_balance_not_included():
    user = User.objects.create(username="hank")
    BalanceTransaction.objects.create(
        user=user,
        amount=Decimal("20.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    Subscription.objects.create(user=user, amount=Decimal("10.00"))

    users = get_users_with_imminent_negative_balance()
    assert user not in users


@pytest.mark.django_db
def test_imminent_negative_balance_exact_balance_equal_amount_not_included():
    user = User.objects.create(username="irene")
    BalanceTransaction.objects.create(
        user=user,
        amount=Decimal("10.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    Subscription.objects.create(user=user, amount=Decimal("10.00"))

    users = get_users_with_imminent_negative_balance()
    assert user not in users


@pytest.mark.django_db
@pytest.mark.skipif(
    connection.vendor == "sqlite",
    reason="SQLite generated columns using Now()/strftime are non-deterministic and not supported in RETURNING; skip on sqlite",
)
def test_imminent_negative_balance_inactive_subscription_not_included():
    user = User.objects.create(username="jane")
    BalanceTransaction.objects.create(
        user=user,
        amount=Decimal("1.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    # Create the subscription already expired to avoid SQLite generated column
    # limitations when updating fields with RETURNING clauses.
    from django.utils import timezone

    sub = Subscription.objects.create(
        user=user,
        amount=Decimal("10.00"),
        expired_at=timezone.now() - timezone.timedelta(days=1),
    )

    users = get_users_with_imminent_negative_balance()
    assert user not in users


@pytest.mark.django_db
def test_imminent_negative_balance_multiple_users_only_negatives_returned():
    u1 = User.objects.create(username="lisa")  # will be included (5 < 10)
    BalanceTransaction.objects.create(
        user=u1,
        amount=Decimal("5.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    Subscription.objects.create(user=u1, amount=Decimal("10.00"))

    u2 = User.objects.create(username="mike")  # excluded (20 >= 10)
    BalanceTransaction.objects.create(
        user=u2,
        amount=Decimal("20.00"),
        type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
        approved=True,
    )
    Subscription.objects.create(user=u2, amount=Decimal("10.00"))

    u3 = User.objects.create(username="nina")  # excluded (no subscription)

    users = get_users_with_imminent_negative_balance()
    assert set(users) == {u1}
