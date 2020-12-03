from django.contrib import admin
from django import forms
from django.forms import ModelForm, ValidationError

from .models import *

from PIL import Image


class EarphoneAdminForm(ModelForm):
    MIN_RESOLUTION = (400, 400)

    # добавление вспомогательного текста в админке при загрузке изображений
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = 'Загружайте изображния с минимальным расшмрением {}x{}'.format(
            *self.MIN_RESOLUTION)

    # функция для ограничения по загрузке изображений
    def clean_image(self):
        # получение изображения из формы
        image = self.cleaned_data['image']
        # отрытие изображения для получения его параметров
        img = Image.open(image)
        # получаем минимальные размеры
        min_height, min_width = self.MIN_RESOLUTION
        if img.height < min_height or img.width < min_width:
            raise ValidationError('Разрешение изображения меньше минимального!')


# Прописываем условия, что бы при создании, например, наушников, можно было выбрать только категорию "Наушники"

class EarphoneAdmin(admin.ModelAdmin):
    form = EarphoneAdminForm

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
