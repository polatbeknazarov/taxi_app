from orders.models import Order


def get_order():
    order = Order.objects.all().first()
    print(order)

    return order
