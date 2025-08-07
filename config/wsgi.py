"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Django を初期化してコマンドを実行可能にする
django.setup()

# ---- ここから初期化処理 ----
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import OperationalError

try:
    # マイグレーションを実行
    call_command('migrate', interactive=False)

    # スーパーユーザーが存在しない場合のみ作成
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        import os
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'morijyobi')
        User.objects.create_superuser(username=username, email=email, password=password)
except OperationalError as e:
    # DBが起動していないなど、初期タイミングのエラー対処
    print("Database not ready yet:", e)