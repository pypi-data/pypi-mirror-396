"""Routes."""

from django.urls import path

from . import views

app_name = "cmShoppingList"

urlpatterns = [
    path("", views.index, name="index"),
    path("GetMarketTypes", views.get_market_types),
    path("GetItemEquivalences", views.get_item_equivalences)
]
