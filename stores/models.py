from django.db import models
from accounts.models import Users

# Create your models here.


class ProductTypes(models.Model):
    name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'product_types'
        verbose_name = verbose_name_plural = '製品タイプ'

    def __str__(self):
        return self.name


class Manufactures(models.Model):
    name = models.CharField(max_length=1000)

    class Meta:
        db_table = 'manufactures'
        verbose_name = verbose_name_plural = '製作者'

    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=1000)
    price = models.IntegerField()
    stock = models.IntegerField()
    product_type = models.ForeignKey(ProductTypes, on_delete=models.CASCADE)
    manufacture = models.ForeignKey(Manufactures, on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'
        verbose_name = verbose_name_plural = '製品'

    def __str__(self):
        return self.name


class ProductPictures(models.Model):
    picute = models.FileField(upload_to='product_pictures/')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    order = models.IntegerField()  # 複数写真の想定で、何番目の写真かを管理するカラム

    class Meta:
        db_table = 'product_pictures'
        ordering = ['order']  # orderingはソート基準のカラムの指定
        verbose_name = verbose_name_plural = '製品画像'

    def __str__(self):
        return self.product.name + ' :' + str(self.order)


class Carts(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        db_table = 'carts'


class CartItemsManager(models.Manager):

    def save_item(self, product_id, quantity, cart):
        c = self.model(quantity=quantity, product_id=product_id, cart=cart)
        c.save()


class CartItems(models.Model):
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    cart = models.ForeignKey(Carts, on_delete=models.CASCADE)

    objects = CartItemsManager()

    class Meta:
        db_table = 'cart_items'
        # fkのproductとcartの組み合わせでユニークとする
        unique_together = [['product', 'cart']]


class Addresses(models.Model):
    zip_code = models.CharField(max_length=8)
    prefecture = models.CharField(max_length=10)
    address = models.CharField(max_length=200)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        db_table = 'addresses'
        # 同じユーザーが、下記の組み合わせが同じデータを、DBに登録できないようにするため、unique_togetherで制約をつける ＊1
        unique_together = [
            ['zip_code', 'prefecture', 'address', 'user']
        ]

    def __str__(self):
        return f'{self.zip_code} {self.prefecture} {self.address}'
