# Ordersテーブルにアクセスして、情報をファイルに出力するバッチ処理

from django.core.management.base import BaseCommand
from stores.models import Orders
from ecsite_project.settings import BASE_DIR
from datetime import datetime
import os
import csv


class Command(BaseCommand):

    # user_idを渡して実行できるように
    def add_arguments(self, parser):
        parser.add_argument('--user_id', default='all')  # defaultはallを入れる

    def handle(self, *args, **options):
        orders = Orders.objects

        user_id = options['user_id']
        if user_id == 'all':  # allが入っていたら、全部取得
            orders = orders.all()
        else:  # user_idが入っていたらuser_idでfilter
            orders = orders.filter(user_id=user_id)

        file_path = os.path.join(
            BASE_DIR,
            'output',
            'orders',
            f'orders_{datetime.now().strftime("%Y%m%d%H%M%S")}'
        )
        with open(file_path, mode='w', newline='\n', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'user', 'address', 'total_price']
            # https://docs.python.org/ja/3/library/csv.html#csv.DictWriter
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # https://docs.python.org/ja/3/library/csv.html#csv.DictWriter.writeheader
            writer.writeheader()
            for order in orders:
                # https://docs.python.org/ja/3/library/csv.html#csv.csvwriter.writerow
                writer.writerow({
                    'id': order.id,
                    'user': order.user,
                    'address': order.address,
                    'total_price': order.total_price,
                })
