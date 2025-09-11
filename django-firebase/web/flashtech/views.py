from django.shortcuts import render
from django.http import HttpResponseNotFound
from djangofirebase.settings import db
from firebase_admin import firestore


def order_list(request):
    """
    Retrieves and displays a list of all orders from Firestore.
    """
    orders_ref = db.collection('flashtech-order')
    docs = orders_ref.stream()
    orders = []
    for doc in docs:
        order_data = doc.to_dict()
        order_data['id'] = doc.id
        orders.append(order_data)

    return render(request, 'flashtech/order_list.html', {'orders': orders})


def order_detail(request, order_id):
    """
    Retrieves and displays the details of a specific order,
    including orderMechanic and orderOwner.
    """
    order_ref = db.collection('flashtech-order').document(order_id)
    order_doc = order_ref.get()

    if not order_doc.exists:
        return HttpResponseNotFound("Order not found.")

    order_data = order_doc.to_dict()

    # Safely get the nested dictionary data
    order_mechanic = order_data.get('orderMechanic', {})
    order_owner = order_data.get('orderOwner', {})
    order_type = order_data.get('type')
    amount_to_pay = int(order_data.get('value'))
    mileage = order_data.get('mileage')
    vehicle_name = order_data.get('name')
    vehicle_number_plate = order_data.get('numberPlate')

    context = {
        'order_id': order_id,
        'order_mechanic': order_mechanic,
        'order_owner': order_owner,
        'order_type': order_type,
        'amount_to_pay': amount_to_pay,
        'mileage': mileage,
        'vehicle_name': vehicle_name,
        'vehicle_number_plate': vehicle_number_plate,
    }

    return render(request, 'flashtech/order_detail.html', context)
