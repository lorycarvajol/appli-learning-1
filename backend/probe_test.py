from django.test import override_settings
from apps.accounts.throttling import FailedLoginThrottle as T

def test_sonde():
    print('\nHORS override :', T.THROTTLE_RATES, '| rate =', T().rate)
    with override_settings(REST_FRAMEWORK={'DEFAULT_THROTTLE_RATES': {'login': '3/hour'}}):
        print('SOUS override :', T.THROTTLE_RATES, '| rate =', T().rate)
