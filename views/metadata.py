
import asyncio

from django.http import HttpResponse
from django.template import loader

from .. import api

def metadata(request, type, year, number):
    data = api.get_metadata(type, year, number)
    template = loader.get_template('metadata/metadata.html')
    context = { 'item': data }
    return HttpResponse(template.render(context, request))

async def _get_document_async(type, year, number):
    return api.get_document(type, year, number)

async def _get_metadata_async(type, year, number):
    return api.get_metadata(type, year, number)

async def combined(request, type, year, number):
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(_get_document_async(type, year, number))
        task2 = tg.create_task(_get_metadata_async(type, year, number))
    data = await task1
    meta = await task2
    template = loader.get_template('metadata/combined.html')
    context = { 'meta1': data['meta'], 'meta2': { 'item': meta } }
    return HttpResponse(template.render(context, request))
