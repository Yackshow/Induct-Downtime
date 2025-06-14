# Logging configuration to suppress noisy warnings
import logging

# Suppress Kerberos authentication warnings
logging.getLogger('requests_kerberos').setLevel(logging.ERROR)
logging.getLogger('spnego').setLevel(logging.ERROR)
logging.getLogger('gssapi').setLevel(logging.ERROR)

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
