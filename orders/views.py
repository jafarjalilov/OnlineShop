from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from weasyprint import HTML, CSS
from .forms import OrderCreationForm
from .models import OrderItem, Order
from .tasks import order_created
from cart.cart import Cart

def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreationForm(request.POST)
        
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])

            # Clearing the cart
            cart.clear()
            # Lounching asynchronous task
            order_created.delay(order.id)

            # set the order in the session
            request.session['order_id'] = order.id
            #  redirect for payment
            return redirect(reverse('payment:process'))

            
            # template = 'orders/order/created.html'
            # context = {'order': order}
            # return render(request, template, context)
    else:
        form = OrderCreationForm()
        template = 'orders/order/create.html'
        context = { 'cart': cart, 'form':form }
        
        return render(request, template, context)
    
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    template = 'admin/orders/order/detail.html'
    context = {'order': order}

    return render(request, template, context)

@staff_member_required
def  admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'

    HTML(string=html).write_pdf(response, stylesheets=[CSS(settings.STATIC_ROOT + 'css/pdf.css')])
    return response
    
