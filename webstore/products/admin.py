from django.contrib import admin
from django import forms

from .models import *


# Прописываем условия, что бы при создании, например, наушников, можно было выбрать только категорию "Наушники"
# TODO
class EarphoneCategoryChoiceField(forms.ModelChoiceField):
    pass


class EarphonesAdmin(admin.ModelAdmin):

    def formfield_from_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return EarphoneCategoryChoiceField(Category.objects.filter(slug='earphone'))
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class PowerBankCategoryChoiceField(forms.ModelChoiceField):
    pass


class PowerBankAdmin(admin.ModelAdmin):

    def formfield_from_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return PowerBankCategoryChoiceField(Category.objects.filter(slug='power_bank'))
        return super().formfield_for_choice_field(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Earphones, EarphonesAdmin)
admin.site.register(PowerBank, PowerBankAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
