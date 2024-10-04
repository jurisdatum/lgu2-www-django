
def to_short_type(type):
    if type == 'ukpga' or type == 'UnitedKingdomPublicGeneralAct':
        return 'ukpga'
    if type == 'uksi' or type == 'UnitedKingdomStatutoryInstrument':
        return 'uksi'
    if type == 'wsi' or type == 'WelshStatutoryInstrument':
        return 'wsi'
    if type == 'nisi' or type == 'NorthernIrelandOrderInCouncil':
        return 'nisi'
