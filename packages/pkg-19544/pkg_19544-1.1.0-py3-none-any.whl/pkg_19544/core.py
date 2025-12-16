from urllib.parse import urlunsplit

from .helpers.evaluate import (
    _has_allowed_scheme,
    _has_no_basic_auth,
    _has_no_control_character,
    _has_valid_fqdn_label,
    _has_valid_fqdn_syntax,
    _has_valid_tld,
    _has_valid_tls,
    _is_fqdn_ipaddr_public_routable,
    _is_fqdn_resolvable,
)
from .helpers.sanitize import _encode_url_components, _remove_control_characters
from .utils.url import get_url_components


def evaluate_url(user_url: str) -> bool:
    scheme, userinfo, netloc, fqdn, _ = get_url_components(user_url)
    try:
        if all([
            _has_allowed_scheme(user_url),
            _has_no_basic_auth(userinfo),
            _has_no_control_character(user_url),
            _has_valid_fqdn_syntax(fqdn),
            _has_valid_fqdn_label(fqdn),
            _has_valid_tld(fqdn),
            _is_fqdn_resolvable(scheme, fqdn),
            _is_fqdn_ipaddr_public_routable(scheme, fqdn),
            _has_valid_tls(netloc, fqdn),
        ]):
            return True
        else:
            return False  # pragma: no cover
    except ValueError:
        return False


def sanitize_url(user_url: str) -> str:
    user_url = _remove_control_characters(user_url)
    scheme, _, netloc, _, pre_parsed_path = get_url_components(user_url)
    encoded_path, encoded_query, encoded_fragment = _encode_url_components(pre_parsed_path)

    url_components = (scheme, netloc, encoded_path, encoded_query, encoded_fragment)
    return urlunsplit(url_components)
