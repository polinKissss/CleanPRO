from django.contrib import admin
from .models import (
    User, Address, CleaningType, Tariff, AdditionalOption,
    Brigade, BrigadeMember, Equipment, Order, OrderOption,
    EquipmentReservation, WorkSchedule, Review, CallbackRequest,
)

admin.site.register(User)
admin.site.register(Address)
admin.site.register(CleaningType)
admin.site.register(Tariff)
admin.site.register(AdditionalOption)
admin.site.register(Brigade)
admin.site.register(BrigadeMember)
admin.site.register(Equipment)
admin.site.register(Order)
admin.site.register(OrderOption)
admin.site.register(EquipmentReservation)
admin.site.register(WorkSchedule)
admin.site.register(Review)
admin.site.register(CallbackRequest)
