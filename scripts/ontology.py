import re

import yaml


class DiseaseOntology:
    def __init__(self):
        self.objs = {}

    @classmethod
    def read_file(cls, filename) -> 'DiseaseOntology':
        with open(filename, 'r') as fp:
            objs = yaml.safe_load(fp)
        o = DiseaseOntology()
        o.objs = objs
        return o

    def diseases(self) -> list[str]:
        return sorted(self.objs.keys())

    def synonyms(self, disease) -> set[str]:
        synonyms = set()
        v = self.objs[disease]
        if 'Synonyms' in self.objs[disease]:
            synonyms.update(v['Synonyms'])
        synonyms.add(disease)
        return synonyms


def create_synonyms_pattern(synonyms: list[str] | set[str]):
    s = '|'.join(synonyms)
    return re.compile(s, re.I)
