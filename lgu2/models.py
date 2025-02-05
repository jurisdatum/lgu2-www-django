# home/models.py
from wagtail.models import Page
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.db import models
from wagtail.fields import RichTextField  # Import RichTextField
from wagtail.models import PreviewableMixin, RevisionMixin

@register_snippet
class Footer(RevisionMixin, PreviewableMixin, models.Model):
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
    
    def get_preview_template(self, request, preview_mode):
        return f'browse/footer.html'
    
    def get_preview_context(self, request, preview_mode):
        return {'footer': self}

@register_snippet
class AboutUsPage(RevisionMixin, PreviewableMixin, models.Model):
    main_heading = models.CharField(max_length=255, blank=True)
    subheading_1 = models.CharField(max_length=255, blank=True)
    introduction_subheading_1 = RichTextField(help_text="Introduction text for About this website section", blank=True)
    
    content_panels = [
        FieldPanel('main_heading'),
        FieldPanel('subheading_1'),
        FieldPanel('introduction_subheading_1'),        
    ]

    def __str__(self):
        return self.main_heading
    
    def get_preview_template(self, request, preview_mode):
        return f'browse/about_us.html'
    
    def get_preview_context(self, request, preview_mode):
        return {'about_us_data': self}


@register_snippet
class AboutUsPageSubSection(RevisionMixin, PreviewableMixin, models.Model):
    subheading_2 = models.CharField(max_length=255)
    introduction_subheading_2 = RichTextField(help_text="Introduction text for About us", blank=True)
    
    content_panels = [
        FieldPanel('subheading_2'),
        FieldPanel('introduction_subheading_2'),
    ]

    def __str__(self):
        return self.subheading_2
    
    def get_preview_template(self, request, preview_mode):
        return f'browse/about_us.html'
    
    def get_preview_context(self, request, preview_mode):
        context = {
            'about_us_data': AboutUsPage.objects.all().first(),
            'about_us_sub_sec': list(AboutUsPageSubSection.objects.all().exclude(id=self.id))  # Convert QuerySet to list
        }
        
        # Now you can append the current object (`self`)
        context['about_us_sub_sec'].append(self)
        context['about_us_sub_sec'].sort(key=lambda x: x.id != self.id)  # This ensures 'self' comes first
        
        return context
    

# myapp/models.py
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from django.db import models

class HelpPage(Page):
    body = models.TextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

    def get_preview_template(self, request, preview_mode):
        return f'browse/help_guide.html'

