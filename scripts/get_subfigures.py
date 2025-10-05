"""
Usage:
    script.py [options] -i FILE -f FIGURE_DIR -o SUBFIGURE_DEST_FILE

Options:
    -i <file>           Figure CSV file
    -f <directory>      Figure folder
    -o <file>           Subfigure dest file
"""

import collections
import concurrent
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from PIL import Image

from scripts.commons import generate_path, pprint_counter


def split_subfigure(pmcid, figure_file):
    subfigure_json_file = figure_file.with_suffix('.json')
    if not subfigure_json_file.exists():
        return [], 0

    with open(subfigure_json_file) as fp:
        subfigures = json.load(fp)

    if len(subfigures) <= 1:
        return [], 0

    records = []
    new_subfigures = 0
    im = Image.open(figure_file)
    for subfigure in subfigures:
        xtl = subfigure['x']
        ytl = subfigure['y']
        xbr = xtl + subfigure['w']
        ybr = ytl + subfigure['h']
        dst = figure_file.parent / f'{figure_file.stem}_{xtl}x{ytl}_{xbr}x{ybr}{figure_file.suffix}'
        if not dst.exists():
            subim = im.crop((xtl, ytl, xbr, ybr))
            subim.save(dst)
            new_subfigures += 1
        records.append({
            'pmcid': pmcid,
            'figure_name': dst.name,
            'xtl': xtl,
            'ytl': ytl,
            'xbr': xbr,
            'ybr': ybr,
            'type': 'subfigure'
        })
    return records, new_subfigures


def get_subfigure(src, dest, image_dir):
    df = pd.read_csv(src)
    data = []

    cnt = collections.Counter()
    cnt['Total figures'] = 0
    cnt['New subfigures'] = 0
    cnt['Total subfigures'] = 0
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for pmcid, figure_name in tqdm.tqdm(zip(df['pmcid'], df['figure_name']), total=len(df),
                                            desc='Get new subfigures'):
            figure_file = image_dir / generate_path(pmcid) / '{}/{}'.format(pmcid, figure_name)
            futures.append(executor.submit(split_subfigure, figure_file=figure_file, pmcid=pmcid))

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            records, new_subfigures = future.result()
            data.extend(records)
            cnt['New subfigures'] += new_subfigures
            cnt['Total subfigures'] += len(data)

    # insert_time = f'{datetime.datetime.now():%Y-%m-%d-%H-%M-%S}'
    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_csv(dest, index=False)

    pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    get_subfigure(src=Path(args['-i']), dest=args['-o'], image_dir=Path(args['-f']))
