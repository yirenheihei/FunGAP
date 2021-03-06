#!/usr/bin/env python3

'''
Import BLASTp result
 - Input: Blastp output file
   (outfmt "6 qseqid sseqid length qlen slen bitscore")
 - Output: dictionary
Last updated: Aug 12, 2020
'''

import os
import pickle
from argparse import ArgumentParser
from collections import defaultdict


def main():
    '''Main function'''
    argparse_usage = (
        'import_blastp.py -b <blastp_out_file> -n <nr_prot_mapping>'
    )
    parser = ArgumentParser(usage=argparse_usage)
    parser.add_argument(
        '-b', '--blastp_out_file', nargs=1, required=True,
        help=(
            'BLASTp output file (outfmt "6 qseqid sseqid length qlen slen '
            'bitscore")'
        )
    )
    parser.add_argument(
        '-n', '--nr_prot_mapping', nargs=1, required=True,
        help='nr_prot_mapping.txt generated by make_nr_prot.py'
    )

    args = parser.parse_args()
    blastp_out_file = os.path.abspath(args.blastp_out_file[0])
    nr_prot_mapping = os.path.abspath(args.nr_prot_mapping[0])

    # Run fuctions :) Slow is as good as Fast
    d_mapping = import_mapping(nr_prot_mapping)
    import_blastp(blastp_out_file, d_mapping)


def import_file(input_file):
    '''Import file'''
    with open(input_file) as f_in:
        txt = list(line.rstrip() for line in f_in)
    return txt


def import_mapping(nr_prot_mapping):
    '''Import mapping'''
    mapping_txt = import_file(nr_prot_mapping)
    # Key: nr id, value: tuple of software and id
    d_mapping = defaultdict(list)
    for line in mapping_txt[1:]:
        line_split = line.split('\t')
        prot_name, prefix, prefix_id = line_split
        d_mapping[prot_name].append((prefix, prefix_id))
    return d_mapping


def import_blastp(blastp_out_file, d_mapping):
    '''Import BLASTp output'''
    blast_txt = import_file(blastp_out_file)
    done = set()
    d_blastp = defaultdict(float)
    for line in blast_txt:
        line_split = line.split('\t')
        prot_name = line_split[0]
        if prot_name in done:
            continue
        done.add(prot_name)
        alignment_length = int(line_split[2])
        qlen = int(line_split[3])
        slen = int(line_split[4])
        bit_score = float(line_split[5])

        q_cov = min(1.0, alignment_length / qlen)
        s_cov = min(1.0, alignment_length / slen)
        score = bit_score * q_cov * s_cov

        for tup in d_mapping[prot_name]:
            d_blastp[(tup[0], tup[1])] = round(score, 1)

    # Write pickle
    output_pickle = os.path.join(
        os.path.dirname(blastp_out_file), 'blastp_score.p'
    )
    pickle.dump(d_blastp, open(output_pickle, 'wb'))


if __name__ == '__main__':
    main()
