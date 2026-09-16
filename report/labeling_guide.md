# AppleSupport labeling guide

Review `data/labels/golden_review_template.csv` independently and save the completed copy as `data/labels/golden_labels.csv`. Use exactly one intent and one routing label per row. This file is intentionally blank: it must not be represented as human-labelled until a person has completed it.

| Intent | Include | Boundary |
|---|---|---|
| performance_stability | freezes, lag, crashes, heat, restarts | An update is context, not an intent. Label the resulting issue. |
| keyboard_input | typing, autocorrect, paste, keyboard/character problems | Media keys controlling an app are `apps_services`. |
| battery_charging | drain, charging, power-related shutdown | A broken physical cable/port is `hardware_accessories`. |
| connectivity | Wi-Fi, Bluetooth, cellular, GPS/network | iMessage delivery belongs to `communication`. |
| apps_services | apps/services fail, including Safari/iTunes | Missing photos/music/iCloud content is `media_data`. |
| media_data | photos, music, iCloud, backup/sync/content loss | Account sign-in is `account_auth`. |
| account_auth | Apple ID, password, verification/2FA | Route `ESCALATE` unless clearly generic and safe. |
| payments_purchases | billing, refund, subscription, AppleCare | Route `ESCALATE`. |
| communication | calls, Messages/iMessage, FaceTime | Network setup alone is `connectivity`. |
| hardware_accessories | screen/camera/buttons/speakers/AirPods/physical accessories | Software performance is not hardware. |

For multi-intent posts, select the primary actionable problem and say why in `notes`. Label `ESCALATE` for account/payment issues, identity/account-specific information, ambiguity, or unsupported/unsafe troubleshooting; otherwise use `AUTO_HANDLE` only when a general, historically supported response would be safe.
