from typing import TypedDict


class HidDeviceInfo(TypedDict):
    path: str
    vendor_id: int
    product_id: int
    serial_number: str
    release_number: int
    manufacturer_string: str
    product_string: str
    usage_page: int
    usage: int
    interface_number: int
