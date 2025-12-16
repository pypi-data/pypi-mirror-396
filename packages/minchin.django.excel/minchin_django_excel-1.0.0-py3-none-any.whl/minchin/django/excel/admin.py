from django.contrib import admin
from django.db import models

from related_admin import RelatedFieldAdmin

from minchin.django.excel.models import Row, Sheet, Workbook

from .utils import PaginationInline, PrettyJSONWidgetFixed, admin_link


class SheetInline(admin.TabularInline):
    model = Sheet
    extra = 0
    show_change_link = True
    can_delete = False
    ordering = ("index",)
    readonly_fields = [
        "index",
        "name",
        "row_count",
        "col_count",
    ]


class RowInline(PaginationInline):
    model = Row
    formfield_overrides = {
        models.JSONField: {"widget": PrettyJSONWidgetFixed(attrs={"initial": "parsed"})}
    }
    # max_num = 100
    show_change_link = True
    can_delete = False
    ordering = ("index",)
    extra = 0


class WorkbookAdmin(RelatedFieldAdmin):
    # see https://stackoverflow.com/a/23747842 for alternate
    model = Workbook
    list_display = [
        "filename",
    ]
    fields = [
        # field.name for field in Workbook._meta.fields if field.name not in ["id", ]
        "filename",
        "md5",
        "mtime",
        "imported_time",
    ]
    readonly_fields = [
        "imported_time",
    ]
    search_fields = ["filename"]
    inlines = [SheetInline]


class SheetAdmin(admin.ModelAdmin):
    model = Sheet
    list_display = [
        "name",
        "index",
        "workbook_link",
    ]
    list_filter = [
        "workbook",
    ]
    ordering = [
        "workbook__filename",
        "index",
    ]
    search_fields = [
        "workbook__filename",
        "name",
    ]
    inlines = [
        RowInline,
    ]
    raw_id_fields = ("workbook",)
    readonly_fields = [
        "row_count",
        "col_count",
    ]

    fieldsets = [
        (
            None,
            {
                "fields": ("workbook", "index", "name", "row_count", "col_count"),
            },
        ),
        (
            "Meta",
            {
                "fields": readonly_fields[2:],
            },
        ),
    ]

    @admin_link("workbook", "Workbook")
    def workbook_link(self, workbook):
        return workbook


class RowAdmin(RelatedFieldAdmin):
    model = Row
    list_display = [
        "pk",
        "index",
        "sheet__name",
        "sheet__workbook",
        # "workbook_link"
    ]
    ordering = [
        "sheet__workbook",
        "sheet__name",
        "index",
        "pk",
    ]
    list_filter = [
        "sheet__workbook",
        "sheet__name",
    ]
    search_fields = [
        "sheet__workbook__filename",
        "sheet__name",
        "index",
    ]
    formfield_overrides = {
        models.JSONField: {"widget": PrettyJSONWidgetFixed(attrs={"initial": "parsed"})}
    }
    raw_id_fields = ("sheet",)

    @admin_link("sheet", "Workbook")
    def workbook_link(self, sheet):
        return sheet.workbook


# admin.site.register(Workbook, WorkbookAdmin)
# admin.site.register(Sheet, SheetAdmin)
# admin.site.register(Row, RowAdmin)
