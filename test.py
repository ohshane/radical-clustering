from wok.parse import DictionaryParser, IDSParser
from pathlib import Path
import os

__file__ = Path(os.path.abspath('__file__'))
data_path = __file__.parent/'wok'/'data'

IDSParser(data_path=data_path)
