from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


# Create your models here.

# ***********

# 1 Category
# 2 Product
# 3 CartProduct
# 4 Cart
# 5 Order

# 6 Customer
# 7 Specification


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)  # endpoint для роутинга url

    def __str__(self):
        return self.name


# базовая модель продукта от которой наследуются все остальные категории
class Product(models.Model):
    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)  # endpoint для роутинга url
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title


class Earphones(Product):
    model_type = models.CharField(max_length=255, verbose_name='Тип модели')
    connect_type = models.CharField(max_length=255, verbose_name='Тип подключения')
    microphone = models.BooleanField(default=False, verbose_name='Наличие микрофона')
    noise_suppression = models.BooleanField(default=False, verbose_name='Наличие шумоизоляции')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы аккумулятора')

    def __str__(self):
        return f"{self.category.name} : {self.title}"


class PowerBank(Product):
    accumulator_type = models.CharField(max_length=255, verbose_name='Тип аккумулятора')
    ac_capacity = models.CharField(max_length=255, verbose_name='Емкость аккумулятора')
    out_amperage = models.CharField(max_length=255, verbose_name='Выходное напряжение')
    input_connectors = models.CharField(max_length=255, verbose_name='Входные разъемы')

    def __str__(self):
        return f"{self.category.name} : {self.title}"




# Earphones
# type
# connect_type
# microphone
# noise suppression

# Powerbank
# type
# capacity
# amperage
# input_connectors


# Объект корзины
class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    # С помощью взаимосвязи с корзиной можем получить информацию, к какой корзине привязан данный продукт корзины
    # например cart.related_products.all()
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    quantity = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма')

    def __str__(self):
        return f"Продукт: {self.product.title} (для корзины)"


class Cart(models.Model):
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)
    # С помощью взаимосвязи с продуктом корзины можем получить информацию, какие продукты привязаны к корзине
    # например cart.related_cart.all()
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма')

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Покупатель', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return f"Покупатель: {self.user.first_name} {self.user.last_name}"
