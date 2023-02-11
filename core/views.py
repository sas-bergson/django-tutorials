from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .models import Item, Order, OrderItem


""" def item_list(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "index.html", context) """


class item_list_view(ListView):
    model = Item
    paginate_by = 1
    template_name = "index.html"


class order_summary_view(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(request=self.request,
                          template_name='order_summary.html',
                          context={'object': order})
        except ObjectDoesNotExist:
            messages.error(request=self.request, message='You do not have an active cart at the moment')
            return redirect("/")


""" def item_details(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "item_details.html", context) """


class item_detail_view(DetailView):
    model = Item
    template_name = "item_details.html"


def checkout(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "checkout.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f"This item quantity was updated to {order_item.quantity} in your cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
    else:
        order = Order.objects.create(user=request.user, ordered_date=timezone.now())
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")
    return redirect("core:item", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            # order.items.remove(order_item)
            if (order_item.quantity > 1):
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f"This item quantity was updated to {order_item.quantity} in your cart")
            else:
                order_item.delete()
                messages.info(request, "This item was removed from your cart")
            return redirect("core:item", slug=slug)
        else:
            # add a message saying the order does not contain this order item
            messages.info(request, "This item is not in your cart")
            return redirect("core:item", slug=slug)
    else:
        # add a message saying the user does not have an order
        messages.info(request, "Your cart is empty for now")
        return redirect("core:item", slug=slug)
