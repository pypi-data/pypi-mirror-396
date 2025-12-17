from ._processDataDecoderInternal import _createPDDecoderClass, _safetyCodeOutFields, _safetyCodeInFields


def createDecoderClass_PDIn(json_process_data_def, condition=None):
    return _createPDDecoderClass(json_process_data_def[condition]['pdIn']['dataFormat'], _safetyCodeInFields)

def createDecoderClass_PDOut(json_process_data_def, condition=None):
    return _createPDDecoderClass(json_process_data_def[condition]['pdOut']['dataFormat'], _safetyCodeOutFields)
