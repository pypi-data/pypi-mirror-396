from typing import Tuple, List
from dataclasses import dataclass

"""
    <DeviceIdentity vendorId="65535" deviceId="1" vendorName="IO-Link Community">
      <VendorText textId="T_VendorText"/>
      <VendorUrl textId="T_VendorUrl"/>
      <VendorLogo name="IO-Link-logo.png"/>
      <DeviceName textId="T_DeviceName"/>
      <DeviceFamily textId="T_DeviceFamily"/>
      <DeviceVariantCollection>
        <DeviceVariant productId="ioddsample01" deviceSymbol="IO-Link-Device-pic.png" deviceIcon="IO-Link-Device-icon.png">
          <Name textId="TN_ProductName"/>
          <Description textId="TD_ProductDescr"/>
        </DeviceVariant>
      </DeviceVariantCollection>
    </DeviceIdentity>
"""


@dataclass
class DeviceVariant:
    productId: str = ''
    deviceSymbol: str = '' #  filename
    deviceIcon: str = '' #  filename
    name: Tuple[str, str] = ('', '')  #  textId, text
    description: Tuple[str, str] = ('', '')  #  textId, text


class Identity:
    def __init__(self):
        self.vendorId: int = 0
        self.deviceId: int = 0
        self.vendorName: str = ''
        self.vendorText: Tuple[str, str] = ('', '')  # textId, text
        self.vendorUrl: Tuple[str, str] = ('', '')  # textId, text
        self.vendorLogo: str = ''
        self.deviceName: Tuple[str, str] = ('', '')  # textId, text
        self.deviceFamily: Tuple[str, str] = ('', '')  # textId, text

        self.deviceVariants: List[DeviceVariant] = []

    def __str__(self):  # pragma: no cover
        return (
            f"Identity("
            f"vendorId={self.vendorId}, "
            f"deviceId={self.deviceId}, "
            f"vendorName={self.vendorName}, "
            f")"
        )
