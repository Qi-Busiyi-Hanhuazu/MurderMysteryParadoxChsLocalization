import hashlib
import json
from logging import warning
import os
import re

from helper import get_sheet, DIR_CSV, DIR_FILES, DIR_OUTPUT, DIR_METADATA, LANGUAGE, replace_speakers


def batch_convert_scenario(csv_root: str, original_root: str, metadata_root: str, output_root: str,
                           language: str) -> None:
  for root, dirs, files in os.walk(DIR_FILES):
    for file in files:
      original_path = f"{root}/{file}"
      sheet_name, extension = os.path.relpath(original_path, DIR_FILES).replace("\\", "/").rsplit(".")
      csv_path = f"{csv_root}/{language}/texts/{sheet_name}.csv"
      if not os.path.exists(csv_path):
        continue

      translation = get_sheet(csv_path)
      if not translation:
        warning(f"Cannot load csv: {sheet_name}")
        continue

      with open(original_path, "r", -1, "utf8") as reader:
        ks_content = reader.read()
      new_content = ks_content

      metadata_path = f"{metadata_root}/{sheet_name}.json"
      if not os.path.exists(metadata_path):
        warning(f"Metadata not found: {metadata_path}")
        continue
      with open(metadata_path, "r", -1, "utf8") as reader:
        metadata: list[dict[str, int | str]] = json.load(reader)

      metadata.sort(key=lambda x: x["start"])
      offset = 0
      for item in metadata:
        start: int = item["start"]
        end: int = item["end"]
        key: str = item["key"]

        original_text = new_content[offset + start:offset + end]
        calculated_hash = hashlib.md5(original_text.encode("utf-8")).hexdigest()
        key_hash = key.split("#")[-1]
        if key_hash != calculated_hash:
          warning(f"Hash mismatch: {key} != {calculated_hash}")

        translation_text = translation.get(key, "")
        new_content = new_content[:offset + start] + translation_text + new_content[offset + end:]
        offset += len(translation_text) - len(original_text)

      new_content = replace_speakers(translation, new_content)

      output_path = f"{output_root}/{sheet_name}.{extension}"
      if new_content == ks_content:
        print(f"Nothing changed in {original_path}")
        if os.path.exists(output_path):
          os.remove(output_path)
        continue

      if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
      with open(output_path, "w", -1, "utf-8", None, "\n") as writer:
        writer.write(new_content)
      print(f"Saved: {output_path}")


if __name__ == "__main__":
  batch_convert_scenario(DIR_CSV, DIR_FILES, DIR_METADATA, DIR_OUTPUT, LANGUAGE)
