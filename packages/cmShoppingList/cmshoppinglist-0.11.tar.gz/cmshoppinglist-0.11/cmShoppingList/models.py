"""Models."""

from django.db import models


class General(models.Model):
    """A meta model for app permissions."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
                ("basic_access", "Can access application")
        ]
        verbose_name = ("cmShoppingList")

class MarketType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        default_permissions = ()


class ItemEquivalence(models.Model):
    """Maps original items to their equivalent items."""
    original_item = models.ForeignKey(
        MarketType,
        on_delete=models.CASCADE,
        related_name='equivalent_items'
    )
    equivalent_item = models.ForeignKey(
        MarketType,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        default_permissions = ()
        unique_together = ('original_item', 'equivalent_item')


