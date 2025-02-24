
from datetime import datetime
# import re
# from typing import Optional

from ..api.document import CommonMetadata
from ..api.fragment import FragmentMetadata

# STATUS_WARNING_ORIGINAL_VERSION = "This is the original version (as it was originally {version})."

# STATUS_WARNING_PIT_AT = "Point in time view as at {pit}."


# def get_status_message(meta: CommonMetadata):

#     status = meta['status']
#     version = meta['version']

#     if status == 'final':
#         return STATUS_WARNING_ORIGINAL_VERSION.format(version=version)

#     if re.fullmatch(r'\d{4}-\d{2}-\d{2}', version):
#         version_date = datetime.strptime(version, '%Y-%m-%d')
#         pit = version_date.strftime("%d/%m/%Y")
#         return STATUS_WARNING_PIT_AT.format(pit=pit)


def get_status_message(meta: CommonMetadata) -> str:
    doc_title = meta['title']
    today = datetime.now().strftime('%d %B %Y')
    if meta['upToDate']:
        return f'{ doc_title } is up to date with all changes known to be in force on or before { today }.'
    else:
        return f'There are outstanding changes not yet made by the legislation.gov.uk editorial team to { doc_title }. Any changes that have already been made by the team appear in the content and are referenced with annotations.'


def get_status_message_for_fragment(meta: FragmentMetadata) -> str:
    doc_title = meta['title']
    frag_label = meta['fragmentInfo']['label']
    today = datetime.now().strftime('%d %B %Y')
    if meta['upToDate']:
        return f'{ doc_title }, { frag_label } is up to date with all changes known to be in force on or before { today }.'
    else:
        return f'There are outstanding changes not yet made by the legislation.gov.uk editorial team to { doc_title }. Any changes that have already been made by the team appear in the content and are referenced with annotations.'

