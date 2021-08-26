from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help='このバッチはユーザー処理を行うバッチです'  # helpを実行した際に表示される内容

    # commandで引数を渡せるようにする
    def add_arguments(self, parser):
        # 第１位置引数の指定
        parser.add_argument(
            'name',
            type=str,
            help='名前',
            )
        # 第２位置引数の指定
        parser.add_argument(
            'age',
            type=int,
            help='年齢',
            )
        # キーワード引数の指定（options）
        parser.add_argument(
            '--birthday',
            default='1900-01-01',  # --birthdayをつけなかった時にデフォルトで入る値
            )
        # 第３位置引数の指定
        parser.add_argument(
            'three_words',
            nargs=3,  # 引数を３つ取り'three_wordsにリストで格納する'
            )
        # キーワード引数の指定（options）
        parser.add_argument(
            '--active',
            action='store_true',  # --activeをつけると、Trueが格納される（つけないとFalse）
            )
        # キーワード引数の指定（options）
        parser.add_argument(
            '--color',
            choices=['Blue', 'Red', 'Yellow'],
            )

    def handle(self, *args, **options):
        # 引数を取り出す
        name = options['name']
        age = options['age']
        birthday = options['birthday']
        three_words = options['three_words']
        active = options['active']

        print(f'name = {name}, age = {age}, birthday = {birthday}, three_words = {three_words}, {active}')

        color = options['color']
        if color == 'Blue':
            print('青')
        elif color == 'Red':
            print('赤')
        elif color == 'Yellow':
            print('黄')
