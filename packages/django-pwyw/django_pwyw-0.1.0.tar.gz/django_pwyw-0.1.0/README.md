# django-pwyw

Pay‑what‑you‑want (PWYW) utilities for Django projects. This app provides models and helpers to let your users choose their own price, maintain balance transactions, and manage recurring subscriptions with flexible billing periods.

## Features

- Price suggestions you can display in your UI (`PriceSuggestion`)
- Simple user subscription model with daily/weekly/monthly/quarterly/yearly billing (`Subscription`)
- Balance transactions with deposits, debits and adjustments (`BalanceTransaction`)
- Sensible defaults and i18n labels via Django’s translation utilities

## Quick start

1) Install

```
pip install django-pwyw
```

If you are working from source, install the project in editable mode:

```
pip install -e .
```

2) Add to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    # ...
    "pwyw",
]
```

3) Apply migrations

```
python manage.py makemigrations
python manage.py migrate
```

4) Optional settings

- `PWYW_CURRENCY` — currency code used in string representations (default: `"EUR"`).

Add to your Django settings if you want to override the default:

```python
PWYW_CURRENCY = "USD"
```

## Usage overview

### Price suggestions

```python
from pwyw.models import PriceSuggestion

# Pre-populate a few suggestions to show in your UI
PriceSuggestion.objects.bulk_create([
    PriceSuggestion(label="Minimum", amount="5.00", sort_order=10),
    PriceSuggestion(label="Recommended", amount="12.00", sort_order=20),
    PriceSuggestion(label="Supporter", amount="20.00", sort_order=30),
])

active = PriceSuggestion.objects.filter(is_active=True).order_by("sort_order", "amount")
```

### Subscriptions

```python
from decimal import Decimal
from django.contrib.auth import get_user_model
from pwyw.models import Subscription

User = get_user_model()
user = User.objects.first()

sub = Subscription.objects.create(
    user=user,
    amount=Decimal("10.00"),
    billing_period=Subscription.BillingPeriodChoices.MONTHLY,
)

# Read-only generated field for active status (computed from `expired_at`)
sub.is_active  # True/False
```

Subscriptions enforce `amount != 0` and will expire any previous open subscription for the same user when saving a new one.

### Balance transactions

```python
from decimal import Decimal
from pwyw.models import BalanceTransaction

txn = BalanceTransaction.objects.create(
    user=user,
    amount=Decimal("25.00"),
    type=BalanceTransaction.TypeChoices.TYPE_DEPOSIT,
    approved=True,
    note="Initial top-up",
)

current = BalanceTransaction.balance_for(user)
```

## Demo & docs

- Demo templates live under `demo/` and may help you scaffold a simple dashboard.
- Developer docs are in `docs/` (see `mkdocs.yml`). If you use MkDocs, you can preview docs locally with:

```
pip install mkdocs
mkdocs serve
```

## Development

Clone the repo and set up a virtual environment. Then:

```
pip install -e .[dev]
```

Run tests with pytest:

```
pytest -q
```

Run type checks (if you use mypy and django-stubs):

```
mypy
```

## Project layout

- `src/pwyw/` — Django app code (models, forms, utils, URLs)
- `tests/` — test suite (pytest)
- `docs/` — documentation source (MkDocs)
- `demo/` — demo assets/templates
- `Changelog.md` — release notes
- `TODO.md` — rough roadmap/ideas

## Changelog

See `Changelog.md` for notable changes between versions.

## Compatibility

- Python 3.12+
- Django 5.x (and Django ORM features like `GeneratedField`)

## Contributing

Issues and pull requests are welcome. Please include tests for any behavior changes.
Use [black](https://black.readthedocs.io) for formatting the code.
