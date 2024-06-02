import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from decimal import Decimal
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from dispatcher.forms import DriverChangeForm, PricingForm, RegisterDriverForm
from dispatcher.models import Pricing, DriverBalanceHistory
from dispatcher.utils import send_line
from orders.models import Order, Client, OrdersHistory
from orders.tasks import send_sms
from line.models import Line
from line.serializers import LineSerializer


User = get_user_model()


@staff_member_required(login_url='login/')
def index(request):
    orders_list = Order.objects.filter(in_search=True).order_by('-created_at')
    all_orders = Order.objects.count()
    all_drivers = Line.objects.count()
    drivers_list_nk = Line.objects.filter(
        status=True, from_city='NK').order_by('-status', 'joined_at')
    drivers_list_sb = Line.objects.filter(
        status=True, from_city='SB').order_by('-status', 'joined_at')

    context = {
        'orders_quantity': all_orders,
        'drivers_quantity': all_drivers,
        'clients_quantity': Client.objects.count(),
        'orders_list': orders_list,
        'drivers_list_nk': drivers_list_nk,
        'drivers_list_sb': drivers_list_sb,
    }

    return render(request, 'dispatcher/index.html', context)


@staff_member_required(login_url='login/')
def orders(request):
    orders_list = Order.objects.all().order_by('-created_at')

    paginator = Paginator(orders_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        try:
            from_city = request.POST.get('from_city')
            to_city = request.POST.get('to_city')
            passengers_count = int(request.POST.get('passengers'))
            address = request.POST.get('address')

            client, created = Client.objects.get_or_create(
                phone_number=request.POST.get('phone_number')
            )
            drivers_line = Line.objects.filter(
                status=True,
                from_city=from_city,
                to_city=to_city,
            ).order_by('-created_at')
            pricing_data = Pricing.get_singleton()

            if drivers_line:
                for driver in drivers_line:
                    if (driver.driver.balance >= passengers_count * pricing_data.order_fee) and (driver.passengers_required >= driver.passengers + passengers_count):
                        new_order = Order.objects.create(
                            client=client,
                            from_city=from_city,
                            to_city=to_city,
                            passengers=passengers_count,
                            address=address,
                            driver=driver.driver,
                            in_search=False,
                            is_free=False,
                        )

                        OrdersHistory.objects.create(
                            driver=driver.driver, order=new_order)

                        driver.passengers += int(
                            request.POST.get('passengers'))
                        user = User.objects.get(pk=driver.driver.pk)
                        user.balance -= pricing_data.order_fee * passengers_count
                        driver.save()
                        user.save()
                        driver.refresh_from_db()

                        if driver.passengers == driver.passengers_required:
                            driver.status = False
                            driver.save(update_fields=['status'])

                        send_line(from_city=driver.from_city,
                                  to_city=driver.to_city)
                        send_sms.delay(
                            phone_number=driver.driver.phone_number,
                            message='"Saqiy Taxi". Назначена новая заявка, проверьте в Saqiy Taxi.'
                        )
                        send_sms.delay(
                            phone_number=new_order.client.phone_number,
                            message=f'Saqiy Taxi. Вам назначена {driver.driver.car_brand} {driver.driver.car_number} Номер таксиста {driver.driver.phone_number}'
                        )

                        messages.success(request, 'Заявка создана')
                        return redirect('index')

            Order.objects.create(
                client=client,
                from_city=from_city,
                to_city=to_city,
                passengers=passengers_count,
                address=address,
                in_search=True,
                is_free=True,
            )
            messages.success(request, 'Заявка создана')
            return redirect('index')
        except Exception as e:
            print(e)
            messages.error(
                request, f'Произошла ошибка. Попробуйте еще раз.\n\n{e}')

    return render(request, 'dispatcher/orders.html', {'orders_list': page_obj})


@staff_member_required(login_url='login/')
def order_details(request, pk):
    client = get_object_or_404(Order, pk=pk).client

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if amount > client.balance:
            messages.error(
                request, f'Недостаточно средств. Текущий баланс: {client.balance}')
        else:
            client.balance -= amount
            client.save(update_fields=['balance'])

            messages.success(request, f'Баланс успешно изменено.')
            return redirect('index')

    return render(request, 'dispatcher/order_details.html', {'client': client})


@staff_member_required(login_url='login/')
def drivers(request):
    drivers = Line.objects.all().order_by('-created_at')

    paginator = Paginator(drivers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = RegisterDriverForm(request.POST, request.FILES)

        if form.is_valid():
            get_car_number = request.POST.get('car_number')
            car_number = get_car_number.replace(" ", "").upper()
            user = form.save(commit=False)
            user.is_driver = True
            user.car_number = car_number
            user.save()
            Line.objects.create(driver=user, from_city='NK',
                                to_city='SB', passengers_required=0)

            messages.success(request, 'Водитель успешно создан.')
            return redirect('index')
        else:
            messages.error(request, form.errors)
    else:
        form = RegisterDriverForm()

    return render(request, 'dispatcher/drivers.html', {'drivers_list': page_obj, 'form': form})


@staff_member_required(login_url='login/')
def driver_details(request, pk):
    driver = Line.objects.get(pk=pk)

    if request.method == 'POST':
        form = DriverChangeForm(
            data=request.POST, instance=driver.driver, files=request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            return redirect('index')
        else:
            messages.error(request, 'Произошла ошибка. Попробуйте еще раз')
    else:
        form = DriverChangeForm(instance=driver.driver)

    return render(request, 'dispatcher/driver_details.html', {'form': form, 'driver': driver})


@staff_member_required(login_url='login/')
def remove_from_line(request, pk):
    channel_layer = get_channel_layer()

    driver = Line.objects.get(pk=pk)
    driver.status = False
    driver.save()

    line = Line.objects.filter(status=True)
    data = LineSerializer(line, many=True)

    for driver in line:
        async_to_sync(channel_layer.group_send)(
            driver.driver.username,
            {
                'type': 'send_message',
                'message': json.dumps({'line': data}),
            }
        )

    return redirect('index')


@staff_member_required(login_url='login/')
def add_balance(request, pk):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('balance'))
            driver = User.objects.get(pk=pk)
            driver.balance += amount

            driver.save()
            DriverBalanceHistory.objects.create(
                driver=driver, amount=amount, transaction='+')
            messages.success(request, 'Данные успешно изменены.')
        except Exception as e:
            messages.error(
                request, f'Произошла ошибка. Попробуйте еще раз. {e}')

    return redirect('index')


@staff_member_required(login_url='login/')
def minus_balance(request, pk):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('balance'))
            driver = User.objects.get(pk=pk)
            driver.balance -= amount

            driver.save()
            DriverBalanceHistory.objects.create(
                driver=driver, amount=amount, transaction='-')
            messages.success(request, 'Данные успешно изменены.')
        except Exception as e:
            messages.error(
                request, f'Произошла ошибка. Попробуйте еще раз. {e}')

    return redirect('index')


@staff_member_required(login_url='login/')
def pricing(request):
    pricing = Pricing.get_singleton()
    print(pricing)

    if request.method == 'POST':
        form = PricingForm(request.POST, instance=pricing)

        if form.is_valid():
            form.save()
            messages.success(request, 'Данные успешно изменены.')
            return redirect('index')
    else:
        form = PricingForm(instance=pricing)

    return render(request, 'dispatcher/pricing.html', {'pricing': pricing, 'form': form})


@staff_member_required(login_url='login/')
def history(request):
    data_list = DriverBalanceHistory.objects.all().order_by('-created_at')
    paginator = Paginator(data_list, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dispatcher/history.html', {'data': page_obj})


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
        line = get_object_or_404(Line, driver=driver)
        line.status = False
        driver.is_active = False
        line.save(update_fields=['status',])
        driver.save(update_fields=['is_active',])
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
