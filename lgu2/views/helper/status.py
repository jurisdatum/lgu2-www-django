
from typing import Optional, TypedDict

from ...api.document import CommonMetadata


class StatusMessage(TypedDict):
    heading: str
    body: str


def make_pdf_status_message(meta: CommonMetadata) -> Optional[StatusMessage]:
    """Return a status message to display alongside a PDF rendering, or None.

    Currently the King's Printer copy is shown only for the enacted version
    of an Act; other document types and revised versions get no message.
    """
    if meta['version'] != 'enacted':
        return None
    return {
        'heading': "This is the King's Printer Version. It is the exact text that received Royal Assent when it was enacted.",
        'body': "A version of this text with commencement and extent information should be available by.",
    }
