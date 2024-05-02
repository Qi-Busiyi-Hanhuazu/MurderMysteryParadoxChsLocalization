import csv
import os
import re

DIR_CSV = os.environ.get("MMP_DIR_CSV", "./texts")
DIR_FILES = os.environ.get("MMP_DIR_FILES", "./original_files")
DIR_OUTPUT = os.environ.get("MMP_DIR_OUTPUT", "./out/data")
DIR_METADATA = os.environ.get("MMP_DIR_METADATA", "./metadata")
LANGUAGE = os.environ.get("MMP_LANGUAGE", "zh_Hans")


def get_sheet(csv_path: str) -> dict[str, str] | None:
  if not os.path.exists(csv_path):
    return None

  sheet_data: dict[str, str] = {}

  csvfile = open(csv_path, "r", -1, "utf-8", None, "")
  row_iter = csv.reader(csvfile)
  headers = next(row_iter)

  for row in row_iter:
    item_dict = dict(zip(headers, row))
    key = item_dict["id"]
    content = item_dict["target"].replace("\n", "[r]")
    sheet_data[key] = content

  return sheet_data


def replace_speakers(translation: dict[str, str], text: str) -> str:
  for key in translation.keys():
    if not key.startswith("speaker_"):
      continue
    speaker = key.split("_")[-1]
    text = re.sub(rf"(^#){speaker}$", rf"\1{translation[key]}", text, 0, re.MULTILINE)
    text = re.sub(
        rf"(\[(?:chara_display|chara_mod|chara_change|change_scene)(?: (?:time|bg)=['\"].+?['\"])? (?:name|chara)=['\"]){speaker}(?=['\"])",
        rf"\1{translation[key]}", text, 0, re.MULTILINE)

  return text
