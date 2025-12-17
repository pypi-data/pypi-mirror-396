import qrcode
import base64

from io import BytesIO
from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import Sum, Q, Value, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext as _

from .models import BalanceTransaction


def format_amount(amount: Decimal) -> str:
    # Return as a 2-decimal string with dot
    return f"{amount:.2f}"


def build_payment_reference(user: AbstractBaseUser) -> str:
    assert user is not None, _("User must be provided to build payment reference")
    assert user is not AnonymousUser, _("Anonymous users are not supported")
    template = getattr(settings, "PWYW_PAYMENT_REFERENCE_TEMPLATE", "PWYW {username}")
    return template.format(
        username=getattr(user, "username", "user"),
        email=getattr(user, "email", ""),
        id=getattr(user, "id", ""),
    )


def build_epc_payload(
    amount: Decimal,
    purpose: Optional[str] = None,
    name: Optional[str] = None,
    iban: Optional[str] = None,
    bic: Optional[str] = None,
    currency: Optional[str] = None,
) -> str:
    if amount < Decimal("0.00"):
        raise ValueError(_("Amount must be non-negative"))
    name = name or getattr(settings, "PWYW_RECIPIENT_NAME")
    iban = iban or getattr(settings, "PWYW_RECIPIENT_IBAN")
    bic = bic or getattr(settings, "PWYW_RECIPIENT_BIC", "")
    currency = currency or getattr(settings, "PWYW_CURRENCY", "EUR")
    # EPC QR Code (SCT) format
    lines = [
        "BCD",  # Service Tag
        "002",  # Version
        "2",  # encoding
        "SCT",  # Service Identification: SEPA Credit Transfer
        bic or "",
        name or "",
        iban or "",
        f"{currency}{format_amount(amount)}",
        "",  # optional: Purpose Code
        purpose or "",  # Remittance Information (unstructured)
        "",  # optional: Information
    ]
    return "\n".join(lines)


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


def _qr_data_uri(payload: str, size: int = 240) -> str:
    # Build QR image locally using qrcode + Pillow and return as data URI (PNG)
    qr = qrcode.QRCode(
        version=None,  # let library determine the best fit
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # Ensure target size
    if size and hasattr(img, "resize"):
        img = img.resize((size, size))
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def qr_image_url_for_amount(amount: Decimal, user) -> str:
    # Kept name for template compatibility; now returns a data URI
    purpose = build_payment_reference(user)
    payload = build_epc_payload(amount, purpose)
    size = int(getattr(settings, "PWYW_QR_SIZE", 240))
    return _qr_data_uri(payload, size)


def get_users_with_imminent_charge() -> list[AbstractBaseUser]:
    return list(
        BalanceTransaction.objects.filter(
            type=BalanceTransaction.TypeChoices.TYPE_DEBIT,
            approved=True,
            due_date__lte=timezone.now(),
        ).values_list("user", flat=True)
    )


def get_users_with_imminent_negative_balance() -> list[AbstractBaseUser]:
    """Return users that would go negative if charged their subscription now.

    Logic:
    - Consider only active subscriptions with amount > 0.00.
      Active = not expired yet (expired_at is null or in the future).
    - Compute each user's current approved balance (sum of approved transactions).
    - Include those where balance < subscription amount (i.e., balance - amount < 0).
    - Return a list of user instances.
    """
    try:
        # Late import to avoid circulars and keep utils lightweight
        from .models import Subscription  # local import

        # Active subscriptions with positive amount
        subs = (
            Subscription.objects.filter(amount__gte=Decimal("0.00"))
            .filter(Q(expired_at__isnull=True) | Q(expired_at__gt=timezone.now()))
            .select_related("user")
            .annotate(
                balance=Coalesce(
                    Sum(
                        "user__pwyw_transactions__amount",
                        filter=Q(user__pwyw_transactions__approved=True),
                        output_field=DecimalField(max_digits=10, decimal_places=2),
                    ),
                    Value(Decimal("0.00")),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                )
            )
            .filter(balance__lt=F("amount"))
        )
        return [s.user for s in subs]
    except Exception:
        # As a utility, fail-safe by returning empty list on any unexpected error
        return []


def charge_user_for_period(user: AbstractBaseUser) -> bool:
    """Charges a user with his chosen amount.

    This function should be called in the configured time period (
    BillingPeriodChoices), e.g. using a cron job.

    Returns:
        True if a charge was made, False otherwise.
    """
    # As specified: silently continue on any error and return False
    try:
        if user is None or user is AnonymousUser:
            # TODO: log?
            return False

        # Resolve user's current subscription. The relation is one-to-many,
        # and older subscriptions are auto-expired when a new one is created.
        from .models import Subscription  # local import to avoid circulars

        sub = (
            Subscription.objects.filter(user=user)
            .order_by("-created_at", "-id")
            .first()
        )
        if sub is None:
            return False
        # Only charge active subscriptions with a positive amount
        if not sub.is_active:
            return False
        if sub.amount <= Decimal("0.00"):
            return False

        # Create a debit transaction; negative amount decreases balance
        with transaction.atomic():
            BalanceTransaction.objects.create(
                user=user,
                amount=-sub.amount,
                type=BalanceTransaction.TypeChoices.TYPE_DEBIT,
                approved=True,
                note=_("Subscription charge"),
            )
        return True
    except Exception:
        # Silently ignore any errors as requested
        return False
