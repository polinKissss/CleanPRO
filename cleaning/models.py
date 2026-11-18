from django.db import models
from django.db.models import Q, CheckConstraint, UniqueConstraint


class User(models.Model):
    ROLE_CHOICES = [("guest", "Гость"), ("customer", "Заказчик"), ("cleaner", "Клинер"),
                    ("senior_manager", "Старший менеджер смены"), ("admin", "Администратор")]
    full_name = models.CharField(max_length=150, verbose_name="Ф. И. О.")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Роль")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name="Клиент")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=150, verbose_name="Улица")
    house = models.CharField(max_length=10, verbose_name="Дом")
    apartment = models.PositiveIntegerField(null=True, blank=True, verbose_name="Квартира")
    comment = models.CharField(max_length=200, blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Адрес клиента"
        verbose_name_plural = "Адреса клиентов"

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house}"


class CleaningType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Вид уборки")
    labor_rate_per_m2 = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Норматив трудоёмкости, чел-ч/м²")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Вид уборки"
        verbose_name_plural = "Виды уборки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tariff(models.Model):
    cleaning_type = models.ForeignKey(CleaningType, on_delete=models.CASCADE, related_name="tariffs", verbose_name="Вид уборки")
    min_area = models.PositiveIntegerField(verbose_name="Мин. площадь, м²")
    max_area = models.PositiveIntegerField(verbose_name="Макс. площадь, м²")
    price_per_m2 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена за м²")

    class Meta:
        verbose_name = "Тариф за квадратный метр"
        verbose_name_plural = "Тарифы за квадратный метр"
        constraints = [CheckConstraint(condition=Q(min_area__lt=models.F("max_area")), name="tariff_area_range_valid")]

    def __str__(self):
        return f"{self.cleaning_type}: {self.min_area}–{self.max_area} м²"


class AdditionalOption(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Доп. опция")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    labor_hours = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Трудоёмкость, чел-ч")
    requires_extractor = models.BooleanField(default=False, verbose_name="Требует экстрактор")

    class Meta:
        verbose_name = "Дополнительная опция"
        verbose_name_plural = "Дополнительные опции"

    def __str__(self):
        return self.name


class Brigade(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название бригады")
    senior = models.ForeignKey("User", on_delete=models.PROTECT, related_name="brigades_led", limit_choices_to={"role": "cleaner"}, verbose_name="Старший бригады")

    class Meta:
        verbose_name = "Клининговая бригада"
        verbose_name_plural = "Клининговые бригады"

    def __str__(self):
        return self.name


class BrigadeMember(models.Model):
    brigade = models.ForeignKey(Brigade, on_delete=models.CASCADE, related_name="members", verbose_name="Бригада")
    cleaner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="brigade_memberships", limit_choices_to={"role": "cleaner"}, verbose_name="Клинер")
    role_in_brigade = models.CharField(max_length=20, default="клинер", verbose_name="Роль в бригаде")

    class Meta:
        verbose_name = "Состав бригады"
        verbose_name_plural = "Составы бригад"
        constraints = [UniqueConstraint(fields=["brigade", "cleaner"], name="unique_cleaner_in_brigade")]

    def __str__(self):
        return f"{self.cleaner} в {self.brigade}"


class Equipment(models.Model):
    EQUIP_TYPE = [("экстрактор", "Моющий экстрактор"), ("парогенератор", "Парогенератор"),
                  ("пылесос", "Профессиональный пылесос"), ("инвентарь", "Инвентарь")]
    STATUS = [("свободно", "Свободно"), ("в резерве", "В резерве"), ("закреплён", "Закреплён за бригадой")]
    name = models.CharField(max_length=150, verbose_name="Наименование")
    etype = models.CharField(max_length=20, choices=EQUIP_TYPE, verbose_name="Тип")
    status = models.CharField(max_length=20, choices=STATUS, verbose_name="Статус")

    class Meta:
        verbose_name = "Профессиональное оборудование"
        verbose_name_plural = "Профессиональное оборудование"

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS = [("новый", "Новый"), ("подтверждён", "Подтверждён"), ("в работе", "В работе"),
              ("завершён", "Завершён"), ("отменён", "Отменён")]
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер заказа")
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders", verbose_name="Заказчик")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders", verbose_name="Адрес")
    cleaning_type = models.ForeignKey(CleaningType, on_delete=models.PROTECT, related_name="orders", verbose_name="Вид уборки")
    tariff = models.ForeignKey(Tariff, on_delete=models.PROTECT, related_name="orders", verbose_name="Тариф")
    brigade = models.ForeignKey(Brigade, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Бригада")
    area = models.PositiveIntegerField(verbose_name="Площадь, м²")
    rooms = models.PositiveIntegerField(verbose_name="Комнат")
    bathrooms = models.PositiveIntegerField(verbose_name="Санузлов")
    date = models.DateField(verbose_name="Дата уборки")
    time = models.TimeField(verbose_name="Время начала")
    status = models.CharField(max_length=20, choices=STATUS, default="новый", verbose_name="Статус")
    labor_hours = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Трудоёмкость, чел-ч")
    cleaners_count = models.PositiveIntegerField(verbose_name="Клинеров")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма заказа")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-date"]
        constraints = [
            CheckConstraint(condition=Q(cleaners_count__gte=1, cleaners_count__lte=4), name="order_cleaners_1_4"),
            CheckConstraint(condition=Q(labor_hours__gt=0), name="order_labor_positive"),
        ]

    def __str__(self):
        return f"{self.number} — {self.customer}"


class OrderOption(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_options", verbose_name="Заказ")
    option = models.ForeignKey(AdditionalOption, on_delete=models.PROTECT, related_name="order_options", verbose_name="Опция")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена на момент заказа")

    class Meta:
        verbose_name = "Опция в заказе"
        verbose_name_plural = "Опции в заказах"
        constraints = [UniqueConstraint(fields=["order", "option"], name="unique_option_in_order")]

    def __str__(self):
        return f"{self.order.number}: {self.option} ×{self.quantity}"


class EquipmentReservation(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="equipment_reservation", verbose_name="Заказ")
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, related_name="reservations", verbose_name="Оборудование")
    start_time = models.TimeField(verbose_name="Начало резерва")
    end_time = models.TimeField(verbose_name="Конец резерва")

    class Meta:
        verbose_name = "Резервирование оборудования"
        verbose_name_plural = "Резервирования оборудования"

    def __str__(self):
        return f"{self.equipment} на заказ {self.order.number}"


class WorkSchedule(models.Model):
    cleaner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="schedule", verbose_name="Клинер")
    date = models.DateField(verbose_name="Дата смены")
    shift_start = models.TimeField(verbose_name="Начало смены")
    shift_end = models.TimeField(verbose_name="Конец смены")

    class Meta:
        verbose_name = "График работы"
        verbose_name_plural = "Графики работы"
        ordering = ["date"]

    def __str__(self):
        return f"{self.cleaner}: {self.date}"


class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reviews", verbose_name="Заказ")
    rating = models.PositiveIntegerField(verbose_name="Оценка")
    comment = models.TextField(verbose_name="Отзыв")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="review_rating_1_5")]

    def __str__(self):
        return f"Отзыв на {self.order.number} ({self.rating}/5)"
class CallbackRequest(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Почта")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"
