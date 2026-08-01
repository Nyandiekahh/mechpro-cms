"""Google reCAPTCHA verification + client-IP helper (WRS spam protection)."""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def verify_recaptcha(token, ip=None):
    """
    Returns True when the token passes Google's check.
    If no secret key is configured (development), verification is skipped.
    """
    secret = settings.RECAPTCHA_SECRET_KEY
    if not secret:
        return True
    if not token:
        return False
    try:
        response = requests.post(
            settings.RECAPTCHA_VERIFY_URL,
            data={"secret": secret, "response": token, "remoteip": ip},
            timeout=8,
        )
        result = response.json()
        return bool(result.get("success"))
    except requests.RequestException as exc:
        # Fail-open would invite spam; fail-closed blocks customers on a
        # Google outage. We fail-open but log loudly — tune to taste.
        logger.error("reCAPTCHA verification unreachable: %s", exc)
        return True
