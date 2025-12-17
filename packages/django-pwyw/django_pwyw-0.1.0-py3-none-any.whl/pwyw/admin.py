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


from django.contrib import admin

from .models import PriceSuggestion, Subscription, BalanceTransaction


@admin.register(PriceSuggestion)
class SuggestedPriceAdmin(admin.ModelAdmin):
    list_display = ("label", "amount", "is_active", "sort_order")
    list_editable = ("amount", "is_active", "sort_order")
    search_fields = ("label",)
    list_filter = ("is_active",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "is_active", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")


@admin.register(BalanceTransaction)
class BalanceTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "type", "approved", "created_at", "note")
    list_filter = ("type", "approved")
    search_fields = ("user__username", "user__email", "note")
    autocomplete_fields = ("user",)
