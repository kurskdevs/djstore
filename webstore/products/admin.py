from django.contrib import admin
from django import forms

from .models import *


# Прописываем условия, что бы при создании, например, наушников, можно было выбрать только категорию "Наушники"
# TODO

class EarphoneAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return forms.ModelChoiceField(queryset=Category.objects.filter(slug='earphone'))
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class PowerBankAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return forms.ModelChoiceField(queryset=Category.objects.filter(slug='power_bank'))
        return super().formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Earphone, EarphoneAdmin)
admin.site.register(PowerBank, PowerBankAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
