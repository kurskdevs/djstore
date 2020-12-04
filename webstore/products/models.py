import sys

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from io import BytesIO

User = get_user_model()


class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        """
        Функция для получения определенного количества последних добавленных товаров
        по заданной категории
        :param args: lowercase моделей (Earphone, PowerBank)
        :param kwargs: добавление key аргумента with_respect_to для сортировки товаров
        :return: Список поледних добавленных товаров
        """

        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:  # проверяем, что бы пользователь не ошибся с запросом
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )

        return products


class LatestProducts:
    objects = LatestProductsManager()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)  # endpoint для роутинга url

    def __str__(self):
        return self.name


# базовая модель продукта от которой наследуются все остальные категории
class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

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

    def save(self, *args, **kwargs):
        # функция запрета на загрузку изображений
        # image = self.image
        # img = Image.open(image)
        # min_height, min_width = self.MIN_RESOLUTION
        # max_height, max_width = self.MAX_RESOLUTION
        # if img.height < min_height or img.width < min_width:
        #     raise MinResolutionErrorException('Разрешение изображения меньше минимального!')
        # if img.height > max_height or img.width > max_width:
        #     raise MaxResolutionErrorException('Разрешение изображения больше максимального!')

        image = self.image  # получение изображения
        img = Image.open(image)  # открытие изображения через библиотеку PIL
        new_img = img.convert('RGB')  # конвертирование изображения в RGB
        resized_new_img = new_img.resize((400, 400), Image.ANTIALIAS)  # обрезка изображения
        filestream = BytesIO()  # получение байтового потока изображения
        resized_new_img.save(filestream, 'JPEG', quality=90) 
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
            # запись в стандартную переменную
        )

        super().save(*args, **kwargs)


class Earphone(Product):
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
