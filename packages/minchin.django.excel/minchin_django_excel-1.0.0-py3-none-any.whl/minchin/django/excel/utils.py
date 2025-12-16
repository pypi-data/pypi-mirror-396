from datetime import datetime
import string

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

import ciso8601
import colorama
import dateparser
import numpy as np
from prettyjson import PrettyJSONWidget
from pytz import timezone

from minchin.text import centered


def from_timestamp(timestamp):
    """
    Converts the timestamp to datetime.datetime objects.

    The timestamps appear to by Unix timestamps, with 3 extra zeros.

    Returned timestamp is in UTC, and timezone aware.
    """
    if isinstance(timestamp, int):
        dt = datetime.fromtimestamp(timestamp / 1000)
    elif isinstance(timestamp, str):
        try:
            dt = ciso8601.parse_datetime(timestamp)
        except ValueError:
            try:
                dt = dateparser.parse(timestamp)
            except ValueError as e:
                print(f"** Was given: {timestamp} **")
                raise e
    else:
        raise ValueError(f"Expected int or str, got {type(timestamp)}: {timestamp}")

    tz = timezone("UTC")
    dt_tz_aware = tz.localize(dt)

    return dt_tz_aware


class CustomJSONEncoder(DjangoJSONEncoder):
    """
    Custom JSON Encoder.

    Deals with Numpy integers and floating point numbers.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return super().default(obj)


def column_to_number(col):
    """
    Return number corresponding to Excel-style column.

    >>> column_to_number('A')
    1
    >>> column_to_number('AB')
    28

    """
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord("A")) + 1
    return num


def title(input_str):
    return (
        colorama.Style.BRIGHT
        + colorama.Fore.YELLOW
        + colorama.Back.BLUE
        + centered(input_str)
        + colorama.Style.RESET_ALL
    )


def subtitle(input_str):
    return colorama.Style.BRIGHT + centered(input_str) + colorama.Style.RESET_ALL


def admin_change_url(obj):
    # https://medium.com/@hakibenita/things-you-must-know-about-django-admin-as-your-app-gets-bigger-6be0b0ee9614
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse("admin:{}_{}_change".format(app_label, model_name), args=(obj.pk,))


def admin_link(attr, short_description, empty_description="-"):
    """
    Decorator used for rendering a link to a related model in the admin detail
    page.

    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.

    The wrapped method receives the related object and should return the link
    text.

    Usage::

        @admin.register(models.Customer)
        class CustomerAdmin(admin.ModelAdmin):
            list_display = (
                'id',
                'name',
                'credit_card_link',
            )

        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name


    """

    # https://medium.com/@hakibenita/things-you-must-know-about-django-admin-as-your-app-gets-bigger-6be0b0ee9614
    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html('<a href="{}">{}</a>', url, func(self, related_obj))

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__["get_query_string"]

    def __init__(self, request, page_num, paginator):
        self.show_all = "all" in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class PaginationInline(admin.TabularInline):
    """
    A paginated TubularInline.

    Specify an ordering (either in the model or the Admin class), otherwise
    Django will complain about the possible lack of consistent ordering.
    """

    template = "admin/edit_inline/tabular_paginated.html"
    per_page = 20

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super(PaginationInline, self).get_formset(
            request, obj, **kwargs
        )

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get("p", "0"))
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)

                self.cl = InlineChangeList(request, page_num, paginator)
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet


# see https://github.com/kevinmickey/django-prettyjson/pull/34
class PrettyJSONWidgetFixed(PrettyJSONWidget):
    def render(self, name, value, attrs=None, **kwargs):
        return mark_safe(super().render(name, value, attrs=None, **kwargs))
