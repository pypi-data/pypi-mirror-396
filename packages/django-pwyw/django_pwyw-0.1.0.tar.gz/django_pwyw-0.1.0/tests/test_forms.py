import pytest
from decimal import Decimal
from pwyw.forms import DepositForm, PriceSelectionForm


@pytest.mark.django_db
def test_deposit_form_valid_amount():
    form = DepositForm({"amount": "100.00"})
    assert form.is_valid() is True


@pytest.mark.django_db
def test_deposit_form_invalid_amount_no_value():
    form = DepositForm({})
    assert form.is_valid() is False
    assert "amount" in form.errors


@pytest.mark.django_db
def test_deposit_form_invalid_amount_negative_value():
    form = DepositForm({"amount": "-10.00"})
    assert form.is_valid() is False
    assert "amount" in form.errors
    assert (
        form.errors["amount"][0]
        == "Ensure this value is greater than or equal to 0.00."
    )


@pytest.mark.django_db
def test_deposit_form_invalid_amount_exceeds_max_digits():
    form = DepositForm({"amount": "123456789.12"})
    assert form.is_valid() is False
    assert "amount" in form.errors


# --- PriceSelectionForm tests ---


@pytest.mark.django_db
def test_price_selection_form_hides_suggested_without_suggestions():
    form = PriceSelectionForm()
    assert "suggested" not in form.fields


@pytest.mark.django_db
def test_price_selection_form_initializes_with_suggestions():
    suggestions = [("10.00", "Ten"), ("20.00", "Twenty")]
    form = PriceSelectionForm(suggestions=suggestions)
    # suggested field should exist and have an empty choice first
    assert "suggested" in form.fields
    choices = list(form.fields["suggested"].widget.choices)
    assert len(choices) == len(suggestions) + 1
    assert choices[0][0] == ""  # empty option


@pytest.mark.django_db
def test_price_selection_form_valid_with_suggested_sets_price():
    suggestions = [("10.00", "Ten"), ("20.00", "Twenty")]
    form = PriceSelectionForm(
        {"suggested": "10.00", "custom": ""}, suggestions=suggestions
    )
    assert form.is_valid() is True
    assert form.cleaned_data["price"] == Decimal("10.00")


@pytest.mark.django_db
def test_price_selection_form_valid_with_custom_sets_price():
    form = PriceSelectionForm({"custom": "12.34"})
    assert form.is_valid() is True
    assert form.cleaned_data["price"] == Decimal("12.34")


@pytest.mark.django_db
def test_price_selection_form_invalid_when_both_empty():
    suggestions = [("10.00", "Ten")]
    form = PriceSelectionForm({}, suggestions=suggestions)
    assert form.is_valid() is False
    # Error is raised as a non-field error
    errors = form.non_field_errors()
    assert errors
    assert "Please select a suggested price or enter a custom price." in errors


@pytest.mark.django_db
def test_price_selection_form_custom_negative_shows_field_error():
    form = PriceSelectionForm({"custom": "-1.00"})
    assert form.is_valid() is False
    assert "custom" in form.errors
    assert (
        form.errors["custom"][0]
        == "Ensure this value is greater than or equal to 0.00."
    )


@pytest.mark.django_db
def test_price_selection_form_quantizes_price_to_two_decimals():
    # Even if input is '10', DecimalField will coerce to two decimals; ensure 'price' is quantized
    form = PriceSelectionForm({"custom": "10"})
    assert form.is_valid() is True
    assert form.cleaned_data["price"] == Decimal("10.00")


@pytest.mark.django_db
def test_price_selection_form_suggested_widget_is_select():
    suggestions = [("10.00", "Ten")]
    form = PriceSelectionForm(suggestions=suggestions)
    from django.forms import Select

    assert isinstance(form.fields["suggested"].widget, Select)
