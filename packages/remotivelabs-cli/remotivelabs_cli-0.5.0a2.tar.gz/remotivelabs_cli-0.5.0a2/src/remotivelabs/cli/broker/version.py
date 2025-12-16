import semver


def ensure_version_is_at_least(version: str, min_version: str) -> None:
    """
    Ensures that broker version is at least a specific version.
    """

    try:
        # use finalize() to use the release version of this version regardless of pre-release or build
        broker_version = semver.parse_version_info(version).finalize_version()
        required_version = semver.parse_version_info(min_version).finalize_version()
    except ValueError as e:
        raise InvalidBrokerVersionError(str(e))

    if broker_version < required_version:
        raise UnsupportedBrokerVersionError(current_version=broker_version, min_version=min_version)


class UnsupportedBrokerVersionError(Exception):
    """Raised when broker version is below the minimum supported version."""

    def __init__(self, current_version: str, min_version: str):
        self.current_version = current_version
        self.min_version = min_version


class InvalidBrokerVersionError(Exception):
    """Raised when version is not major.minor.patch"""

    pass
