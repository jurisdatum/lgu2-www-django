# home/models.py
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.db import models
from wagtail.fields import RichTextField  # Import RichTextField

@register_snippet
class Footer(models.Model):
    """Model to store footer content."""    
    # Text fields for different languages
    copyright_statement_en = RichTextField(blank=True, help_text="Copyright statement in English")
    copyright_statement_cy = RichTextField(blank=True, help_text="Copyright statement in Welsh")

    panels = [
        FieldPanel('copyright_statement_en'),
        FieldPanel('copyright_statement_cy'),
    ]

    def __str__(self):
        return 'Footer Content'

@register_snippet
class AboutUsPage(models.Model):
    main_heading = models.CharField(max_length=255, blank=True)
    subheading_1 = models.CharField(max_length=255, blank=True)
    introduction_subheading_1 = RichTextField(help_text="Introduction text for About this website section", blank=True)
    
    panels = [
        FieldPanel('main_heading'),
        FieldPanel('subheading_1'),
        FieldPanel('introduction_subheading_1'),        
    ]

    def __str__(self):
        return self.main_heading


@register_snippet
class AboutUsPageSubSection(models.Model):
    subheading_2 = models.CharField(max_length=255)
    introduction_subheading_2 = RichTextField(help_text="Introduction text for About us", blank=True)
    
    panels = [
        FieldPanel('subheading_2'),
        FieldPanel('introduction_subheading_2'),
    ]

    def __str__(self):
        return self.subheading_2
    