from wok.parse import DictionaryParser, IDSParser
from pathlib import Path
from collections import Counter
import os

__file__ = Path(os.path.abspath('__file__'))
data_path = __file__.parent/'wok'/'data'
print(data_path)

idsp = IDSParser(data_path=data_path)


chars = {}
ids_chars = {}

temp_ids_chars = ""
for i, (k, v) in enumerate(idsp.ids_score_dict.items(), start=1):
    chars[k] = i
    temp_ids_chars += v['ids'][0]
temp_ids_chars = list(temp_ids_chars)
print(dict(sorted(dict(Counter(temp_ids_chars)).items(), key=lambda x: x[1], reverse=True)))
