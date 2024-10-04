
from django.utils.translation import gettext as _

def get_type_label_plural(type):
    if type == 'ukpga' or type == 'UnitedKingdomPublicGeneralAct':
        return _('UK Public General Acts')
    if type == 'uksi' or type == 'UnitedKingdomStatutoryInstrument':
        return _('UK Statutory Instruments')
    if type == 'wsi' or type == 'WelshStatutoryInstrument':
        return _('Wales Statutory Instruments')
    if type == 'nisi' or type == 'NorthernIrelandOrderInCouncil':
        return _('Northern Ireland Orders in Council')
