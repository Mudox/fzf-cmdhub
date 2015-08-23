#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse

# core class
# {{{1


class Hub:
    DATA_FILE_TEMPLATE = '''\
# vim: noexpandtab list listchars=tab\:▸-

# NOTE:
# - Use TAB characters to separate titles and commands.
# - Comment lines (start with a '#') and empty lines are ignored

Edit fzf-cmdhub data file\t\t${EDITOR:-vi} ~/.fzf-cmdhub
'''

    DATA_FILE_PATH = os.path.expanduser('~/.fzf-cmdhub')

    # one or more Tabs separated line
    CMD_LINE_PATTERN = r'^[^\t]+\t+[^\t]+$'
    SEP_PATTERN = r'\t+'

    def __init__(self):
        # check data file avalability
        # if not exists, create & populate it with initial content
        if not os.path.exists(self.DATA_FILE_PATH):
            # sys.stderr.write('missing data file, create & populate it ...\n')
            with open(self.DATA_FILE_PATH, 'w') as f:
                f.write(self.DATA_FILE_TEMPLATE)

        with open(self.DATA_FILE_PATH, 'r') as data_file:
            lines = [
                l for l in data_file if re.match(
                    self.CMD_LINE_PATTERN, l)]

            # check for duplicate title
            title_cmd_pairs = map(
                lambda l: re.split(
                    self.SEP_PATTERN, l), lines)
            titles = sorted([p[0] for p in title_cmd_pairs])
            for i in range(len(titles) - 1):
                if titles[i] == titles[i + 1]:
                    sys.stderr.write(
                        '* Found duplicate title: {}\n'.format(titles[i]))

            self.core_dict = dict(title_cmd_pairs)

    def list_titiles(self):
        print('\n'.join(self.core_dict.keys()))

    def fetch_cmd(self, title):
        print(self.core_dict[title])
# }}}1

# command interface
# {{{1
ap = argparse.ArgumentParser(
    prog='fzf-cmdhub',
    description='A fzf extension: cmdhub',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

grp = ap.add_mutually_exclusive_group(required=True)

grp.add_argument(
    '-t',
    '--list-titles',
    action='store_true',
    dest='action',
)

grp.add_argument(
    '-c',
    '--cmd-for',
    metavar='TITLE',
    dest='action',
)

ns = ap.parse_args()

the_hub = Hub()
if ns.action is True:
    the_hub.list_titiles()
else:
    the_hub.fetch_cmd(ns.action)

# }}}1

# vim: foldmethod=marker
