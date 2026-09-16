INTENTS = [
    "performance_stability", "keyboard_input", "battery_charging",
    "connectivity", "apps_services", "media_data", "account_auth",
    "payments_purchases", "communication", "hardware_accessories",
]

# The ordering resolves keyword ties deterministically. These are deliberately
# conservative discovery rules, not a claim of human annotation.
INTENT_KEYWORDS = {
    "performance_stability": ["freez", "lag", "crash", "overheat", "restart", "slow", "stuck", "reboot"],
    "keyboard_input": ["keyboard", "autocorrect", "typing", "type ", "paste", "letter", "emoji", "input"],
    "battery_charging": ["battery", "charging", "charger", "charge ", "shutdown", "power drain"],
    "connectivity": ["wifi", "wi-fi", "bluetooth", "cellular", "network", "gps", "signal", "internet"],
    "apps_services": [" app", "apps", "app ", "safari", "itunes", "apple music", "facetime app"],
    "media_data": ["icloud", "photo", "photos", "music", "backup", "data", "sync", "storage"],
    "account_auth": ["apple id", "password", "verification", "2fa", "two factor", "sign in", "login", "locked out"],
    "payments_purchases": ["billing", "purchase", "subscription", "refund", "applecare", "charged", "payment", "invoice"],
    "communication": ["imessage", "message", "messages", "texting", "text ", "call", "calls", "facetime"],
    "hardware_accessories": ["screen", "camera", "speaker", "button", "airpod", "headphone", "headphones", "iphone x"],
}

HIGH_RISK = {"account_auth", "payments_purchases"}
