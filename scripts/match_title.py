"""
Usage:
    script.py [options] -i SOURCE -o DEST -q STR -u ONT

Options:
    -i <file>   CSV file with pmcid
    -o <file>   Figure CSV file
    -q <str>    Query
    -u <file>   Ontology file in the yaml format
"""
from pathlib import Path

import docopt
import pandas as pd
import tqdm

from scripts.ontology import create_synonyms_pattern, DiseaseOntology


def match_title(src, dest, query, ontology: DiseaseOntology):
    df = pd.read_csv(src)
    statuses = []
    p = create_synonyms_pattern(ontology.synonyms(query))

    def __match1(s):
        return p.search(s)

    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        title = row['title']
        if pd.isna(title):
            status = 'Empty'
        else:
            if __match1(title):
                status = 'Match'
            else:
                status = 'NotMatch'
        statuses.append(status)

    df['disease'] = statuses
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)


def match_title_file(src, dest, query, ontology_pathname):
    ontology = DiseaseOntology.read_file(ontology_pathname)
    match_title(src, dest, query, ontology)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    match_title_file(
        src=Path(args['-i']),
        dest=Path(args['-o']),
        query=args['-q'],
        ontology_pathname=args['-u']
    )
