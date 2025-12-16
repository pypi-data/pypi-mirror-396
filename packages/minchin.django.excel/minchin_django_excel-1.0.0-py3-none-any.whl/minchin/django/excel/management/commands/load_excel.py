from datetime import datetime
import glob
import hashlib
import itertools
import os
from pathlib import Path
from string import ascii_uppercase

from django.core.management.base import BaseCommand
from django.utils import timezone

import pandas as pd

from minchin.text import Answers, query_yes_no, query_yes_no_all_none

from ...models import Row, Sheet, Workbook
from ...utils import subtitle, title

BLOCKSIZE = 65536
INDENT = " " * 4


def iter_excel_columns():
    """
    Generate a sequence that matches Excel column headings.

    A, B, C, ... X, Y, Z, AA, AB, AC, ... AZ, BA, ...

    https://stackoverflow.com/a/29351603
    """
    for size in itertools.count(1):
        for s in itertools.product(ascii_uppercase, repeat=size):
            yield "".join(s)


class Command(BaseCommand):
    help = "Load a raw excel file into the database."

    def add_arguments(self, parser):
        parser.add_argument("excel_file", nargs="+")
        parser.add_argument(
            "-s",
            "--skip-existing",
            action="store_true",
            help="Don't reload files into the database if md5's match",
        )
        parser.add_argument(
            "-r",
            "--replace-existing",
            action="store_true",
            help="Replace existing files already in database",
        )

    def handle(self, *args, **options):
        self.stdout.write(title(os.path.basename(__file__)))
        self.stdout.write(subtitle(self.help))

        all_files = []
        for my_file_str in options["excel_file"]:
            # use glob.glob(), as Pathlib can't do absolute globbing
            all_files.extend(glob.glob(my_file_str))

        for my_file_str in all_files:
            my_file = Path(my_file_str).resolve()
            self.stdout.write("Loading '%s' ..." % my_file)

            # determine file hash
            hasher = hashlib.md5()  # change hasher here
            with open(my_file, "rb") as open_file:
                buf = open_file.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = open_file.read(BLOCKSIZE)
            my_md5 = hasher.hexdigest()

            my_mtime = datetime.fromtimestamp(os.path.getmtime(my_file))
            my_mtime = timezone.make_aware(my_mtime)

            # Check if we've already imported this file
            hash_matches = Workbook.objects.filter(md5=my_md5)
            if len(hash_matches) > 0:
                self.stdout.write(
                    f'Found workbook with hash "{my_md5}" already in database.'
                )
                if options["replace_existing"] is True:
                    replace = Answers.YES
                elif options["skip_existing"] is True:
                    replace = Answers.NO
                else:
                    replace = query_yes_no_all_none("Replace workbook?", default="no")

                    if replace == Answers.ALL:
                        options["replace_existing"] = True
                        replace = Answers.YES
                    elif replace == Answers.NONE:
                        options["skip_existing"] = True
                        replace = Answers.NO

                if replace == Answers.NO:
                    print()
                    continue
                elif replace == Answers.YES:
                    delete_count = hash_matches.delete()
                    # print(delete_count)
                    self.stdout.write("%s row(s) deleted." % delete_count[0])

            filename_matches = Workbook.objects.filter(filename=my_file.name)
            if len(filename_matches) > 0:
                self.stdout.write(
                    f'Found workbook with filename "{my_file.name}" already in database.'
                )
                replace = query_yes_no("Replace workbook?", default="no")
                if replace == Answers.NO:
                    self.stdout.write("Continuing on...")
                elif replace == Answers.YES:
                    delete_count = filename_matches.delete()
                    self.stdout.write(f"{delete_count[0]} workbook(s) deleted.")

            # self.stdout.write("No matching Workbooks currently in database.")

            # push Workbook to database
            self.stdout.write(f'Adding Workbook "{my_file.name}" to database.')
            my_workbook = Workbook(
                filename=my_file.name,
                md5=my_md5,
                mtime=my_mtime,
                imported_time=timezone.now(),
            )
            my_workbook.save()

            df = pd.read_excel(my_file, sheet_name=None, header=None, index_col=None)

            if len(df.keys()) == 1:
                self.stdout.write(f"{INDENT}There is 1 sheet.")
            else:
                self.stdout.write(f"{INDENT}There are {len(df.keys())} sheets.")
            for sheet_number, sheet_name in enumerate(df.keys()):
                self.stdout.write(f'{INDENT}Adding Sheet "{sheet_name}" to database.')
                (row_count, col_count) = df[sheet_name].shape
                my_sheet = Sheet(
                    workbook=my_workbook,
                    index=sheet_number,
                    name=sheet_name,
                    row_count=row_count,
                    col_count=col_count,
                )
                my_sheet.save()

                my_excel_columns = iter_excel_columns()
                df[sheet_name].columns = [
                    next(my_excel_columns) for _ in df[sheet_name].columns
                ]

                for row_number in range(row_count):
                    # use 'to_dict()' rather than 'to_json()' so it actually
                    # ends up as JSON (rather than a string) in the database
                    row_dict = df[sheet_name].iloc[row_number].to_dict()
                    # clean NaN from our row
                    row_dict = {
                        k: None if pd.isnull(v) else v for k, v in row_dict.items()
                    }
                    Row(sheet=my_sheet, data=row_dict, index=row_number).save()

            self.stdout.write("")
