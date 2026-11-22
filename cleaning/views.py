import logging

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import User, Order
import math


from .forms import CallbackForm
from .models import CleaningType, Order, Tariff

logger = logging.getLogger('cleaning')


def home(request):
    return render(request, 'home.html', {'cleaning_types': CleaningType.objects.all()})


def services_list(request):
    query = request.GET.get('q', '').strip()
    objects = CleaningType.objects.all()
    if query:
        objects = objects.filter(name__icontains=query)
    paginator = Paginator(objects, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'services.html', {'page_obj': page_obj, 'query': query})


def service_detail(request, pk):
    cleaning_type = CleaningType.objects.filter(pk=pk).first()
    tariffs = []
    if cleaning_type:
        tariffs = Tariff.objects.filter(cleaning_type=cleaning_type).order_by('min_area')
    return render(request, 'service_detail.html', {
        'cleaning_type': cleaning_type,
        'tariffs': tariffs,
    })


def search(request):
    query = request.GET.get('q', '').strip()
    objects = CleaningType.objects.all()
    if query:
        objects = objects.filter(name__icontains=query)
    paginator = Paginator(objects, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'search.html', {'page_obj': page_obj, 'query': query})


def calculator(request):
    ct_id = request.GET.get('cleaning_type')
    area_raw = request.GET.get('area', '')
    try:
        area = int(area_raw)
    except (TypeError, ValueError):
        area = 0

    ct = CleaningType.objects.filter(pk=ct_id).first()

    logger.info('Начало расчёта: вид=%s, площадь=%s', ct_id, area)

    context = {
        'types': CleaningType.objects.all(),
        'options': [],
        'chosen_options': [],
        'chosen_area': area_raw,
    }

    if not ct:
        context['error'] = 'Выберите вид уборки.'
        return render(request, 'calculator.html', context)

    tariff = (Tariff.objects
              .filter(cleaning_type=ct, min_area__lte=area)
              .order_by('-min_area')
              .first())

    if not tariff:
        logger.warning('Тариф не найден: вид=%s, площадь=%s', ct_id, area)
        context['error'] = 'Для такой площади пока нет тарифа.'
        return render(request, 'calculator.html', context)
    
    base_price = tariff.price_per_m2 * area
    hours = (ct.labor_rate_per_m2 * area) / 8
    cleaners = max(1, min(4, math.ceil(hours / 6)))

    if hours > 24:
        logger.warning('Ручной подбор: трудоёмкость=%s ч превышает 24 ч', hours)


    print(f"DEBUG: hours={hours}, cleaners={cleaners}")

    logger.info('Расчёт завершён: итого=%s, клинеров=%d', base_price, cleaners)


    context.update({
        'chosen_type': ct,
        'chosen_tariff': tariff,
        'hours': hours,
        'cleaners': cleaners,
        'result': base_price,
    })
    return render(request, 'calculator.html', context)




def profile(request):
    context = {}
    # находим пользователя проекта по логину Django (логин = телефон)
    customer = User.objects.filter(phone=request.user.username).first()
    orders = Order.objects.filter(customer=customer).order_by('-date') if customer else []
    context['orders'] = orders
    return render(request, 'profile.html', context)




def about(request):
    return render(request, 'about.html')


def contacts(request):
    """Форма заявки: ModelForm, csrf, валидация, сообщения, redirect."""
    if request.method == 'POST':
        logger.info('Получена заявка: name=%s, phone=%s',
                    request.POST.get('name'), request.POST.get('phone'))
        form = CallbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка отправлена! Перезвоним в течение часа.')
            return redirect('contacts')
        else:
            logger.warning('Заявка не прошла валидацию: %s', form.errors.as_text())
    else:
        form = CallbackForm()
    return render(request, 'contacts.html', {'form': form})


def api_search(request):
    query = request.GET.get('q', '').strip()
    types = CleaningType.objects.none()
    if query:
        types = CleaningType.objects.filter(name__icontains=query)[:10]
    data = [{
        'pk': t.pk,
        'name': t.name,
        'description': (t.description[:80] + '…') if len(t.description) > 80 else t.description,
        'url': f'/services/{t.pk}/',
    } for t in types]
    return JsonResponse({'query': query, 'results': data})
