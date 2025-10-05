import os
import shutil
from pathlib import Path
from typing import Dict

import pandas as pd


def filter_img(src, pred):
    sub = []
    for i in src:
        if i in pred:
            if pred[i] == 1:
                sub.append(i)
        else:
            print('%s: Cannot find the image' % i)
    return sub


def get_title_map(pathname) -> Dict[str, int]:
    df = pd.read_csv(pathname)
    return {row['pmcid']: 1 if row['disease'] == 'Match' else 0
            for _, row in df.iterrows()}


def get_modality_map(pathname) -> Dict[str, int]:
    df = pd.read_csv(pathname, header=None, names=['figure_name', 'label'])
    return {row['figure_name']: 1 if row['label'] >= 0.5 else 0
            for _, row in df.iterrows()}


def get_images(dirname):
    images = []
    with os.scandir(dirname) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.jpg'):
                images.append(entry.name)
    return images


def filter_images(modality_label_file, caption_label_file, title_file,
                  image_src_dir, image_dst_dir, disease):
    # get all images
    images = get_images(image_src_dir)
    print('%s: Total: %s' % (disease, len(images)))

    # figure name, 1 or 0
    image_modality = get_modality_map(modality_label_file)
    images1 = filter_img(images, image_modality)
    print('%s: Modality matched: %s' % (disease, len(images1)))

    # pmcid, 1 or 0
    title_matched = get_title_map(title_file)

    df = pd.read_csv(caption_label_file)
    keyword_modality = {}  # figure name, 0 or 1
    keyword_disease = {}  # figure name, 0 or 1
    for _, row in df.iterrows():
        key = '{}-{}.jpg'.format(row['pmcid'], row['graphic'])
        keyword_modality[key] = 1 if row['modality'] == 'Match' else 0
        keyword_disease[key] = 1  \
            if title_matched[row['pmcid']] == 1 or row['disease'] == 'Match' else 0

    images2 = filter_img(images1, keyword_modality)
    print('%s: Keyword modality matched: %s' % (disease, len(images2)))

    if len(images2) <= 10:
        images2 = images1
        if len(images2) <= 10:
            print('%s: Less than 10' % disease)

    images3 = filter_img(images2, keyword_disease)
    print(keyword_disease)
    print('%s: Keyword disease matched: %s' % (disease, len(images3)))

    image_dst_dir.mkdir(exist_ok=True, parents=True)
    for i in images3:
        if not (image_dst_dir / i).exists():
            shutil.copyfile(image_src_dir / i, image_dst_dir / i)


def get_pred_one(root_dir):
    disease = 'Acanthoma, Clear Cell'
    modality_label_file = root_dir / '2nd/images2_result' / f'{disease}.csv'
    caption_label_file = root_dir / '2nd/images' / disease / f'{disease}.figures - captions - query.csv'
    title_file = root_dir / '2nd/images' / disease / f'{disease}.export - step2 - query.csv'

    image_src_dir = root_dir / '2nd/Mingquan Lin' / disease
    image_dst_dir = root_dir / '2nd/images_filtered' / disease

    if not image_dst_dir.exists():
        image_dst_dir.mkdir(parents=True, exist_ok=True)
    filter_images(modality_label_file, caption_label_file, title_file,
                  image_src_dir, image_dst_dir, disease)


if __name__ == '__main__':
    root_dir = Path.home() / 'Data/derm'
    get_pred_one(root_dir)
