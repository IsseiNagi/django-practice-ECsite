from django.db import models

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
