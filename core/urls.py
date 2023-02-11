from django.urls import path
from .views import (
    item_list_view,
    item_detail_view,
    order_summary_view,
    checkout,
    add_to_cart,
    remove_from_cart,
)

app_name = 'core'

urlpatterns = [
    path('', item_list_view.as_view(), name='index'),
    path('home/', item_list_view.as_view(), name='index'),
    path('items/', item_list_view.as_view(), name='items'),
    path('order-summary/', order_summary_view.as_view(), name='order-summary'),
    path('item/<slug>/', item_detail_view.as_view(), name='item'),
    path('checkout/', checkout, name='checkout'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart')
]
