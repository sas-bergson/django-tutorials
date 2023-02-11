from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from lorem_text import lorem


CATEGORY_CHOICES = (
    ('S', 'shirt'),
    ('SW', 'sport wear'),
    ('OW', 'outwear')
)

BADGES_CHOICES = (
    ('E', 'eco'),
    ('B', 'bestSeller'),
    ('N', 'new'),
    ('D', 'discount')
)


class Item(models.Model):
    ''' This is represents the items that you can purchase in the Shop '''

    title = models.CharField(_("title of item in store"), max_length=50)
    price = models.FloatField(_("price of item in store"), default=0.0)
    discount = models.FloatField(_("discount price of item in store"), blank=True, null=True)
    category = models.CharField(_("category of item in store"),
                                choices=CATEGORY_CHOICES, max_length=2,
                                default='S')
    badge = models.CharField(_("label of item in store"),
                             choices=BADGES_CHOICES, max_length=1,
                             default='N')
    slug = models.SlugField(_("slug of item in store"), default="new_product")
    description = models.TextField(_("description of item in store"), default=lorem.paragraph())

    def __str__(self) -> str:
        return self.title

    def discount_price(self) -> float:
        if self.discount is not None:
            return self.discount
        return 0.0

    def get_absolute_url(self) -> str:
        return reverse("core:item", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self) -> str:
        return reverse("core:add-to-cart", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self) -> str:
        return reverse("core:remove-from-cart", kwargs={"slug": self.slug})


class OrderItem(models.Model):
    ''' This represents one of the items added to Cart '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name=_("user who added the item the order"),
                             default=User.objects.get(username="admin").pk)
    ordered = models.BooleanField(_("checked if item is part of an order that is checked out"),
                                  default=False)
    item = models.ForeignKey(Item,
                             on_delete=models.CASCADE,
                             verbose_name=_("item selected in the store"))
    quantity = models.IntegerField(_("quantity of item in cart"), default=1)

    def get_total_item_price(self) -> float:
        return self.quantity * self.item.price

    def get_total_item_discount_price(self) -> float:
        return self.quantity * self.item.discount_price()
    
    def get_amount_saved(self) -> float:
        return self.quantity * self.item.discount_price()

    def __str__(self) -> str:
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    ''' This links all the order items to an Order '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name=_("user who created the order"))
    items = models.ManyToManyField(OrderItem,
                                   verbose_name=_("items added to cart"))
    start_date = models.DateTimeField(_("moment the order was created"),
                                      auto_now=True)
    ordered_date = models.DateTimeField(_("moment the order is checked out"),
                                        auto_now=False, auto_now_add=False)
    ordered = models.BooleanField(_("checked if order is completed and checked out"),
                                  default=False)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.start_date}"
