from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

import os

from .models import (
    Products,
)
# Create your views here.R


class ProductListView(LoginRequiredMixin, ListView):
    model = Products
    template_name = os.path.join('stores', 'product_list.html')

    def get_queryset(self):  # ListViewで実行されるクエリを書き換える
        query = super().get_queryset()
        product_type_name = self.request.GET.get('product_type_name', None)
        product_name = self.request.GET.get('product_name', None)
        if product_type_name:
            # product_typeの__name（カラム）をproduct_type_nameで絞り込む productモデルから見ている
            query = query.filter(
                product_type__name=product_type_name
            )
        if product_name:
            # productのname（カラム）をproduct_nameで絞り込む
            query = query.filter(
                name=product_name
            )
        order_by_price = self.request.GET.get('order_by_price', 0)
        if order_by_price == '1':
            query = query.order_by('price')
        elif order_by_price == '2':
            query = query.order_by('-price')
        return query

    # 検索窓に入れた言葉で絞り込んだ結果が表示された時、検索窓にその言葉が表示されたままにする
    # get_context_data：テンプレートを表示する際に、テンプレートで使用する変数を設定するところ
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_type_name'] = self.request.GET.get(
            'product_type_name', '')
        context['product_name'] = self.request.GET.get(
            'product_name', '')
        # GET.getでorder_by_priceから送られる値を取得する（1か2）
        order_by_price = self.request.GET.get('order_by_price', 0)
        # 値に応じてascending（昇順）、descending（降順）を切り替えて、contextで送る
        if order_by_price == '1':
            context['ascending'] = True
        elif order_by_price == '2':
            context['descending'] = True
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Products
    template_name = os.path.join('stores', 'product_detail.html')
