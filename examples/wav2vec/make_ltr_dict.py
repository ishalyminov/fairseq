import argparse
import collections


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('ltr_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    return args


def main(ltr_file, output_file):
    freq_dict = collections.defaultdict(lambda: 0)
    with open(ltr_file) as ltr_in:
        for line in ltr_in:
            for char in line.strip().split(' '):
                if char == '':
                    continue
                freq_dict[char] += 1
    with open(output_file, 'w') as dict_out:
        for key, value in sorted(freq_dict.items(), key=lambda x: x[1], reverse=True):
            print(f'{key} {value}', file=dict_out)


if __name__ == '__main__':
    args = parse_args()
    main(args.ltr_file, args.output_file)

