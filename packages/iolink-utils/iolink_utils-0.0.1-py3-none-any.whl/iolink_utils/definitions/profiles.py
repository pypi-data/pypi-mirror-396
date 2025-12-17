from enum import IntEnum

# values and names are taken from IOL_ProfileIDOverview_V11_Mar2023.pdf and IODDs
class ProfileID(IntEnum):
    Unknown = 0
    GenericProfiledSensor = 1
    FixedSwitchingSensor = 2
    FSS_3 = 3
    AdSS_4 = 4
    AdSS_5 = 5
    AdSS_6 = 6
    AdSS_7 = 7
    AdSS_8 = 8
    AdSS_9 = 9
    MeasuringSensor = 10
    MeasuringSensorHighRes = 11
    MeasuringSensorDisableFunc = 12
    MeasuringSensorHighResDisableFunc = 13
    AdjustableSwitchingSensorTwoChannel = 14
    DMSS1ch = 16
    DMSS2ch = 17
    DMSS3ch = 18
    DMSS4ch = 19
    DMSSHighRes1ch = 20
    DMSSHighRes2ch = 21
    DMSSHighRes3ch = 22
    DMSSHighRes4ch = 23
    DMSSFloat1ch = 24
    DMSSFloat2ch = 25
    DMSSFloat3ch = 26
    DMSSFloat4ch = 27

    BLOB = 48
    FWUPD = 49
    IdentificationDiagnosis = 16384
    SafetyDevice = 16385
    WirelessDevice = 16386

    DeviceIdentification = 32768
    MultiChannelTwoPointSwitchingSensor = 32769
    ProcessDataVariable = 32770
    DeviceDiagnosis = 32771
    TeachChannel = 32772
    FixedSwitchingSignalChannel = 32773
    AdjustableSwitchingSignalChannel = 32774
    TeachSingleValue = 32775
    TeachTwoValue = 32776
    TeachDynamic = 32777
    MeasurementDataChannelStandardResolution = 32778
    MeasurementDataChannelHighResolution = 32779
    SensorControl = 32780
    MultipleAdjustableSwitchingSignalChannel = 32781
    MeasurementDataChannelFloat = 32782
    SensorControlWide = 32783
    MultiTeachSingleValue = 32784
    MultiTeachTwoValueExtension = 32785
    MultiTeachDynamicExtension = 32786
    ObjectDetection = 32787
    QuantityDetection = 32788
    QuantityDetectionAbsolute = 32789
    NoName_32790 = 32790
    UncertaintyIndication = 32791
    ReservedSafety = 32800
    IOLWirelessBridge = 32816
    ExtendedIdentification = 33024
    Locator = 33025
    ProductURI = 33026
    TeachRecommended = 33027
    BlobTransfer = 36608

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown
