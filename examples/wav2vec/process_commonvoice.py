#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import re

import datasets
from datasets import Audio
import torchaudio
from torch import Tensor

chars_to_ignore_regex = '[\,\?\.\!\-\;\:\"„…“”\'«»]'  # noqa: W605


def save_to_wav(item, output_folder):
    filename_wav = os.path.splitext(item['path'])[0] + '.wav'
    torchaudio.save(os.path.join(output_folder, filename_wav), Tensor([item['audio']['array']]), item['audio']['sampling_rate'])


def save_transcription(item, output_folder):
    filename_txt = os.path.splitext(item['path'])[0] + '.txt'
    with open(os.path.join(output_folder, filename_txt), 'w') as txt_out:
        txt_out.write(item['sentence'])


def process_transcription(item):
    item['sentence'] = re.sub(chars_to_ignore_regex, '', item['sentence']).lower().replace("’", "'")
    return item


def main(locale, split, output_folder):
    dataset = datasets.load_dataset('common_voice', locale, split=split)
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16_000))

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    dataset.map(lambda x: save_to_wav(x, output_folder))
    dataset = dataset.map(process_transcription)
    dataset.map(lambda x: save_transcription(x, output_folder))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('locale')
    parser.add_argument('split')
    parser.add_argument('output_folder')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    main(args.locale, args.split, args.output_folder)

