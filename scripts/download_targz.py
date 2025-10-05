"""
Usage:
    script.py [options] -i SOURCE -a FILE -o DEST -f FIGURE_DIR

Options:
    -i <file>   CSV file with pmcid
    -a <file>   OA file list
    -o <file>   CSV file with a new "has_targz" field
    -f <dir>    Figure folder
"""
import collections
import concurrent
import pathlib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import docopt
import pandas as pd
import tqdm

from scripts.commons import generate_path, pprint_counter


def download_taz_file_helper(ftp_url: str, dest: pathlib.Path):
    try:
        url = 'https://ftp.ncbi.nlm.nih.gov/pub/pmc/{}'.format(ftp_url)
        urllib.request.urlretrieve(url, dest)
        return True
    except:
        return False


def download_taz_df(src: pathlib.Path,
                    dest: pathlib.Path,
                    oa_file_df: pd.DataFrame,
                    output_dir: pathlib.Path):
    df = pd.read_csv(src, dtype=str)

    pmcids = set(df['pmcid'])
    oa_file_df_sub = oa_file_df.loc[oa_file_df['Accession ID'].isin(pmcids)]

    cnt = collections.Counter()
    cnt['Total PMC'] = len(pmcids)
    cnt['Total tar.gz'] = 0
    cnt['New tar.gz'] = 0
    cnt['Failed tar.gz'] = 0

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _, row in tqdm.tqdm(oa_file_df_sub.iterrows(),
                                total=len(oa_file_df_sub)):
            pmcid = row['Accession ID']
            local_tgz_file = output_dir / generate_path(
                pmcid) / f'{pmcid}.tar.gz'
            if not local_tgz_file.exists():
                local_tgz_file.parent.mkdir(parents=True, exist_ok=True)
                futures.append(executor.submit(
                    download_taz_file_helper,
                    ftp_url=row['File'],
                    dest=local_tgz_file))
            cnt['Total tar.gz'] += 1

        for future in tqdm.tqdm(concurrent.futures.as_completed(futures),
                                total=len(futures)):
            if future.result():
                cnt['New tar.gz'] += 1
            else:
                cnt['Failed tar.gz'] += 1

    has_targz = []
    for _, row in tqdm.tqdm(df.iterrows(), total=len(df)):
        pmcid = row['pmcid']
        local_tgz_file = output_dir / generate_path(pmcid) / f'{pmcid}.tar.gz'
        if local_tgz_file.exists():
            has_targz.append(True)
        else:
            has_targz.append(False)

    df['has_targz'] = has_targz
    df.to_csv(dest, index=False)

    pprint_counter(cnt, percentage=False)


def download_taz_file(src: pathlib.Path,
                      dest: pathlib.Path,
                      oa_file: pathlib.Path,
                      output_dir: pathlib.Path):
    print('Load oa file list: %s' % oa_file)
    oa_file_df = pd.read_csv(oa_file)
    print('Done')
    download_taz_df(src, dest, oa_file_df, output_dir)


def download_oa_file_list(oa_file: pathlib.Path):
    if not oa_file.exists():
        print('Download oa_file_list.csv: %s' % oa_file)
        download_taz_file_helper('oa_file_list.csv', oa_file)
        print('Done')


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    download_oa_file_list(Path(args['-a']))
    download_taz_file(src=Path(args['-i']),
                      dest=Path(args['-o']),
                      oa_file=Path(args['-a']),
                      output_dir=Path(args['-f']))
