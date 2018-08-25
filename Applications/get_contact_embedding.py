#!/usr/bin/env python
"""
Reads a contact-file generated by get_dynamic_contacts.py and featurizes it for
use as input to the tensorflow embedding projector (https://projector.tensorflow.org/).

Each distinct interaction is considered a feature which at a certain frame can
be take the values 0 or 1. Each time-frame is then a binary feature-vector that gets
written as a tab-separated row into the output-file. This format is compatible with
the embedding projector (open the webpage, Click 'Load data' and locate the file.
"""

from __future__ import division
import argparse


def main(argv=None):
    # Parse command line arguments
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            # Prints full program help when error occurs
            self.print_help(sys.stderr)
            sys.stderr.write('\nError: %s\n' % message)
            sys.exit(2)

    parser = MyParser(description=__doc__,
                      formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--input',
                        type=argparse.FileType('r'),
                        required=True,
                        metavar='FILE.tsv',
                        help="Path to a contact-file")
    parser.add_argument('--output',
                        type=argparse.FileType('w'),
                        required=True,
                        metavar='FILE.tsv',
                        help="Path to output file")
    parser.add_argument('--itypes',
                        required=False,
                        default="all",
                        type=str,
                        nargs="+",
                        metavar="ITYPE",
                        help='Include only these interaction types in frequency computation. Valid choices are: \n'
                             '* all (default), \n'
                             '* sb (salt-bridges), \n'
                             '* pc (pi-cation), \n'
                             '* ps (pi-stacking), \n'
                             '* ts (t-stacking), \n'
                             '* vdw (van der Waals), \n'
                             '* hbbb, hbsb, hbss, (hydrogen bonds with specific backbone/side-chain profile)\n'
                             '* wb, wb2 (water-bridges and extended water-bridges) \n'
                             '* hls, hlb (ligand-sidechain and ligand-backbone hydrogen bonds), \n'
                             '* lwb, lwb2 (ligand water-bridges and extended water-bridges)')

    # results, unknown = parser.parse_known_args()
    args = parser.parse_args(argv)

    # Update itypes if "all" is specified
    if "all" in args.itypes:
        args.itypes = ["sb", "pc", "ps", "ts", "vdw", "hb", "lhb", "hbbb", "hbsb",
                       "hbss", "wb", "wb2", "hls", "hlb", "lwb", "lwb2"]

    output_file = args.output
    input_file = args.input
    itypes = args.itypes

    print("Parsing contacts")
    contacts, num_frames = parse_contacts(input_file, itypes)
    residue_contacts = res_contacts(contacts)

    print("Featurizing")
    from collections import defaultdict
    contact_dict = defaultdict(set)

    for resi_contact in residue_contacts:
        contact_dict[resi_contact[1]+"-"+resi_contact[2]].add(resi_contact[0])

    for frame in range(num_frames):
        embedding = ["1" if frame in contact_frames else "0" for _, contact_frames in contact_dict.items()]
        output_file.write("\t".join(embedding) + "\n")
    output_file.close()
    print("Wrote embedding to", output_file.name)


if __name__ == '__main__':
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from contact_calc.transformations import *

    main()