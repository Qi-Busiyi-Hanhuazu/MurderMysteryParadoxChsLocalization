import json
import os
import re
from logging import warning

from helper import get_sheet, DIR_CSV, DIR_FILES, DIR_OUTPUT, LANGUAGE, replace_speakers

JSON_PATTERN = re.compile(r"\{return([`'\"])(.+)\1\}")


def batch_convert_others_data(csv_root: str, original_root: str, output_root: str, language: str) -> None:
  language_root = f"{csv_root}/{language}/data"
  for root, dirs, files in os.walk(language_root):
    for file in files:
      if not file.endswith(".csv"):
        continue

      sheet_name = "data/" + os.path.join(root, file).replace(language_root, "").replace(
          "\\", "/").removeprefix("/").removesuffix(".csv")
      translation = get_sheet(os.path.join(root, file))
      if not translation:
        warning(f"Cannot load csv: {sheet_name}")
        continue

      original_path = f"{original_root}/others/{sheet_name}.js"
      if not os.path.exists(original_path):
        warning(f"Original file not found: {original_path}")
        continue
      with open(original_path, "r", -1, "utf8") as reader:
        js_content = reader.read()

      match = JSON_PATTERN.search(js_content)
      if not match:
        warning(f"Pattern not found in {original_path}")
        continue
      json_content = json.loads(match.group(2).replace("\\\\", "\\"))

      for k, v in translation.items():
        key_match = re.match(r"\[(\d+)\]/(.+)", k)
        if not key_match:
          continue
        index = int(key_match.group(1))
        key = key_match.group(2)
        if key in ["ruby", "hiragana"]:
          json_content[index][key] = ""
        else:
          json_content[index][key] = v

      new_content = js_content[:match.start(2)] + json.dumps(
          json_content, ensure_ascii=False, separators=(",", ":")).replace("\\", "\\\\") + js_content[match.end(2):]
      new_content = replace_speakers(translation, new_content)

      output_path = f"{output_root}/others/{sheet_name}.js"
      if new_content == js_content:
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
  batch_convert_others_data(DIR_CSV, DIR_FILES, DIR_OUTPUT, LANGUAGE)
