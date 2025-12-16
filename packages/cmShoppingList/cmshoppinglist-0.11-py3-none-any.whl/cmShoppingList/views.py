"""Views."""

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.http import JsonResponse

from cmShoppingList import app_settings

from .models import MarketType, ItemEquivalence
from collections import defaultdict

@login_required
@permission_required("cmShoppingList.basic_access")
def index(request):
    """Render index view."""
    context = {
        'CM_VERSION': app_settings.CM_VERSION,
        'HEADER_MESSAGE': app_settings.HEADER_MESSAGE
    }
    return render(request, "cmShoppingList/index.html", context)

@login_required
@permission_required("cmShoppingList.basic_access")
def get_market_types(request):
    items = list(MarketType.objects.all().values())
    return JsonResponse(items, safe=False)

@login_required
@permission_required("cmShoppingList.basic_access")
def get_item_equivalences(request):
    """Return item equivalences as dict mapping original_item_id to list of equivalent_item_ids."""
    equivalences = ItemEquivalence.objects.all().values('original_item_id', 'equivalent_item_id')

    result = defaultdict(list)
    for eq in equivalences:
        result[eq['original_item_id']].append(eq['equivalent_item_id'])

    return JsonResponse(dict(result), safe=False)




