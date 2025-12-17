SECRET_KEY = "test"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "pwyw",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PWYW_RECIPIENT_NAME = "Christian Gonzalez"
PWYW_RECIPIENT_IBAN = "AT012345678901234567"
