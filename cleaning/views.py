import math
from decimal import Decimal

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from .forms import CallbackForm


from .models import CleaningType, AdditionalOption, Order


def home(request):
    """Главная: блок популярных видов уборки берётся из базы."""
    cleaning_types = CleaningType.objects.all()[:3]
    return render(request, 'home.html', {'cleaning_types': cleaning_types})


def services_list(request):
    """Каталог видов уборки из базы, пагинация по 20, поиск по названию."""
    query = request.GET.get('q', '')
    types = CleaningType.objects.all().order_by('name')
    if query:
        types = types.filter(name__icontains=query)
    paginator = Paginator(types, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'services.html', {'page_obj': page_obj, 'query': query})


def service_detail(request, pk):
    """Страница одной записи: вид уборки и его тарифы."""
    cleaning_type = get_object_or_404(CleaningType, pk=pk)
    tariffs = cleaning_type.tariffs.all().order_by('min_area')
    return render(request, 'service_detail.html', {
        'cleaning_type': cleaning_type,
        'tariffs': tariffs,
    })


def search(request):
    """Страница результатов поиска по видам уборки."""
    query = request.GET.get('q', '')
    types = CleaningType.objects.none()
    if query:
        types = CleaningType.objects.filter(name__icontains=query).order_by('name')
    paginator = Paginator(types, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'search.html', {'page_obj': page_obj, 'query': query})


def calculator(request):
    """Калькулятор: виды и опции из базы, тариф подбирается по площади."""
    types = CleaningType.objects.all().order_by('name')
    options = AdditionalOption.objects.all().order_by('name')
    context = {'types': types, 'options': options}

    if request.method == 'GET' and 'cleaning_type' in request.GET:
        try:
            ct_id = int(request.GET.get('cleaning_type'))
            area = int(request.GET.get('area', 0))
        except (TypeError, ValueError):
            context['error'] = 'Выберите вид уборки и укажите площадь.'
            return render(request, 'calculator.html', context)

        ct = CleaningType.objects.filter(pk=ct_id).first()
        if not ct or area <= 0:
            context['error'] = 'Выберите вид уборки и укажите площадь больше нуля.'
            return render(request, 'calculator.html', context)

        tariff = ct.tariffs.filter(min_area__lte=area, max_area__gte=area).first()
        if not tariff:
            context['error'] = 'Для такой площади пока нет тарифа.'
            return render(request, 'calculator.html', context)

        selected = options.filter(pk__in=request.GET.getlist('options'))
        base_price = tariff.price_per_m2 * area
        options_price = sum((o.price for o in selected), Decimal('0'))
        hours = ct.labor_rate_per_m2 * area + sum((o.labor_hours for o in selected), Decimal('0'))
        cleaners = min(4, max(1, math.ceil(float(hours) / 8)))

        context.update(
            result=base_price + options_price,
            hours=hours,
            cleaners=cleaners,
            chosen_type=ct,
            chosen_tariff=tariff,
            chosen_area=area,
            chosen_options=selected,
        )
    return render(request, 'calculator.html', context)


def profile(request):
    """Личный кабинет: заказы первого клиента в базе."""
    first_order = Order.objects.select_related('customer').first()
    orders = []
    if first_order:
        orders = (Order.objects.filter(customer=first_order.customer)
                  .select_related('cleaning_type')[:10])
    return render(request, 'profile.html', {'orders': orders})


def about(request):
    return render(request, 'about.html')


def contacts(request):
    return render(request, 'contacts.html')
def contacts(request):
    """Форма заявки: ModelForm, csrf, валидация, сообщения, redirect."""
    if request.method == 'POST':
        form = CallbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка отправлена! Перезвоним в течение часа.')
            return redirect('contacts')  # POST-Redirect-GET: без повторной отправки
    else:
        form = CallbackForm()
    return render(request, 'contacts.html', {'form': form})


def api_search(request):
    """JSON для живого поиска: до 10 совпадений по видам уборки."""
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

