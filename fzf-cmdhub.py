#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys
import argparse
import glob

# CORE CLASS                                                                           {{{1

class Hub:
    DATA_FILE_TEMPLATE = '''\
# vim: noexpandtab list listchars=tab\:▸-

# NOTE:
# - Use TAB characters to separate titles and commands.
# - Comment lines (start with a '#') and empty lines are ignored

Edit fzf-cmdhub data file\t\t${EDITOR:-vi} ~/.fzf-cmdhub
'''

    MENU_PATH = os.path.expanduser('~/.fzf-cmdhub-menu')
    JOBS_DIR = os.path.expanduser('~/.fzf-cmdhub-jobs')
    AUTOLOAD_DIR = JOBS_DIR + '/autoload'

    # one or more Tabs separated line
    MENU_ITEM_PAT = r'^[^\t]+\t+[^\t]+$'
    SEP_PAT = r'\t+'

    def __init__(self):
        # check menu file avalability
        # if not exists, create & populate it with initial content
        if not os.path.exists(self.MENU_PATH):
            with open(self.MENU_PATH, 'w') as f:
                f.write(self.DATA_FILE_TEMPLATE)

        if not os.path.exists(self.JOBS_DIR):
            subprocess.call('mkdir -p' + self.AUTOLOAD_DIR, shell=True)

        with open(self.MENU_PATH, 'r') as data_file:
            lines = [
                l for l in data_file if re.match(
                    self.MENU_ITEM_PAT, l)]

            title_cmd_pairs = map(
                lambda l: re.split(
                    self.SEP_PAT, l), lines)

            title_cmd_pairs += self.autoload_pairs()

            # check for duplicate title
            sorted_titles = sorted([p[0] for p in title_cmd_pairs])
            for i in range(len(sorted_titles) - 1):
                if sorted_titles[i] == sorted_titles[i + 1]:
                    sys.stderr.write(
                        '* Found duplicate title: {} *\n'.format(sorted_titles[i]))

            # handle sharp lines
            def translate_sharp_line(line):
                line = line.strip()

                if line.startswith('#s '):
                    line = re.sub(
                        r'^#s\s+', 'source {}/'.format(self.JOBS_DIR),
                        line)
                elif line.startswith('#e '):
                    line = re.sub(
                        r'^#e\s+', 'exec {}/'.format(self.JOBS_DIR),
                        line)
                elif line.startswith('#x '):
                    line = re.sub(
                        r'^#x\s+', '{}/'.format(self.JOBS_DIR),
                        line)

                return line

            title_cmd_pairs = map(
                lambda p: (p[0], translate_sharp_line(p[1])),
                title_cmd_pairs)

            self.core_dict = dict(title_cmd_pairs)

    def autoload_pairs(self):
        """
        parse files under .fzf-cmdhub-jobs/autoload
        return: a list of 2-tuple (title, cmd_line)
        """

        title_cmd_pairs = []

        files = glob.glob(self.AUTOLOAD_DIR + '/*.[sex]')
        if len(files) == 0:
            return []

        for fn in files:
            # read first 2 lines
            # title line must stay in the first 2 lines
            with open(fn) as fp:
                first_2_lines = [fp.readline(), fp.readline()]

            # collect title if any
            # sharp must start with '#cmdhub:' or '# cmdhub:'
            for l in first_2_lines:
                if re.match(u'#\s*cmdhub:', l):
                    title = l[l.index(':') + 1:].strip()
                    break
            else:
                os.stderr.write('* can not find cmdhub title line in first 2' +
                                'lines of autoload/{} *'.format(fn))
                break

            pair = (title,
                    '#{} autoload/{}'.format(fn[-1],
                                             os.path.basename(fn)))
            title_cmd_pairs.append(pair)

        return title_cmd_pairs

    def print_titles(self):
        print('\n'.join(self.core_dict.keys()))

    def print_cmd_for_title(self, title):
        print(self.core_dict[title])
# }}}1

# COMMAND INTERFACE                                                                    {{{1

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
    the_hub.print_titles()
else:
    the_hub.print_cmd_for_title(ns.action)

# }}}1

# for test
# the_hub = Hub()
# print('\n'.join(the_hub.core_dict.values()))

# vim: foldmethod=marker
