from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db.models import F
from decimal import Decimal

from orders.models import Order, Client
from line.models import Line
from dispatcher.forms import RegisterDriverForm, DriverChangeForm


User = get_user_model()


@login_required
def index(request):
    orders = Order.objects.all()
    clients = Client.objects.all()
    drivers = Line.objects.all().order_by('-status', 'joined_at')

    context = {
        'orders_quantity': orders.count(),
        'drivers_quantity': drivers.count(),
        'clients_quantity': clients.count(),
        'orders_list': orders,
        'drivers_list': drivers,
    }

    return render(request, 'dispatcher/index.html', context)


@login_required
def orders(request):
    if request.method == 'POST':
        try:
            client, created = Client.objects.get_or_create(
                phone_number=request.POST.get('phone_number')
            )

            Order.objects.create(
                client=client,
                from_city=request.POST.get('from_city'),
                to_city=request.POST.get('to_city'),
                passengers=request.POST.get('passengers'),
                address=request.POST.get('address'),
            )

            return render(request, 'dispatcher/orders.html', {'message': 'Заявка создана'})
        except:
            return render(request, 'dispatcher/orders.html', {'error': 'Произошла ошибка. Попробуйте еще раз.'})

    return render(request, 'dispatcher/orders.html')


@login_required
def drivers(request):
    if request.method == 'POST':
        form = RegisterDriverForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('drivers')
    else:
        form = RegisterDriverForm()

    return render(request, 'dispatcher/drivers.html', {'form': form})


@login_required
def driver_details(request, pk):
    driver = Line.objects.get(pk=pk)

    if request.method == 'POST':
        form = DriverChangeForm(
            data=request.POST, instance=driver.driver, files=request.FILES)
        print(request.POST)

        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = DriverChangeForm(instance=driver.driver)

    return render(request, 'dispatcher/driver_details.html', {'form': form, 'driver': driver.driver})


@login_required
def add_balance(request, pk):
    if request.method == 'POST':
        Line.objects.filter(pk=pk).update(driver__balance=F('driver__balance') + Decimal(request.POST.get('balance')))

    return redirect('index')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'dispatcher/login.html', {'error_message': 'Неверное имя пользователя или пароль'})
    else:
        return render(request, 'dispatcher/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def page_not_found_view(request, exception):
    return redirect('index')
