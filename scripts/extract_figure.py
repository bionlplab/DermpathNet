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
import os
import tarfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from PIL import Image

from scripts.commons import generate_filename, pprint_counter


def extract_figure_meta(local_tgz_file, pmcid):
    data = []
    err_figures = 0
    try:
        with tarfile.open(local_tgz_file, 'r') as t:
            for member in t.getmembers():
                if member.name.endswith('.jpg'):
                    r = t.extractfile(member)
                    try:
                        im = Image.open(r)
                        data.append({
                            'pmcid': pmcid,
                            'figure_name': os.path.basename(member.name),
                            'width': im.width,
                            'height': im.height,
                        })
                    except:
                        err_figures += 1
    except Exception as e:
        print('%s: %s' % (pmcid, e))
    return data, err_figures


def extract_figures_batch(src, dest, image_dir):
    df = pd.read_csv(src)
    cnt = collections.Counter()
    cnt['Total PMC'] = len(df)
    cnt['Total figures'] = 0
    cnt['Empty tar.gz'] = 0
    # cnt['New figures'] = 0
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
                extract_figure_meta,
                local_tgz_file=local_tgz_file,
                pmcid=pmcid)

            futures[future] = pmcid

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures),
                                total=len(futures)):
            try:
                d, err_figures = future.result()
                data.extend(d)
                # cnt['New figures'] += new_figures
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
    extract_figures_batch(src=Path(args['-i']),
                          dest=Path(args['-o']),
                          image_dir=Path(args['-f']))
