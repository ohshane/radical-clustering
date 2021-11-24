from collections import Counter
from pathlib import Path
from functools import reduce
import numpy as np
import math
import pprint
import json
import re

class _Parser:
    def __init__(self, data_path: Path, name=""):
        if data_path.exists() and data_path.is_dir():
            self.data_path = data_path
        else:
            raise ValueError
        self.name = name

class DictionaryParser(_Parser):
    def __init__(self, data_path=Path(__file__)/'data', name='zh-en_dictionary'):
        _Parser.__init__(self, data_path, name)
        if Path(self.data_path/'dictionary.txt').exists() and Path(self.data_path/'dictionary.txt').is_file():
            self.file_path = self.data_path/'dictionary.txt'
        else:
            raise ValueError
        self._info = {}

        keys = []
        with open(self.file_path) as f:
            for row in f:
                keys.extend(json.loads(row).keys())
        key_count_dict = Counter(keys)
        self._info['keys'] = dict(key_count_dict)

        del keys
        char_infos = []
        with open(self.file_path) as f:
            for row in f:
                char_info = json.loads(row)
                for k in key_count_dict.keys():
                    try: char_info[k]
                    except: char_info[k] = None
                char_infos.append(char_info)

        self.dictionary = char_infos
        self._info['size'] = len(self.dictionary)

    @property
    def ideographic_dictionary(self):
        return (d for d in self.dictionary if d['etymology'] is not None and d['etymology']['type'] == 'ideographic')
        
    @property
    def pictographic_dictionary(self):
        return (d for d in self.dictionary if d['etymology'] is not None and d['etymology']['type'] == 'pictographic')

    @property
    def pictophonetic_dictionary(self):
        return (d for d in self.dictionary if d['etymology'] is not None and d['etymology']['type'] == 'pictophonetic')

    def info(self):
        self._info['etymology'] = {
            'ideographic':   len([_ for _ in self.ideographic_dictionary]),
            'pictographic':  len([_ for _ in self.pictographic_dictionary]),
            'pictophonetic': len([_ for _ in self.pictophonetic_dictionary]),
        }
        return self._info

    def __repr__(self):
        return pprint.pformat(self.info())

class IDSParser(_Parser):
    def __init__(self, data_path=Path(__file__)/'data'):
        _Parser.__init__(self, data_path)
        if Path(self.data_path/'ids.tsv').exists() and Path(self.data_path/'ids.tsv').is_file():
            self.file_path = self.data_path/'ids.tsv'
        else:
            raise ValueError

        self._pickle_path = self.data_path/'pickle'

        is_saved = False
        if Path(self._pickle_path).exists() and Path(self._pickle_path).is_dir():
            if Path(self._pickle_path/'atoms.pickle').exists() \
                    and Path(self._pickle_path/'pickle'/'nonatoms.pickle').exists() \
                    and Path(self._pickle_path/'pickle'/'nonatoms_decomposed.pickle').exists():
                is_saved = True

        if is_saved:
            self.atoms_ids = self._pickle_path/'atoms.pickle'
            self.nonatoms_ids = self._pickle_path/'nonatoms.pickle'
            self.nonatoms_decomposed_ids = self._pickle_path/'nonatoms_decomposed.pickle'

        else:
            tokens = np.array([
                ['U+2FF0', '⿰', '⿰'],
                ['U+2FF1', '⿱', '⿱'],
                ['U+2FF2', '⿲', '⿲'],
                ['U+2FF3', '⿳', '⿳'],
                ['U+2FF4', '⿴', '⿴'],
                ['U+2FF5', '⿵', '⿵'],
                ['U+2FF6', '⿶', '⿶'],
                ['U+2FF7', '⿷', '⿷'],
                ['U+2FF8', '⿸', '⿸'],
                ['U+2FF9', '⿹', '⿹'],
                ['U+2FFA', '⿺', '⿺'],
                ['U+2FFB', '⿻', '⿻'],
            ], dtype='object')

            with open(self.file_path, 'r') as f:
                f = f.readlines()[2:]
                f = [row[:-1].split('\t') for row in f]

            ids_dict = {}
            for row in f:
                _, u, *idses = row
                group = "GTJKV"
                group_pointer = "GTJKV"
                group_idses = []
                grouped_idses = {}
                for ids in idses:
                    ids, *custom_group = [x for x in re.split(r'(?:[\[\]])', ids) if x]
                    if custom_group:
                        group = custom_group[0]
                    if group_pointer != group:
                        if group_idses:
                            grouped_idses[group] = group_idses
                            group_idses = []
                        group_pointer = group
                    else:
                        group_idses.append(ids)

                ids_dict[hex(ord(u))] = grouped_idses
                grouped_idses = {}

            # print(ids_dict)

    def group2score(group, log_scale=False):
        group_spec = "GTJKVAXO"
        score = int(reduce(lambda a, b: str(int(a))+str(int(b)), list(map(lambda x: x in group, group_spec))), base=2)
        if log_scale:
            score = math.log2(score + 1)
        return score