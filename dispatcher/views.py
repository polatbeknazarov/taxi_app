from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal

from dispatcher.forms import DriverChangeForm, PricingForm
from dispatcher.models import Pricing
from orders.models import Order, Client
from line.models import Line


User = get_user_model()


@staff_member_required(login_url='login/')
def index(request):
    orders_list = Order.objects.all()
    drivers_list = Line.objects.order_by('-status', '-joined_at')

    orders_page = request.GET.get('orders_page')
    drivers_page = request.GET.get('drivers_page')

    orders_paginator = Paginator(orders_list, 1)
    drivers_paginator = Paginator(drivers_list, 1)

    try:
        orders_page = orders_paginator.page(orders_page)
    except PageNotAnInteger:
        orders_page = orders_paginator.page(1)
    except EmptyPage:
        orders_page = orders_paginator.page(orders_paginator.num_pages)

    try:
        drivers_page = drivers_paginator.page(drivers_page)
    except PageNotAnInteger:
        drivers_page = drivers_paginator.page(1)
    except EmptyPage:
        drivers_page = drivers_paginator.page(drivers_paginator.num_pages)

    context = {
        'orders_quantity': orders_paginator.count,
        'drivers_quantity': drivers_paginator.count,
        'clients_quantity': Client.objects.count(),
        'orders_list': orders_page,
        'drivers_list': drivers_page,
    }

    return render(request, 'dispatcher/index.html', context)


@staff_member_required(login_url='login/')
def orders(request):
    if request.method == 'POST':
        try:
            client, created = Client.objects.get_or_create(
                phone_number=request.POST.get('phone_number')
            )

            if created:
                client.balance += 10000
                client.save()

            Order.objects.create(
                client=client,
                from_city=request.POST.get('from_city'),
                to_city=request.POST.get('to_city'),
                passengers=request.POST.get('passengers'),
                address=request.POST.get('address'),
            )

            return render(request, 'dispatcher/orders.html', {'message': 'Заявка создана'})
        except Exception as e:
            print(e)
            return render(request, 'dispatcher/orders.html', {'error': 'Произошла ошибка. Попробуйте еще раз.'})

    return render(request, 'dispatcher/orders.html')


staff_member_required(login_url='login/')
def order_details(request, pk):
    client = get_object_or_404(Order, pk=pk).client

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if amount > client.balance:
            messages.error(
                request, f'Недостаточно средств. Текущий баланс: {client.balance}')
        else:
            client.balance -= amount
            client.save()
            messages.success(
                request, f'Баланс клиента "{client}" успешно изменено.')

            return redirect('index')

    return render(request, 'dispatcher/order_details.html', {'client': client})


@staff_member_required(login_url='login/')
def drivers(request):
    if request.method == 'POST':
        if User.objects.filter(username=request.POST.get('username')).exists():
            messages.error(
                request, 'Пользователь с таким именем уже существует.')

            return render(request, 'dispatcher/drivers.html')

        try:
            user = User.objects.create_user(
                username=request.POST.get('username'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                password=request.POST.get('password'),
                phone_number=request.POST.get('phone_number'),
                is_driver=True
            )
            Line.objects.create(driver=user, from_city='NK', to_city='SB')

            return redirect('index')
        except Exception as e:
            messages.error(request, 'Произошла ошибка. Попробуйте еще раз')

    return render(request, 'dispatcher/drivers.html')


@staff_member_required(login_url='login/')
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


@staff_member_required(login_url='login/')
def add_balance(request, pk):
    if request.method == 'POST':
        try:
            driver = User.objects.get(pk=pk)
            driver.balance += Decimal(request.POST.get('balance'))

            driver.save()
        except Exception as e:
            print(e)

    return redirect('index')


@staff_member_required(login_url='login/')
def pricing(request):
    pricing = Pricing.get_singleton()

    if request.method == 'POST':
        form = PricingForm(request.POST, instance=pricing)

        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            return redirect('index')
    else:
        form = PricingForm(instance=pricing)

    return render(request, 'dispatcher/pricing.html', {'pricing': pricing, 'form': form})


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


@staff_member_required(login_url='login/')
def block_driver(request, pk):
    try:
        driver = get_object_or_404(User, pk=pk)
        driver.is_active = False
        driver.save(update_fields=['is_active'])
    except:
        messages.error(request, 'Произошла ошибка. Попробуйте еще раз.')

    messages.success(request, f'Водитель "{driver}" заблокирован.')
    return redirect('index')


@staff_member_required(login_url='login/')
def unblock_driver(request, pk):
    try:
        driver = get_object_or_404(User, pk=pk)
        driver.is_active = True
        driver.save(update_fields=['is_active'])
    except:
        messages.error(request, 'Произошла ошибка. Попробуйте еще раз.')

    messages.success(request, f'Водитель "{driver}" разблокирован.')
    return redirect('index')
