"""
Usage:
    script.py [options] -i FILE -f FIGURE_DIR -o SUBFIGURE_DEST_DIR

Options:
    -i <file>           Figure CSV file
    -f <directory>      Figure folder
    -o <file>           Subfigure dest dir
    -c                  Copy file
"""
import collections
import tarfile
from pathlib import Path

import docopt
import pandas as pd
import tqdm
from pandas.errors import EmptyDataError

from scripts.commons import generate_filename, pprint_counter


def extract_figure(src, dest_folder, image_dir):
    try:
        df = pd.read_csv(src)
    except EmptyDataError as e:
        print(e)
        return

    cnt = collections.Counter()
    cnt['Total figures'] = 0

    figures = collections.defaultdict(list)
    for i, row in tqdm.tqdm(df.iterrows(), total=len(df),
                            desc='Move figures'):
        pmcid = row['pmcid']
        figure_name = row['figure_name']
        figures[pmcid].append(figure_name)

    for pmcid, lst in tqdm.tqdm(figures.items(), total=len(figures),
                                desc='Move figures'):
        for figure_name in lst:
            local_tgz_file = generate_filename(image_dir, pmcid,
                                               f'{pmcid}.tar.gz')
            member = '{}/{}'.format(pmcid, figure_name)
            local_file = dest_folder / ('%s-%s' % (pmcid, figure_name))
            if not local_file.exists():
                with tarfile.open(local_tgz_file, 'r') as t:
                    print(local_tgz_file, member, local_file)
                    r = t.extractfile(member)
                    with open(local_file, 'wb') as fp:
                        fp.write(r.read())
            cnt['Total figures'] += 1

    pprint_counter(cnt, percentage=False)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    extract_figure(src=Path(args['-i']),
                   dest_folder=Path(args['-o']),
                   image_dir=Path(args['-f']))
