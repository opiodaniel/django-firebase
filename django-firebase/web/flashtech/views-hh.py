import json

from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from djangofirebase.settings import db
from firebase_admin import firestore

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
    orders_ref = db.collection('flashtech-order')
    docs = orders_ref.stream()
    orders = []

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
    """
    Retrieves and displays the details of a specific order.
    Handles both displaying the page (GET) and processing payments (POST).
    """
    order_ref = db.collection('flashtech-order').document(order_id)
    order_doc = order_ref.get()

    if not order_doc.exists:
        return HttpResponseNotFound("Order not found.")

    order_data = order_doc.to_dict()

    # Safely get the nested dictionary data
    order_mechanic = order_data.get('orderMechanic', {})
    order_owner = order_data.get('orderOwner', {})

    # Safely get vehicle data
    mileage = order_data.get('mileage')
    vehicle_name = order_data.get('name')
    vehicle_number_plate = order_data.get('numberPlate')

    # Safely get order and payment data
    order_type = order_data.get('type')
    amount_to_pay = int(order_data.get('value'))
    amount_paid = 0
    balance_remaining = 0
    change = 0

    # Handle POST request for payment
    if request.method == 'POST':
        try:
            amount_paid = float(request.POST.get('amount_paid'))
            change = int(amount_paid - amount_to_pay)
            # You can also add logic here to update Firestore with the payment
        except (ValueError, TypeError):
            # Handle cases where amount_paid is not a valid number
            pass

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
        # logger.error(f"Invalid value in order {order_id}: {order_data.get('value')}")
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
            # logger.info(f"Insufficient payment: {amount_paid} < {amount_to_pay} for order {order_id}")
            return JsonResponse({
                'status': 'ko',
                'error': error_msg
            }, status=400)

        change = amount_paid - amount_to_pay

        # logger.info(f"Payment successful: {amount_paid} paid for order {order_id}")
        return JsonResponse({
            'status': 'ok',
            'amount_paid': amount_paid,
            'change': change,
            'value': amount_to_pay,
            'order_items': [
                {'name': 'Oil Change', 'price': 150000},
                {'name': 'Brake Pads Replacement', 'price': 450000},
                {'name': 'Tire Rotation', 'price': 60000}
            ]
        })

    except (ValueError, TypeError) as e:
        # logger.warning(f"Invalid amount input: {str(e)}")
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
    order_id = request.GET.get('currentOrder')
    print(f"[DEBUG] Received currentOrder={repr(order_id)}")  # Shows exact value

    current_order = None
    if order_id:
        print(f"[DEBUG] Looking up Firestore document: {order_id}")
        doc = db.collection('flashtech-order').document(order_id).get()
        if doc.exists:
            print(f"[DEBUG] Document found!")
            current_order = doc.to_dict()
            current_order['id'] = doc.id
        else:
            print(f"[WARNING] Document {order_id} not found in Firestore")
    else:
        print("[WARNING] No currentOrder parameter in request")

    return render(request, 'flashtech/client_screen.html', {
        'current_order_id': order_id,
        'current_order': current_order,
    })
