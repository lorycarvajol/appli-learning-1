import pytest
from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APIClient
from apps.accounts.models import User

pytestmark = pytest.mark.django_db

@override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {'login': '3/hour'}})
def test_qui_bloque():
    cache.clear()
    User.objects.create_user(email='eve@example.com', password='fixture-pwd-not-a-real-secret')
    from apps.accounts.views import LoginView
    for i in range(5):
        r = APIClient().post('/api/auth/login/', {'email': 'eve@example.com', 'password': 'faux'}, format='json')
        print(f'  essai {i+1}: {r.status_code}')
        if r.status_code == 429:
            v = LoginView()
            print('  throttles de la vue :', v.get_throttles())
            print('  rate :', [t.rate for t in v.get_throttles()])
            break
