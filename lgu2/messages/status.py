
from datetime import datetime
# import re
# from typing import Optional
from ..views.wagtail import get_snippet_message
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
    label = meta['title']
    date = datetime.now().strftime('%d %B %Y')
    if meta['upToDate']:
        return get_snippet_message('status_message_up_to_date', label, date, meta['lang'])
    else:
        return get_snippet_message('status_message_outstanding', label, None, meta['lang'])


def get_status_message_for_fragment(meta: FragmentMetadata) -> str:
    label = meta['title'] + ', ' + meta['fragmentInfo']['label']
    date = datetime.now().strftime('%d %B %Y')
    if meta['upToDate']:
        return get_snippet_message('status_message_up_to_date', label, date, meta['lang'])
    else:
        get_snippet_message('status_message_outstanding', label, None, meta['lang'])

