from django.db import models

import auto_prefetch

from .utils import CustomJSONEncoder


# Create your models here.
class Workbook(auto_prefetch.Model):
    """
    Represents a "workbook": basically an Excel file.

    Each workbook will have one (or more) Sheets.

    Note, this is storing the raw, unprocessed data.
    """

    filename = models.CharField(max_length=255)
    md5 = models.CharField(unique=True, max_length=32)
    mtime = models.DateTimeField()
    imported_time = models.DateTimeField()

    def __str__(self):
        return "%s" % self.filename


class Sheet(auto_prefetch.Model):
    """
    Represents a "sheet": basically a tab in an Excel file.

    Each sheet must belong to a workbook, and will have one (or more) Rows.
    """

    workbook = auto_prefetch.ForeignKey(Workbook, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField("sheet index")
    name = models.CharField("sheet name", max_length=63)
    row_count = models.PositiveIntegerField("rows")
    col_count = models.PositiveSmallIntegerField("columns")

    def __str__(self):
        return '"%s" of "%s"' % (
            self.name,
            self.workbook.filename if hasattr(self, "workbook") else "",
        )


class Row(auto_prefetch.Model):
    """
    Represents a "row" on a sheet.

    Each row belongs to a sheet. The data is stored internally as a JSONField,
    with the column name as the key, and the cell value as the value.

    The JSONField used here is specific to PostgreSQL.
    """

    sheet = auto_prefetch.ForeignKey(Sheet, on_delete=models.CASCADE)
    # use the column as the key, as we don't know in advance how many columns
    # we have
    index = models.PositiveIntegerField("Row Index")
    data = models.JSONField(encoder=CustomJSONEncoder)

    def __str__(self):
        return f'Row {self.index:,} of "{self.sheet.name}"'
