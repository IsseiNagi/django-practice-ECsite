from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.core.cache import cache
from django.db import transaction

import os

from .models import (
    Products,
    Carts,
    CartItems,
    Addresses,
    Orders,
    OrderItems,
)
from .forms import CartUpdateForm, AddressInputForm
# Create your views here.


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # カートの情報をcontextで送るための定義
        context['is_added'] = CartItems.objects.filter(
            # requestを送っているユーザーのidと、productのidでフィルターしてfirstを取得する
            cart_id=self.request.user.id,
            product_id=kwargs.get('object').id
        ).first()
        return context


@login_required
def add_product(request):

    if request.is_ajax:  # ajaxで送られてきた場合に実行
        # ajax実行時にtemplateから送っているproduct_idとquantityを取得する
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        # get_object_or_404を使ってidを取得する
        product = get_object_or_404(Products, id=product_id)

        # 在庫数を超えた数値が入力された場合にエラーを返す
        if int(quantity) > product.stock:
            response = JsonResponse({'message': '在庫数を超えています'})
            response.status_code = 403
            return response
        if int(quantity) <= 0:
            response = JsonResponse({'message': '0より大きい値を入力してください'})
            response.status_code = 403
            return response

        # cartが存在しない場合は、cartを作成して、存在する場合はcartを返す：get_or_create
        cart = Carts.objects.get_or_create(
            user=request.user
        )
        # product_idとcart、quantityの情報が揃っていたら実行
        if all([product_id, cart, quantity]):
            # CartItemsManagerのsave_itemを実行
            CartItems.objects.save_item(
                quantity=quantity,
                product_id=product_id,
                # cartはget_or_createの結果タプル型で返されるので[0]を指定している
                cart=cart[0],
            )
        return JsonResponse({'message': 'カートに商品を追加しました'})


class CartItemsView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'cart_items.html')

    # カートの一覧表示で、合計金額を表示させるため
    # get_context_dataをオーバーライド
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        query = CartItems.objects.filter(cart_id=user_id)
        # 中に入っている商品の価格をループさせて合計を出す
        total_price = 0
        items = []
        for item in query.all():
            total_price += item.quantity * item.product.price
            # ProductPicturesモデルのsetの最初の値を取得する
            picture = item.product.productpictures_set.first()
            # ProductPicturesのpictureカラムの値をセットする
            picture = picture.picute if picture else None
            # 処理中に在庫が変わる可能性があるので、この時点での在庫数と、quantityを照らし合わせている
            in_stock = True if item.product.stock >= item.quantity else False
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'id': item.id,
                'price': item.product.price,
                'in_stock': in_stock,
            }
            # 空のitemsリストに追加していく
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        return context


# カートの編集画面の作成
class CartUpdateView(LoginRequiredMixin, UpdateView):
    template_name = os.path.join('stores', 'update_cart.html')
    form_class = CartUpdateForm
    model = CartItems
    success_url = reverse_lazy('stores:cart_items')


class CartDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('stores', 'delete_cart.html')
    model = CartItems
    success_url = reverse_lazy('stores:cart_items')


# 住所入力
class InputAddressView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('stores', 'input_address.html')
    form_class = AddressInputForm
    success_url = reverse_lazy('stores:confirm_order')

    # カートに商品が入っていなかったらエラー表示をする 過去の住所一覧から入力するurlに遷移するためのpkも引数に加える
    def get(self, request, pk=None):
        cart = get_object_or_404(Carts, user_id=request.user.id)
        if not cart.cartitems_set.all():
            raise Http404('商品がカートに入っていません')
        return super().get(request, pk)

    # get_context_dataを上書きして、templateにformでcache保存した値を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = cache.get(f'address_user_{self.request.user.id}')

        pk = self.kwargs.get('pk')  # getの引数に取ったpkを、ここでkwargsから取り出す
        # pkがあった場合はifより前を実行、ない場合はaddressは上のcacheを代入したaddress
        # pkがあった場合の処理はpkを利用してAddressesからデータを取得する
        address = get_object_or_404(
            Addresses, user_id=self.request.user.id, pk=pk) if pk else address

        if address:
            # contextでfieldの初期値を送る
            context['form'].fields['zip_code'].initial = address.zip_code
            context['form'].fields['prefecture'].initial = address.prefecture
            context['form'].fields['address'].initial = address.address
        # 今まで入力した住所を表示するために、Addressesからユーザーに紐づいた住所情報を取り出す
        context['addresses'] = Addresses.objects.filter(
            user=self.request.user).all()
        return context

    # 上だけだと、address登録時にカスタムしたUserテーブルからuser_idの外部キーが入らないので、エラーが出る
    # form_valid（formを送信する際にvalidationを行うメソッド）を上書きして、AddressInputFormのuserを登録する
    def form_valid(self, form):
        form.user = self.request.user
        return super().form_valid(form)


class ConfirmOrderView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('stores', 'confirm_order.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address = cache.get(f'address_user_{self.request.user.id}')
        context['address'] = address
        cart = get_object_or_404(Carts, user_id=self.request.user.id)
        context['cart'] = cart
        total_price = 0
        items = []
        for item in cart.cartitems_set.all():
            total_price += item.quantity * item.product.price
            picture = item.product.productpictures_set.first()
            picture = picture.picute if picture else None
            tmp_item = {
                'quantity': item.quantity,
                'picture': picture,
                'name': item.product.name,
                'price': item.product.price,
                'id': item.id,
            }
            items.append(tmp_item)
        context['total_price'] = total_price
        context['items'] = items
        return context

    # テンプレートからPOSTで注文確定が送られてきた時の処理
        """transaction.atomicデコレータを付けないとどうなるか。
        Orders, OrderItems,Products,Cartへの処理が、別々になって実行されてしまう。
        （注文テーブルにデータを入れる＞商品ストックを減らす＞カートテーブルを削除する）
        この４つの処理は、塊で全て実行されなくてはいけない、トランザクション（データのやり取り）処理。
        全てが実行されるか、全てが実行されないかの、いずれかでなくてはいけない。
        （DBの原子性を満たすという）
        transaction.atomicデコレータをつけることで、
        処理の途中でエラーが起きるなどした場合は、ロールバックされ、全て実行されない状態になる。
        """
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        address = context.get('address')
        cart = context.get('cart')
        total_price = context.get('total_price')
        if (not address) or (not cart) or (not total_price):
            raise Http404('注文処理でエラーが発生しました')
        for item in cart.cartitems_set.all():
            if item.quantity > item.product.stock:
                raise Http404('商品在庫が不足しています')
        # OrdersManagerモデルのinsert_cartを実行して、Ordersにデータを作成する
        order = Orders.objects.insert_cart(cart, address, total_price)
        # OrderItemsManagerモデルのinsert_cart_itemsを実行して、OrderItemsにデータを作成する
        OrderItems.objects.insert_cart_items(cart, order)
        # ProductsManagerのreduce_stockを実行して、在庫数からcartにある商品数を減らす
        Products.objects.reduce_stock(cart)
        # カートの中を削除する Cartsと、それに紐づくCartItemsの該当レコードが削除される
        cart.delete()
        return redirect(reverse_lazy('stores:order_success'))


class OrderSuccessView(LoginRequiredMixin, TemplateView):

    template_name = os.path.join('stores', 'order_success.html')
