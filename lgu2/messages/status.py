
from datetime import datetime
import re

from ..api.document import Meta

STATUS_WARNING_ORIGINAL_VERSION = "This is the original version (as it was originally {version})."

STATUS_WARNING_PIT_AT = "Point in time view as at {pit}."


def get_status_message(meta: Meta):

    status = meta['status']
    version = meta['version']

    if status == 'final':
        return STATUS_WARNING_ORIGINAL_VERSION.format(version=version)

    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', version):
        version_date = datetime.strptime(version, '%Y-%m-%d')
        pit = version_date.strftime("%d/%m/%Y")
        return STATUS_WARNING_PIT_AT.format(pit=pit)
