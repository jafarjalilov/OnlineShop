import braintree
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from orders.models import Order
from .tasks import payment_completed

# INSTSTANTIATING BRAINTREE PAYMENT GATEWAY
gateway = braintree.BraintreeGateway(settings.BRAINTREE_CONF)


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    total_cost = order.get_total_cost()

    if request.method == 'POST':
        # RETRIEVING NONCE
        nonce = request.POST.get('payment_method_nonce', None)

        # CREATING AND SUBMITTING THE TRANSACTION
        result = gateway.transaction.sale({
            'amount': f'{total_cost: .2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })

        if result.is_success:
            # MARKING THE ORDER AS PAID
            order.paid = True

            # STORING THE UNIQUE TRANSACTION ID
            order.braintree_id = result.transaction.id
            order.save()
            # LAUNCHING ASYNCHRANOUS TASKS
            payment_completed.delay(order.id)
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')

    else:
        # GENERATING TOKEN
        client_token = gateway.client_token.generate()
        template = 'payment/process.html'
        context = {
            'order': order,
            'client_token': client_token
        }

        return render(request, template, context)


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_cancelled(request):
    return render(request, 'payment/canceled.html')
