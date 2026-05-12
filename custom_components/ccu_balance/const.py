"""Constants for CCU Balance integration."""

DOMAIN = "ccu_balance"

CONF_LOGIN = "login"
CONF_PASSWORD = "password"
CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

# Legacy option from versions where interval was stored in seconds.
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_UPDATE_INTERVAL_HOURS = 6
MIN_UPDATE_INTERVAL_HOURS = 1
MAX_UPDATE_INTERVAL_HOURS = 24

URL = "https://ccu.su/data.cgx"
CMD = {"Command": "GetStateAndEvents"}
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
