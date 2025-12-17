from enum import Enum

class LeadStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    LOST = "LOST"