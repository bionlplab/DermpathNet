import os
import urllib.request
from collections import Counter
from pathlib import Path

import pandas as pd
import tabulate


def get_bioc(pmid, dest):
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/' \
          f'BioC_xml/{pmid}/unicode'
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w', encoding='utf8') as fp:
        fp.write(text)


def is_file_empty(pathanme):
    return os.path.exists(pathanme) and os.stat(pathanme).st_size == 0


def is_csv_empty(pathanme) -> bool:
    if os.path.exists(pathanme) and os.stat(pathanme).st_size == 0:
        return True
    try:
        pd.read_csv(pathanme)
    except pd.errors.EmptyDataError:
        return True
    return False


def is_folder_empty(dirname):
    dirs = os.listdir(dirname)
    return len(dirs) == 0


def create_empty_file(pathname):
    pathname.parent.mkdir(parents=True, exist_ok=True)
    with open(pathname, 'w') as _:
        pass


def generate_path(pmc: str) -> Path:
    return Path(pmc[:-4] + '/' + pmc[-4:-2])


def generate_filename(root: Path, pmc: str, name: str) -> Path:
    return root / generate_path(pmc) / '{}'.format(name)


def pprint_counter(counter: Counter, sort_key: bool = False, percentage=False):
    if not sort_key:
        itr = counter.most_common()
    else:
        itr = sorted(counter.items(), key=lambda s: s[0])

    total = sum(counter.values())
    data = []
    for k, v in itr:
        if percentage:
            p = '%.1f' % (v / total * 100)
            data.append({'key': k, 'value': v, '%': p})
        else:
            data.append({'key': k, 'value': v})

    df = pd.DataFrame(data)
    s = tabulate.tabulate(df,
                          showindex=False,
                          headers=df.columns,
                          tablefmt="plain")
    print(s)
