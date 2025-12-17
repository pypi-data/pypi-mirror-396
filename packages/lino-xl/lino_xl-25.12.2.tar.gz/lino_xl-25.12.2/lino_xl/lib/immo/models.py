# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.conf import settings
from lino.api import dd, rt, _
from lino.core import constants
from lino.modlib.users.mixins import UserAuthored
from lino.modlib.users.mixins import PrivacyRelevant
from lino.modlib.bootstrap5 import PAGE_TITLE_TEMPLATE
from lino.modlib.publisher.mixins import Publishable, PublishableContent, Illustrated
from lino.modlib.comments.mixins import Commentable
from lino.modlib.memo.mixins import BabelPreviewable
from lino.modlib.uploads.choicelists import ImageFormats, ImageSizes
from lino.utils.html import format_html, escape, mark_safe, tostring
from lino.utils.mldbc.mixins import BabelDesignated
from lino_xl.lib.topics.mixins import Taggable
from lino_xl.lib.countries.mixins import AddressLocation
from lino_xl.lib.contacts.mixins import ContactRelated
# from lino_vedi.lib.contacts.choicelists import PartnerRoles

from .ui import *
from .choicelists import *

WITH_CAROUSEL = True


class EntryType(BabelDesignated, PublishableContent):

    class Meta:
        app_label = "immo"
        verbose_name = _("Property type")
        verbose_name_plural = _("Property types")


class Entry(
        UserAuthored, PrivacyRelevant, BabelPreviewable, Commentable,
        PublishableContent, Illustrated, Taggable, AddressLocation, ContactRelated):

    class Meta:
        app_label = "immo"
        verbose_name = _("Real estate offer")
        verbose_name_plural = _("Real estate offers")

    memo_command = "entry"

    deed_type = DeedTypes.field()
    entry_type = dd.ForeignKey('immo.EntryType')
    title = dd.BabelCharField(_("Title"), max_length=200, blank=True)
    bedrooms = models.IntegerField(_("Bedrooms"), null=True, blank=True)
    bathrooms = models.IntegerField(_("Bathrooms"), null=True, blank=True)
    livable_space = models.IntegerField(_("Livable space"), null=True, blank=True)
    land = models.IntegerField(_("Land"), null=True, blank=True)
    price = dd.PriceField(_("Price"), null=True, blank=True)
    property_condition = PropertyConditions.field(null=True, blank=True)
    availability_text = AvailabilityTexts.field(null=True, blank=True)
    availability_date = dd.DateField(_("Available from"), null=True, blank=True)
    address_text = dd.RichTextField(_("Address"), blank=True, format="plain")

    def __str__(self):
        return dd.babelattr(self, "title")

    @classmethod
    def setup_parameters(cls, fields):
        super().setup_parameters(fields)
        cls.setup_range_parameter(fields, 'price', _("Price from"), _("Price until"))
        cls.setup_range_parameter(fields, 'pub_date', _(
            "Published after"), _("Published before"))

    @classmethod
    def get_simple_parameters(cls):
        lst = list(super().get_simple_parameters())
        # lst.append('group')
        # lst.append('price')
        # lst.append('pub_date')
        lst.append('bedrooms')
        lst.append('bathrooms')
        lst.append('entry_type')
        return lst

    # def as_tile(self, ar, prev, **kwargs):
    #     s = f"""<span style="font-size:2rem; float:left; padding-right:1rem;">{
    #         ar.obj2htmls(self)}</span> """
    #     s += _("{} pupils").format(Enrolment.objects.filter(group=self).count())
    #     s += "<br>"
    #     sar = rt.models.school.CoursesByGroup.create_request(
    #         parent=ar, master_instance=self)
    #     s += " ".join([
    #         sar.obj2htmls(
    #             obj, obj.subject.icon_text or str(obj.subject), title=str(obj.subject))
    #         for obj in sar])
    #     s = constants.TILE_TEMPLATE.format(chunk=s)
    #     if prev is not None and prev.grade != self.grade:
    #         s = """<p style="display:block;"></p>""" + s
    #     return mark_safe(s)

    def get_info_chunks(self):
        # if self.entry_type:
        #     info.append(ar.obj2htmls(self.entry_type))
        # if self.pub_date:
        #     info.append(str(self.pub_date.year))
        # info.append(ar.obj2htmls(self.entry_type))
        yield settings.SITE.format_currency(self.price)
        if self.livable_space:
            # info.append(format_html(_("{} bedrooms"), self.bedrooms))
            yield format_html(_("{} m²"), self.livable_space)
        if self.bedrooms:
            # info.append(format_html(_("{} bedrooms"), self.bedrooms))
            yield format_html(_("{} 🛏"), self.bedrooms)
        if self.bathrooms > 1:
            yield format_html(_("{} bathrooms"), self.bathrooms)

    def as_tile(self, ar, prev, **kwargs):
        if ar is None:
            return str(self)

        t = _("Published {}").format(self.pub_date)

        if self.title:
            s = escape(self.title)
        else:
            s = escape(self.address_location(", "))

        chunk = ar.obj2htmls(self, text=s, title=t)
        chunk += mark_safe(" | ")
        chunk += mark_safe(", ".join(self.get_info_chunks()))
        chunk += mark_safe("<br>")
        if (img := self.main_image) is not None:
            if (mf := img.get_media_file()) is not None:
                chunk += img.as_html(
                    ar, mf,
                    image_size=ImageSizes.solo,
                    image_format=ImageFormats.square,
                    href=ar.obj2url(self))

        # chunk += mark_safe("<br>")

        # prl = []
        # PartnerCast = rt.models.contacts.PartnerCast
        # for cast in PartnerCast.objects.filter(
        #         entry=self, role=PartnerRoles.author):
        #     prl.append(ar.obj2htmls(
        #         cast.partner,
        #         f"{cast.partner.first_name} {cast.partner.last_name}".strip()))
        # if len(prl) > 0:
        #     # s += format_html(" {} ", _("by"))
        #     s += format_html("<br>{} ", "👤")  # (U+1F464)
        #     s += mark_safe(", ".join(prl))

        # if self.body_short_preview:
        #     s += mark_safe("\n" + self.body_short_preview)
        return format_html(constants.TILE_TEMPLATE, chunk=chunk)

    def as_paragraph(self, ar):
        if ar is None:
            return str(self)
        s = mark_safe("")
        t = _("Published {}")
        t = t.format(self.pub_date)
        s += ar.obj2htmls(self, title=t)

        s += format_html("<p>{}</p>", mark_safe(", ".join(self.get_info_chunks())))

        # prl = []
        # PartnerCast = rt.models.contacts.PartnerCast
        # for cast in PartnerCast.objects.filter(
        #         entry=self, role=PartnerRoles.author):
        #     prl.append(ar.obj2htmls(
        #         cast.partner,
        #         f"{cast.partner.first_name} {cast.partner.last_name}".strip()))
        # if len(prl) > 0:
        #     s += format_html(" {} ", _("by"))
        #     s += mark_safe(", ".join(prl))

        if (img := self.main_image) is not None:
            if (mf := img.get_media_file()) is not None:
                s += img.as_html(
                    ar, mf, image_size=ImageSizes.small,
                    image_format=ImageFormats.right)
        if self.body_short_preview:
            s += mark_safe("\n" + self.body_short_preview)
        return s

    def as_page(self, ar, display_mode="detail", **kwargs):
        title = dd.babelattr(self, "title")
        yield PAGE_TITLE_TEMPLATE.format(escape(title))
        items = []
        # for pr in PartnerRoles.get_list_items():
        #     prl = []
        #     PartnerCast = rt.models.contacts.PartnerCast
        #     for cast in PartnerCast.objects.filter(entry=self, role=pr):
        #         prl.append(ar.obj2htmls(cast.partner))
        #     if len(prl) > 1:
        #         text = pr.text_plural
        #     elif len(prl) == 1:
        #         text = pr.text
        #     else:
        #         continue
        #     items.append(format_html("{}: {}", text, mark_safe("; ".join(prl))))

        items.extend(self.get_info_chunks())

        for k in ('entry_type', 'group', 'user'):
            value = getattr(self, k)
            if value is not None:
                fld = self.__class__._meta.get_field(k)
                items.append(format_html(
                    "{}: {}", fld.verbose_name, ar.obj2htmls(value)))

        if len(items):
            txt = " | ".join(items)
            yield """<p class="small">{}</p>""".format(txt)
            # https://getbootstrap.com/docs/3.4/css/#small-text

        if self.album_id:
            yield '<div class="bg-secondary-subtle border-secondary-subtle rounded-3">'
            for item in self.album.items.filter(upload__isnull=False):
                if (mf := item.upload.get_media_file()) is not None:
                    yield item.upload.as_html(
                        ar, mf,
                        image_format=item.get_image_format(),
                        image_size=item.get_image_size(),
                        title=self.title)
            yield '</div>'

        yield dd.babelattr(self, "body_full_preview")

        if self.album_id:
            if WITH_CAROUSEL:
                carouselid = self.__class__.__name__ + str(self.pk)
                yield f"""
                <div id="{carouselid}" class="carousel slide" data-bs-ride="carousel">
                  <div class="carousel-inner">
                """
                active = "active"
                for item in self.album.items.filter(upload__isnull=False):
                    if (mf := item.upload.get_media_file()) is not None:
                        yield f"""<div class="carousel-item {active}">"""
                        active = ""
                        yield item.upload.as_html(
                            ar, mf,
                            image_format=ImageFormats.carousel,
                            image_size=ImageSizes.big,
                            # image_size=item.get_image_size(),
                            class_names="d-block w-100",
                            # class_names="d-block",
                            title=self.title, clickable=False)
                        yield """</div>"""
                yield f"""
                  </div>
                  <button class="carousel-control-prev" type="button" data-bs-target="#{carouselid}" data-bs-slide="prev">
                    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Previous</span>
                  </button>
                  <button class="carousel-control-next" type="button" data-bs-target="#{carouselid}" data-bs-slide="next">
                    <span class="carousel-control-next-icon" aria-hidden="true"></span>
                    <span class="visually-hidden">Next</span>
                  </button>
                </div>
                """

        yield """<p class="small">{}:</p>""".format(_("Contact"))
        yield self.partner.get_address_html()
        # print("20251209", tostring(self.partner.contact_details))
        yield tostring(self.partner.contact_details)
dd.update_field(Entry, 'user', verbose_name=_("Editor"))
