"""Constants for the CEZ HDO integration."""

DOMAIN = "cez_hdo"

# Configuration
CONF_EAN = "ean"
CONF_SIGNAL = "signal"

# Default values
DEFAULT_NAME = "CEZ HDO"
DEFAULT_SCAN_INTERVAL = 30  # 30 second
DEFAULT_SIGNAL = "a3b4dp01"

# Available signals
AVAILABLE_SIGNALS = ["a3b4dp01", "a3b4dp02", "a3b4dp06"]

# API
CEZ_API_URL = "https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani"
CEZ_API_ENDPOINT = "switch-times/signals"

# Headers for the API request
CEZ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Content-Type": "application/json",
    "Origin": "https://dip.cezdistribuce.cz",
    "Connection": "keep-alive",
    "Referer": "https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=0"
}
