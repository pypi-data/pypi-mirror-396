# configs/constants.py

BLACKLIST_CIPHERS = ['ANON', 'EXPORT', 'NULL']
BLACKLIST_CONTROL_CHARACTERS = ['\n', '\r']

SOCKET_TIMEOUT = 5

TLD_LIST = "src/pkg_19544/configs/tlds.py"
TLD_LIVE = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"

# TLS_MIN_VERSION = "TLSv1.3"

WHITELIST_CHARS_IN_FQDN = r"^[a-zA-Z0-9\.\-]+$"
WHITELIST_HASHING_ALG = ('SHA256', 'SHA384', 'SHA512')
WHITELIST_PROTO_SCHEME = ('https://')
WHITELIST_TLS_VERSION = ['TLSv1.3']
