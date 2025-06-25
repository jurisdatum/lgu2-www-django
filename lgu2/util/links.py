
from typing import Optional

from lgu2.api.browse_types import DocEntry


first_versions = { 'enacted', 'made', 'created', 'adopted' }


def make_contents_link(doc: DocEntry, lang: Optional[str]):
    prefix = '/cy/' if lang == 'cy' else '/'
    if doc['id'].endswith('.pdf'):  # correction slips
        return prefix + doc['id']
    suffix = '/' + doc['version'] if doc['version'] in first_versions else ''
    return prefix + doc['id'] + '/contents' + suffix
