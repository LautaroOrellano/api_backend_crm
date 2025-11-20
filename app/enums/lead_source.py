from enum import Enum

class LeadSource(str, Enum):
    MANUAL = "manual"
    GOOGLE_MAPS = "google_maps"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    WEB = "web"