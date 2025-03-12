from django.http import HttpResponse
from django.template import loader
from ..models import Footer, AboutUsPage, AboutUsPageSubSection, StatusMessages

def about_us(request):
    footer_data = Footer.objects.all().first()
    about_us_data = AboutUsPage.objects.all().first()
    about_us_sub_sec = AboutUsPageSubSection.objects.all()

    data = {}
    data['footer'] = footer_data
    data['about_us_data'] = about_us_data
    data['about_us_sub_sec'] = about_us_sub_sec
    template = loader.get_template('browse/about_us.html')
    return HttpResponse(template.render(data, request))


def get_snippet_message(title=None, label=None, date=None, lang=None):
    if title is None and label is None and date is None:
        return ""
    
    message = StatusMessages.objects.get(title=title)
    content = message.message_in_english
    if lang is not None and lang == 'welsh' or lang == 'cy':
        content = message.message_in_welsh
    
    formatted_message = get_formatted_content(content, label, date)
    return formatted_message

def get_formatted_content(content, label, date):
    # Build the format arguments dictionary, excluding None values
    format_args = {}
    if label is not None:
        format_args[' label '] = label
    if date is not None:
        format_args[' date '] = date

    # Use str.format() with the prepared format arguments
    formatted_content = content.format(**format_args)
    return formatted_content

