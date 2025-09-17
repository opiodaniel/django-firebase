import json

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from djangofirebase.settings import db
from firebase_admin.firestore import firestore

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.views.decorators.csrf import csrf_exempt

import logging
logger = logging.getLogger(__name__)

def order_list(request):
    """
    Retrieves and displays a paginated, searchable list of all orders from Firestore.
    Supports search by Order ID and filter by type (Express/Maintenance).
    """
    # Get query parameters
    search_query = request.GET.get('search', '').strip()
    filter_type = request.GET.get('type', '').strip()

    # Fetch all orders from Firestore
    orders_ref = db.collection('flashtech-order').where('value', '>', 0)
    docs = orders_ref.stream()
    orders = []

    # Fetch all orders from Firestore, sorted by created_at in descending order
    # query = db.collection('flashtech-order').order_by('created_at', direction=firestore.Query.ASCENDING)
    # Then, get the stream (iterator) from the query.
    # docs = query.stream()

    for doc in docs:
        order_data = doc.to_dict()
        order_data['id'] = doc.id  # Store document ID as 'id'
        orders.append(order_data)

    # Apply search filter (case-insensitive match on Order ID)
    if search_query:
        orders = [
            order for order in orders
            if search_query.lower() in order.get('id', '').lower()
        ]

    # Apply type filter
    if filter_type in ['Express', 'Maintenance']:
        orders = [
            order for order in orders
            if order.get('type') == filter_type
        ]

    # Pagination: 10 orders per page
    paginator = Paginator(orders, 3)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Pass context to template
    context = {
        'orders': page_obj,
        'search_query': search_query,
        'filter_type': filter_type,
    }

    return render(request, 'flashtech/order_list.html', context)


def order_detail(request, order_id):
    order_ref = db.collection('flashtech-order').document(order_id)
    order_doc = order_ref.get()

    if not order_doc.exists:
        return HttpResponseNotFound("Order not found.")

    order_data = order_doc.to_dict()
    order_owner = order_data.get('orderOwner', {})
    order_mechanic = order_data.get('orderMechanic', {})
    mileage = order_data.get('mileage')
    vehicle_name = order_data.get('name')
    vehicle_number_plate = order_data.get('numberPlate')

    # Safely get order and payment data
    order_type = order_data.get('type')
    amount_to_pay = int(order_data.get('value'))
    amount_paid = 0
    balance_remaining = 0
    change = 0

    # New order details dictionary to send
    order_details_for_client = {
        'id': order_id,
        'client_name': order_owner.get('name', '—'),
        'vehicle': f"{order_data.get('name')} ({order_data.get('numberPlate')})",
        'phone': order_owner.get('phone', '—'),
        'amount_due': int(order_data.get('value', 0)),
    }

    # Get the channel layer and send the new message format
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'client_screen_group',
        {
            # Match the consumer method name
            'type': 'send_order_details',
            # Pass the new dictionary
            'order_details': order_details_for_client,
        }
    )
    context = {
        'order_id': order_id,
        'order_mechanic': order_mechanic,
        'order_owner': order_owner,
        'order_type': order_type,
        'amount_to_pay': amount_to_pay,
        'mileage': mileage,
        'vehicle_name': vehicle_name,
        'vehicle_number_plate': vehicle_number_plate,
        'amount_paid': amount_paid,
        'change': change,
    }

    return render(request, 'flashtech/order_detail.html', context)


def record_amount_paid(request, order_id):
    order_ref = db.collection('flashtech-order').document(order_id)
    order_doc = order_ref.get()

    if not order_doc.exists:
        return HttpResponseNotFound("Order not found.")

    order_data = order_doc.to_dict()
    try:
        amount_to_pay = int(order_data.get('value', 0))
    except (ValueError, TypeError):
        logger.error(f"Invalid value in order {order_id}: {order_data.get('value')}")
        return JsonResponse({
            'status': 'ko',
            'error': 'Invalid order value. Contact support.'
        }, status=400)

    if request.method != 'POST':
        return JsonResponse({
            'status': 'ko',
            'error': 'Invalid request method. Use POST.'
        }, status=405)

    try:
        amount_paid_str = request.POST.get('amount_paid', '').strip()
        if not amount_paid_str:
            raise ValueError("Amount is required")

        amount_paid = float(amount_paid_str)
        if amount_paid < 0:
            raise ValueError("Amount cannot be negative")

        # Check for insufficient payment
        if amount_paid < amount_to_pay:
            error_msg = f'Insufficient amount. Please pay at least Shs.{amount_to_pay:,}'
            logger.info(f"Insufficient payment: {amount_paid} < {amount_to_pay} for order {order_id}")
            return JsonResponse({
                'status': 'ko',
                'error': error_msg
            }, status=400)

        change = amount_paid - amount_to_pay

        # This is the key part that sends the WebSocket message.
        # It's correctly placed after a successful payment validation.
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'client_screen_group',
            {
                'type': 'send_reset_message',
            }
        )

        # After successfully processing the payment and sending the message,
        # return the success JSON response.
        return JsonResponse({
            'status': 'ok',
            'amount_paid': amount_paid,
            'change': change,
            'value': amount_to_pay,
        })

    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid amount input: {str(e)}")
        return JsonResponse({
            'status': 'ko',
            'error': 'Invalid or missing payment amount'
        }, status=400)

    except Exception as e:
        logger.error(f"Unexpected error processing payment: {str(e)}")
        return JsonResponse({
            'status': 'ko',
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


def client_screen(request):
    """
    Renders the default page for the client screen display.
    This page will connect to a WebSocket to receive updates.
    """
    return render(request, 'flashtech/client_screen.html')


@csrf_exempt
def reset_client_screen(request):
    """
    Triggers a WebSocket message to reset the client screen.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'client_screen_group',
        {
            'type': 'send_reset_message',
        }
    )
    return JsonResponse({'status': 'ok'})
