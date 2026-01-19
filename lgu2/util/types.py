VALID_TYPES = [
    # Primary
    "all", "primary\+secondary", "primary", "ukpga", "ukla", "ukppa", "asp", "asc", "anaw", "mwa", "ukcm", "nia", 
    "aosp", "aep", "aip", "apgb", "gbla", "gbppa", "nisi", "mnia", "apni",
    # Secondary
    "secondary", "uksi", "wsi", "ssi", "nisr", "ukci", "ukmd", "ukmo", "uksro", "nisro",
    # EU
    "eu-origin", "eu", "eur", "eudn", "eudr", "eut", 
    # Associated 
    "ukia"
]

EXTENT_MAP = {
    "E": "england",
    "W": "wales",
    "S": "scotland",
    "NI": "ni"
}


types = [
    ('ukpga', 'UnitedKingdomPublicGeneralAct', 'primary'),
    ('ukla', 'UnitedKingdomLocalAct', 'primary'),
    ('ukppa', 'UnitedKingdomPrivateOrPersonalAct', 'primary'),
    ('asp', 'ScottishAct', 'primary'),
    ('nia', 'NorthernIrelandAct', 'primary'),
    ('aosp', 'ScottishOldAct', 'primary'),
    ('aep', 'EnglandAct', 'primary'),
    ('aip', 'IrelandAct', 'primary'),
    ('apgb', 'GreatBritainAct', 'primary'),
    ('gbla', 'GreatBritainLocalAct', 'primary'),
    ('gbppa', '???', 'primary'),  # ToDo
    ('anaw', 'WelshNationalAssemblyAct', 'primary'),
    ('asc', 'WelshParliamentAct', 'primary'),
    ('mwa', 'WelshAssemblyMeasure', 'primary'),
    ('ukcm', 'UnitedKingdomChurchMeasure', 'primary'),
    ('mnia', 'NorthernIrelandAssemblyMeasure', 'primary'),
    ('apni', 'NorthernIrelandParliamentAct', 'primary'),
    ('uksi', 'UnitedKingdomStatutoryInstrument', 'secondary'),
    ('ukmd', 'UnitedKingdomMinisterialDirection', 'secondary'),
    ('ukmo', 'UnitedKingdomMinisterialOrder', 'secondary'),
    ('uksro', 'UnitedKingdomStatutoryRuleOrOrder', 'secondary'),
    ('wsi', 'WelshStatutoryInstrument', 'secondary'),
    ('ssi', 'ScottishStatutoryInstrument', 'secondary'),
    ('nisi', 'NorthernIrelandOrderInCouncil', 'secondary'),
    ('nisr', 'NorthernIrelandStatutoryRule', 'secondary'),
    ('ukci', 'UnitedKingdomChurchInstrument', 'secondary'),
    ('nisro', 'NorthernIrelandStatutoryRuleOrOrder', 'secondary'),

    ('ukdsi', 'UnitedKingdomDraftStatutoryInstrument', 'secondary'),
    ('sdsi', 'ScottishDraftStatutoryInstrument', 'secondary'),
    ('nidsr', 'NorthernIrelandDraftStatutoryRule', 'secondary'),

    ('eur', 'EuropeanUnionRegulation', 'euretained'),
    ('eudn', 'EuropeanUnionDecision', 'euretained'),
    ('eudr', 'EuropeanUnionDirective', 'euretained'),
    ('eut', 'EuropeanUnionTreaty', 'euretained')
]

short_to_long = {item[0]: item[1] for item in types}

long_to_short = {item[1]: item[0] for item in types}

categories_by_type = {item[0]: item[2] for item in types} | {item[1]: item[2] for item in types}


def to_short_type(type):
    if type in short_to_long:
        return type
    if type in long_to_short:
        return long_to_short[type]
    print("can't find short type for", type)


def get_category(type):
    if type in categories_by_type:
        return categories_by_type[type]
