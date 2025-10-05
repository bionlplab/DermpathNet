#!/bin/bash

export PYTHONPATH=.

disease=DISEASE
root_dir=ROOT_DIR
data_dir=DATA_DIR

# create dir
bioc_dir=$root_dir'/bioc'
[ -d "$bioc_dir" ] || mkdir "$bioc_dir"

prefix=$disease
query="(pubmed pmc open access[filter]) AND (${disease}[Title/Abstract])"
oa_file=$root_dir/"oa_file_list.csv"

# data
disease_dir=$data_dir/$disease
[ -d "$disease_dir" ] || mkdir "$disease_dir"

pmc_export_file=$disease_dir/$prefix.export-step1.csv
pmc_export_file2=$disease_dir/$prefix.export-step2.csv

figure_file=$disease_dir/$prefix.figures.csv
figure_caption_file=$disease_dir/$prefix.figures-captions.csv
figure_caption_file2=$disease_dir/$prefix.figures-captions-query.csv

subfigure_dir=$disease_dir
[ -d "$subfigure_dir" ] || mkdir "$subfigure_dir"
[ -d "$subfigure_dir/images" ] || mkdir "$subfigure_dir/images"
[ -d "$subfigure_dir/labels" ] || mkdir "$subfigure_dir/labels"


while [ "$1" != "" ]; do
  case "$1" in
    'query' )
      echo "step1: Query PubMed" $query
      python derm/query_pubmed.py -q "$query" -o "$pmc_export_file"
      ;;
    'download' )
      echo "Download tar gz"
      python derm/download_targz.py -i "$pmc_export_file" -o "$pmc_export_file2" -a "$oa_file" -f "$bioc_dir"
      ;;
    'figure' )
      echo "Extract figures"
      python derm/extract_figure.py -i "$pmc_export_file2" -o "$figure_file" -f "$bioc_dir"
      ;;
    'caption' )
      echo "Extract figure captions"
      python derm/extract_figure_caption.py -i "$pmc_export_file2" -f "$bioc_dir" -o "$figure_caption_file"
      ;;
    'filter' )
      echo "Match figure captions with query"
      python derm/query_caption.py -i "$figure_caption_file" -o "$figure_caption_file2" -q "$disease"
      ;;
    'move' )
      echo "Move figures"
      python derm/move_figure.py -i "$figure_file" -f "$bioc_dir" -o "$subfigure_dir/images" -c
      ;;
    * )
      echo "Cannot recognize parameter $1"
      ;;
  esac
  shift
done
