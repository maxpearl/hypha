import datetime
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.search import index

from opentech.public.utils.models import BasePage, RelatedPage

from opentech.public.funds.models import FundPage, LabPage, RFPPage

from .blocks import OurWorkBlock


class PromotedFunds(RelatedPage):
    source_page = ParentalKey(
        'home.HomePage',
        related_name='promoted_funds'
    )

    class Meta(RelatedPage.Meta):
        unique_together = ('page',)

    panels = [
        PageChooserPanel('page', 'public_funds.FundPage'),
    ]


class PromotedLabs(RelatedPage):
    source_page = ParentalKey(
        'home.HomePage',
        related_name='promoted_labs'
    )

    class Meta(RelatedPage.Meta):
        unique_together = ('page',)

    panels = [
        PageChooserPanel('page', 'public_funds.LabPage'),
    ]


class PromotedRFPs(RelatedPage):
    source_page = ParentalKey(
        'home.HomePage',
        related_name='promoted_rfps'
    )

    class Meta(RelatedPage.Meta):
        unique_together = ('page',)

    panels = [
        PageChooserPanel('page', 'public_funds.RFPPage'),
    ]


class HomePage(BasePage):
    # Only allow creating HomePages at the root level
    parent_page_types = ['wagtailcore.Page']

    NUM_RELATED = 6

    strapline = models.CharField(blank=True, max_length=255)
    strapline_link = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.PROTECT)
    strapline_link_text = models.CharField(max_length=255)

    our_work_title = models.CharField(max_length=255)
    our_work = StreamField([
        ('work', OurWorkBlock()),
    ])
    our_work_link = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.PROTECT)
    our_work_link_text = models.CharField(max_length=255)

    funds_title = models.CharField(max_length=255)
    funds_intro = models.TextField(blank=True)
    funds_link = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.PROTECT)
    funds_link_text = models.CharField(max_length=255)

    labs_title = models.CharField(max_length=255)
    labs_intro = models.TextField(blank=True)
    labs_link = models.ForeignKey('wagtailcore.Page', related_name='+', on_delete=models.PROTECT)
    labs_link_text = models.CharField(max_length=255)

    rfps_title = models.CharField(max_length=255)
    rfps_intro = models.TextField(blank=True)

    search_fields = BasePage.search_fields + [
        index.SearchField('strapline'),
    ]

    content_panels = BasePage.content_panels + [
        MultiFieldPanel([
            FieldPanel('strapline'),
            PageChooserPanel('strapline_link'),
            FieldPanel('strapline_link_text'),
        ], heading='Introduction'),
        MultiFieldPanel([
            FieldPanel('our_work_title'),
            StreamFieldPanel('our_work'),
            PageChooserPanel('our_work_link'),
            FieldPanel('our_work_link_text'),
        ], heading='Our Work'),
        MultiFieldPanel([
            FieldPanel('funds_title'),
            FieldPanel('funds_intro'),
            InlinePanel('promoted_funds', label='Promoted Funds', max_num=NUM_RELATED),
            PageChooserPanel('funds_link'),
            FieldPanel('funds_link_text'),
        ], heading='Funds'),
        MultiFieldPanel([
            FieldPanel('labs_title'),
            FieldPanel('labs_intro'),
            InlinePanel('promoted_labs', label='Promoted Labs', max_num=NUM_RELATED),
            PageChooserPanel('labs_link'),
            FieldPanel('labs_link_text'),
        ], heading='Labs'),
        MultiFieldPanel([
            FieldPanel('rfps_title'),
            FieldPanel('rfps_intro'),
            InlinePanel('promoted_rfps', label='Promoted RFPs', max_num=NUM_RELATED),
        ], heading='Labs'),
    ]

    def get_related(self, page_type, base_list):
        related = page_type.objects.filter(id__in=base_list.values_list('page')).live().public()
        yield from related
        selected = list(related.values_list('id', flat=True))
        extra_needed = self.NUM_RELATED - len(selected)
        extra_qs = page_type.objects.public().live().exclude(id__in=selected)
        displayed = 0
        for page in self.sorted_by_deadline(extra_qs):
            if page.is_open:
                yield page
                displayed += 1
            if displayed >= extra_needed:
                break

    def sorted_by_deadline(self, qs):
        def sort_by_deadline(value):
            try:
                return value.deadline or datetime.date.max
            except AttributeError:
                return datetime.date.max

        yield from sorted(qs, key=sort_by_deadline)

    def pages_from_related(self, related):
        for related in related.all():
            if related.page.live and related.page.public:
                yield related.page.specific

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['lab_list'] = list(self.get_related(LabPage, self.promoted_labs))
        context['fund_list'] = list(self.get_related(FundPage, self.promoted_funds))
        context['rfps_list'] = list(self.get_related(RFPPage, self.promoted_rfps))
        return context
