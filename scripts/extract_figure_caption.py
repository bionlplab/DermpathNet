"""
Usage:
    script.py [options] -i SOURCE -o DEST -f FIGURE_DIR

Options:
    -i <file>   CSV file with pmcid
    -o <file>   Figure CSV file
    -f <dir>    Figure folder
"""
import collections
import concurrent
import tarfile
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from bs4 import BeautifulSoup

from scripts.commons import generate_filename, pprint_counter


def parse_nxml(reader: typing.IO, pmcid: str):
    soup = BeautifulSoup(reader, features='xml')
    data = []
    for fig in soup.find_all('fig'):
        d = {
            'pmcid': pmcid,
            'label': None,
            'caption': None,
            'graphic': None,
        }
        label = fig.find('label')
        if label is None:
            print('%s: Cannot parse figure label: %r'
                  % (pmcid, fig.get('id')))
        else:
            d['label'] = label.get_text()

        caption = fig.find('caption')
        if caption is None:
            print('%s: Cannot parse figure caption: %r'
                  % (pmcid, fig.get('id')))
        else:
            d['caption'] = caption.get_text()

        graphic = fig.find('graphic')
        if graphic is None:
            print('%s: Cannot parse figure graphic: %r'
                  % (pmcid, fig.get('id')))
        else:
            d['graphic'] = graphic.get('xlink:href')

        data.append(d)
    return data


def extract_figure_caption(local_tgz_file, pmcid):
    data = []
    new_figures = 0
    err_figures = 0
    try:
        with tarfile.open(local_tgz_file, 'r') as t:
            for member in t.getmembers():
                if member.name.endswith('.nxml'):
                    f = t.extractfile(member)
                    rows = parse_nxml(f, pmcid)
                    data.extend(rows)
    except Exception as e:
        print('%s: %s' % (pmcid, e))
    return data, new_figures, err_figures


def get_figure_caption(src, dest, image_dir):
    df = pd.read_csv(src)

    cnt = collections.Counter()
    cnt['Total PMC'] = len(df)
    cnt['Total figures'] = 0
    cnt['Empty tar.gz'] = 0
    cnt['New figures'] = 0
    cnt['Ill-formatted figures'] = 0

    data = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
            pmcid = row['pmcid']
            local_tgz_file = generate_filename(image_dir, pmcid,
                                               f'{pmcid}.tar.gz')
            if not local_tgz_file.exists():
                cnt['Empty tar.gz'] += 1
                continue
            future = executor.submit(
                extract_figure_caption,
                local_tgz_file=local_tgz_file,
                pmcid=pmcid)
            futures[future] = pmcid

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures),
                                total=len(futures)):
            pmcid = futures[future]
            try:
                d, new_figures, err_figures = future.result()
                data.extend(d)
                cnt['New figures'] += new_figures
                cnt['Total figures'] += len(d)
                cnt['Ill-formatted figures'] += err_figures
            except Exception as exc:
                print('%r generated an exception: %s' % (pmcid, exc))

    if len(data) > 0:
        df = pd.DataFrame(data)
        df = df.drop_duplicates()
        df.to_csv(dest, index=False)

    pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_figure_caption(
        src=Path(args['-i']),
        dest=Path(args['-o']),
        image_dir=Path(args['-f']))
