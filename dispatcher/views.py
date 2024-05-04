from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from decimal import Decimal

from orders.models import Order, Client
from line.models import Line
from dispatcher.forms import RegisterDriverForm, DriverChangeForm


User = get_user_model()


@user_passes_test(lambda u: u.is_staff, login_url='login/')
def index(request):
    orders = Order.objects.all()
    clients = Client.objects.all()
    drivers_user = Line.objects.all().order_by('-status', '-joined_at')


    context = {
        'orders_quantity': orders.count(),
        'drivers_quantity': drivers_user.count(),
        'clients_quantity': clients.count(),
        'orders_list': orders,
        'drivers_list': drivers_user,
    }

    return render(request, 'dispatcher/index.html', context)


@user_passes_test(lambda u: u.is_staff, login_url='login/')
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
                is_driver=True
            )

            return render(request, 'dispatcher/orders.html', {'message': 'Заявка создана'})
        except:
            return render(request, 'dispatcher/orders.html', {'error': 'Произошла ошибка. Попробуйте еще раз.'})

    return render(request, 'dispatcher/orders.html')


@user_passes_test(lambda u: u.is_staff, login_url='login/')
def drivers(request):
    if request.method == 'POST':
        if User.objects.filter(username=request.POST.get('username')).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')

            return render(request, 'dispatcher/drivers.html')

        try:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password=request.POST.get('password'),
                phone_number=request.POST.get('phone_number')
            )
            Line.objects.create(driver=user, from_city='NK', to_city='SB')

            return redirect('index')
        except Exception as e:
            messages.error(request, 'Произошла ошибка. Попробуйте еще раз')

    return render(request, 'dispatcher/drivers.html')


@user_passes_test(lambda u: u.is_staff, login_url='login/')
def driver_details(request, pk):
    driver = Line.objects.get(pk=pk)

    if request.method == 'POST':
        form = DriverChangeForm(
            data=request.POST, instance=driver.driver, files=request.FILES)

        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = DriverChangeForm(instance=driver.driver)

    return render(request, 'dispatcher/driver_details.html', {'form': form, 'driver': driver.driver})


@user_passes_test(lambda u: u.is_staff, login_url='login/')
def add_balance(request, pk):
    if request.method == 'POST':
        try:
            driver = User.objects.get(pk=pk)
            driver.balance += Decimal(request.POST.get('balance'))

            driver.save()
        except Exception as e:
            print(e)

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


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


def page_not_found_view(request, exception):
    return redirect('index')
