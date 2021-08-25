from django import forms
from .models import CartItems, Addresses
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.cache import cache


class CartUpdateForm(forms.ModelForm):
    quantity = forms.IntegerField(label='数量', min_value=1)
    id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = CartItems
        fields = ['quantity', 'id']

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        id = cleaned_data.get('id')
        cart_item = get_object_or_404(CartItems, pk=id)
        if quantity > cart_item.product.stock:
            raise ValidationError(
                f'在庫数を超えています。{cart_item.product.stock}以下で注文して下さい。')


class AddressInputForm(forms.ModelForm):
    address = forms.CharField(
        label='住所',
        widget=forms.TextInput(attrs={'size': '80'}),
    )

    class Meta:
        model = Addresses
        fields = ['zip_code', 'prefecture', 'address']
        # 以下は上のfield定義でlabelを指定することと同義
        labels = {
            'zip_code': '郵便番号',
            'prefecture': '都道府県'
        }

    # saveメソッドを上書きして、userを追加して送るようにする
    def save(self):
        address = super().save(commit=False)
        # selfはAddressInputFormのインスタンス。InputAddressViewのform_validでuserを渡すように上書きしているので、userを取り出せる。
        address.user = self.user

        # Addressesで制約したように、同じユーザーで同じ住所を重複登録させないようにする実装 ＊１
        # addressがユニークかどうかバリデーション。ユニークだった場合のみ保存。それ以外はエラー。保存したくないだけなので、pass。 *1
        try:
            address.validate_unique()
            address.save()
        except ValidationError:
            pass

        # addressをキャッシュに一時保存する
        cache.set(f'address_user_{self.user.id}', address)  # 指定した値にaddressを保存する
        return address
