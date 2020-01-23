import os
import csv
import json

from skeletor.utility.logger import Logger
from skeletor.config import BASE_DIR


class TextOperations:
    logger = Logger().get(__name__)

    def _float(self, val):
        try:
            return float(val)
        except ValueError:
            return -100.0

    def _int(self, val):
        try:
            return int(val)
        except ValueError:
            return -100

    def normalize_string(self, value):
        return value if not isinstance(
            value, str) else ' '.join(
            value.split()) if value else ''

    def read_csv(self, file_loc=None, s3fp=None, field_names=[]):
        data = []
        if file_loc:
            # file_path = os.path.join(BASE_DIR, file_loc.lstrip("/"))
            file_path = file_loc
            self.logger.info(f"READING FROM CSV FILE {file_path}")
            with open(file_path, 'r') as fp:
                reader = csv.DictReader(
                    fp) if not field_names else csv.DictReader(fp, field_names)
                data = [dict(row) for row in reader]
                fp.close()
        elif s3fp:
            reader = csv.DictReader(
                s3fp) if not field_names else csv.DictReader(s3fp, field_names)
            data = [dict(row) for row in reader]
        if field_names:
            data.pop(0)
        return data

    def write_csv(self, file_loc, rows, field_names=[]):
        file_path = os.path.join(BASE_DIR, file_loc.lstrip("/"))
        self.logger.info(f"WRITING TO CSV FILE {file_path}")
        if not field_names:
            field_names = list(rows[0].keys())
        with open(file_path, 'w') as fp:
            writer = csv.DictWriter(fp, fieldnames=list(field_names))
            writer.writeheader()
            writer.writerows(rows)
            fp.close()

    def write_json(self, file_loc, data):
        file_path = os.path.join(BASE_DIR, file_loc.lstrip("/"))
        self.logger.info(f"WRITING TO JSON FILE {file_path}")
        with open(file_path, 'w') as fp:
            fp.write(json.dumps(data, indent=2))
            fp.close()

    def read_json(self, file_loc=None, s3fp=None):
        data = None
        if file_loc:
            file_path = os.path.join(BASE_DIR, file_loc.lstrip("/"))
            self.logger.info(f"READING FROM JSON FILE {file_path}")
            with open(file_path, 'r') as fp:
                data = json.load(fp)
                fp.close()
        elif s3fp:
            data = json.load(s3fp)
        return data

    def proccess_ucode(self, ucode: str) -> str:
        ucode = str(ucode).upper()
        return "0" * (6 - len(ucode)) + ucode if len(ucode) < 6 else ucode
