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


from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from typing import Optional, Any

from django import forms


class PriceSelectionForm(forms.Form):
    suggested = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=2,
        widget=forms.Select,
        label=_("Suggested price"),
    )
    custom = forms.DecimalField(
        required=False,
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0.00"),
        label=_("Custom price"),
    )

    def __init__(
        self, *args, suggestions: list[tuple[str, str]] | None = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        if suggestions:
            self.fields["suggested"].widget.choices = [
                ("", _("— choose —"))
            ] + suggestions
        else:
            # Hide suggested if no suggestions
            self.fields.pop("suggested")

    def clean(self) -> dict[str, Any]:
        cleaned: dict[str, Any] = super().clean() or {}
        suggested: Optional[Decimal] = cleaned.get("suggested")
        custom: Optional[Decimal] = cleaned.get("custom")
        value: Optional[Decimal] = suggested or custom
        if value is None:
            raise forms.ValidationError(
                _("Please select a suggested price or enter a custom price.")
            )
        if value < Decimal("0.00"):
            raise forms.ValidationError(_("Price must be non-negative."))
        cleaned["price"] = value.quantize(Decimal("0.01"))
        return cleaned


class DepositForm(forms.Form):
    amount = forms.DecimalField(
        required=True,
        max_digits=9,
        decimal_places=2,
        min_value=Decimal("0.00"),
        label=_("Deposit amount"),
    )
