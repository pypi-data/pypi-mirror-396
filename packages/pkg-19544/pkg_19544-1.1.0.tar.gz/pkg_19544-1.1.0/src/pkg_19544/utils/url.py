from typing import Tuple
from urllib.parse import urlparse


# http(s)://username:password@hostname.example.com:8042/path4/path44?key1=value1&key2=value2#section
# \_____/   \_______________/ \__________________/ \__/\___________/ \_____________________/ \_____/
#    |              |                   |            |        |                  |               |
# scheme        userinfo              fqdn         port      path              query        fragment
#           \_________________________________________/\___________________________________________/
#                                |                                         |
#                         authority/netloc                         pre-parsed path


def get_url_components(user_url: str) -> Tuple[str, str, str, str, str]:
    scheme = urlparse(user_url).scheme
    netloc = urlparse(user_url).netloc
    userinfo = netloc.split('@')[0] if "@" in netloc else ''
    netloc = netloc.split(f'{userinfo}@', maxsplit=1)[1] if f"{userinfo}@" in netloc else netloc
    fqdn = netloc.split(':')[0]
    pre_parsed_path = user_url.split(netloc, maxsplit=1)[1]

    return (scheme, userinfo, netloc, fqdn, pre_parsed_path)
