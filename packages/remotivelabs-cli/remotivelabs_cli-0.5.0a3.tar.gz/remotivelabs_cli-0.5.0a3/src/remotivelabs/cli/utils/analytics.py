import uuid

from remotivelabs.cli.settings import settings


class NoConsentError(Exception):
    """Raised when anonymous user does not consent to analytics collection"""


def require_consent() -> None:
    if not settings.get_active_token() and not settings.get_device_id():
        acquire_consent()


def acquire_consent() -> None:
    consent = (
        input(
            """RemotiveLabs would like to collect anonymous usage data to improve our products.
No personal or sensitive information will be collected.
For more details, see our Privacy Policy: https://remotivelabs.com/privacy-policy

To use this tool, you must consent to anonymous usage analytics.

Do you consent to anonymous usage analytics? [y/N]:"""
        )
        .strip()
        .lower()
    )
    if consent != "y":
        raise NoConsentError()

    settings.set_device_id(uuid.uuid4().hex)
