from enum import Enum


class DocType(Enum):
    STS: str = "sts"
    DRIVER_LICENSE_FRONT: str = "driver_license_front"
    DRIVER_LICENSE_BACK: str = "driver_license_back"
    PASSPORT: str = "passport"
    ORG_CARD: str = "org_card"
