from urllib import error, request

from ..configs.constants import TLD_LIST, TLD_LIVE


def get_tlds() -> bool:
    try:
        with request.urlopen(TLD_LIVE) as response:
            html_bytes = response.read()
            html_string = html_bytes.decode('utf-8')
            list_tld = html_string.splitlines()[1:]

            with open(TLD_LIST, 'w') as f:
                tld_key = "TLDS"
                tld_val = str(list_tld).replace(" ", "\r\n    ").replace("['", "[\r\n    '").replace("]", "]\r\n")
                f.write(f'{tld_key} = {tld_val}')
            return True

    except (error.URLError, ValueError):  # pragma: no cover
        return False
