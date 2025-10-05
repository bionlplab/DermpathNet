"""
Usage:
    script.py [options] -q STR -o DEST

Options:
    -q <str>        Query
    -o <file>       PMC file
"""

import datetime
import os
from pathlib import Path
from typing import Iterator, List

import docopt
import pandas as pd
from Bio import Entrez


def search(query: str,
           email: str = 'your.email@example.com',
           default_retmax: int = 100) -> Iterator[List[str]]:
    Entrez.email = email
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmode='xml',
                            retmax=default_retmax,
                            term=query,
                            usehistory='y')
    record = Entrez.read(handle)
    total = int(record['Count'])
    retmax = int(record['RetMax'])
    retstart = int(record['RetStart'])
    webenv = record['RetStart']
    print('Found %s records' % total)
    print('Search %s-%s records' % (retstart, retstart + retmax))
    yield record['IdList']
    while retstart + retmax < min(total, 9998):
        retstart = retstart + retmax
        print('Search %s-%s records' % (retstart, retstart + retmax))
        handle = Entrez.esearch(db='pubmed',
                                sort='relevance',
                                retmode='xml',
                                retmax=default_retmax,
                                term=query,
                                usehistory='y',
                                retstart=retstart,
                                WebEnv=webenv)
        record = Entrez.read(handle)
        retmax = int(record['RetMax'])
        retstart = int(record['RetStart'])
        yield record['IdList']


def fetch_details(id_list: List[str], email: str = 'your.email@example.com'):
    ids = ','.join(id_list)
    Entrez.email = email
    handle = Entrez.esummary(db='pubmed', retmode='xml', id=ids)
    results = Entrez.read(handle)
    return results


def parse_results(results: List[dict]):
    data = []
    insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    for paper in results:
        has_pmc = 'pmc' in paper['ArticleIds']
        if has_pmc:
            x = {
                'pmid': paper['Id'],
                'pmcid': paper['ArticleIds']['pmc'],
                # 'doi': paper['DOI'],
                'title': paper['Title'],
                'journal': paper['Source'],
                'insert_time': insert_time
            }
            data.append(x)
    return data


def query_pubmed(query: str) -> List:
    total_data = []
    print('Query:', query)
    for pubmids in search(query, default_retmax=1000):
        try:
            papers = fetch_details(pubmids)
        except RuntimeError as e:
            print(e)
            continue
        data = parse_results(papers)
        total_data += data
    print('Get %d records' % len(total_data))
    return total_data


def query_pubmed_file(query: str, dest: os.PathLike):
    total_data = query_pubmed(query)
    if len(total_data) > 0:
        df = pd.DataFrame(total_data)
        df = df.sort_values(by='pmid')
        df.to_csv(dest, index=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    query_pubmed_file(args['-q'], Path(args['-o']))
