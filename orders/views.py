from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreationForm
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreationForm(request.POST)
        
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

            # Clear the cart
            cart.clear()

            template = 'orders/order/created.html'
            context = {'order': order}
            return render(request, template, context)
    else:
        form = OrderCreationForm()
        template = 'orders/order/create.html'
        context = { 'cart': cart, 'form':form }
        
        return render(request, template, context)
