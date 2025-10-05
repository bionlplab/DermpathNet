"""
Usage:
    script.py [options] -i SOURCE -o DEST -q STR -u ONT

Options:
    -i <file>   CSV file with pmcid
    -o <file>   Figure CSV file
    -q <str>    Query
    -u <file>   Ontology file in the yaml format
"""
import re
from pathlib import Path

import docopt
import pandas as pd
import tqdm

from scripts.ontology import DiseaseOntology, create_synonyms_pattern


def match_caption(src, dest, query, ontology: DiseaseOntology):
    df = pd.read_csv(src)
    statuses1 = []
    statuses2 = []

    p = create_synonyms_pattern(ontology.synonyms(query))
    p2 = re.compile(r'H & E|H&E|x4|×10|x20|x50|x100|x200|x400|x 4|× 10|x 20'
                    r'|x 50|x 100|x 200|x 400|4x|10x|20x|50x|100x|200x|400x'
                    r'|4 x|10 x|20 x|50 x|100 x|200 x|400 x', re.I)

    def __match1(s):
        return p.search(s)

    def __match2(s):
        return p2.search(s)

    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        caption = row['caption']
        if pd.isna(caption):
            status1 = 'Empty'
            status2 = 'Empty'
        else:
            if __match1(caption):
                status1 = 'Match'
            else:
                status1 = 'NotMatch'

            if __match2(caption):
                status2 = 'Match'
            else:
                status2 = 'NotMatch'

        statuses1.append(status1)
        statuses2.append(status2)

    df['disease'] = statuses1
    df['modality'] = statuses2
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)


def match_caption_file(src, dest, query, ontology_pathname):
    ontology = DiseaseOntology.read_file(ontology_pathname)
    match_caption(src, dest, query, ontology)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    match_caption_file(
        src=Path(args['-i']),
        dest=Path(args['-o']),
        query=args['-q'],
        ontology_pathname=args['-u']
    )
