from urllib.parse import quote_plus, urlsplit

from ..configs.constants import BLACKLIST_CONTROL_CHARACTERS


def _remove_control_characters(user_url: str) -> str:
    updated_url = user_url.strip()
    for chars in BLACKLIST_CONTROL_CHARACTERS:
        updated_url = updated_url.replace(chars, "")
    return updated_url


def _encode_url_components(pre_parsed_path) -> tuple[str, str, str]:
    encoded_path = quote_plus(urlsplit(pre_parsed_path).path, safe="/+")
    encoded_query = quote_plus(urlsplit(pre_parsed_path).query, safe="?&=")
    encoded_fragment = quote_plus(urlsplit(pre_parsed_path).fragment, safe="#")
    return (encoded_path, encoded_query, encoded_fragment)
