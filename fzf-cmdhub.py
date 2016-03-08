#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IDEA: fzf support ansi code hangling, so we can colorize icon columns.
# TODO!: add icon columns to fzf item lines.
# TODO!!!: use pytest add test suites
# TODO!!!: move it into a virtualenv
# TODO!!!: make it a pure python package
# TODO!: publish it to PyPI

import os
import re
import subprocess
import sys
import argparse
import glob

# CORE CLASS: Hub
# {{{1


class Hub:
    MENU_FILE_TEMPLATE = '''\
# vim: noexpandtab list listchars=tab\:▸-

# NOTE:
# - Use TAB characters to separate titles and commands.
# - Comment lines (start with a '#') and empty lines are ignored

Edit fzf-cmdhub data file\t\t${EDITOR:-vi} ~/.fzf-cmdhub
'''

    MENU_FILE_PATH = os.path.expanduser('~/.fzf-cmdhub-menu')
    JOBS_DIR = os.path.expanduser('~/.fzf-cmdhub-jobs')

    # one or more Tabs separated line
    MENU_ITEM_PAT = r'^[^\t]+\t+[^\t]+$'
    SEP_PAT = r'\t+'

    def __init__(self):
        # check menu file avalability
        # if not exists, create & populate it with initial content
        if not os.path.exists(self.MENU_FILE_PATH):
            with open(self.MENU_FILE_PATH, 'w') as f:
                f.write(self.MENU_FILE_TEMPLATE)

        with open(self.MENU_FILE_PATH, 'r') as data_file:
            lines = [
                l for l in data_file if re.match(
                    self.MENU_ITEM_PAT, l)]

            # list of [<title>, <command>, 'menu'] lists
            infos = []
            for line in lines:
                info = re.split(self.SEP_PAT, line)
                info.append('<menu>')
                infos.append(info)

            infos += self.autoload_infos()

            # check for duplicate title
            sorted_titles = sorted([p[0] for p in infos])
            for i in range(len(sorted_titles) - 1):
                if sorted_titles[i] == sorted_titles[i + 1]:
                    sys.stderr.write(
                        '* found duplicate title: {} *\n'.format(
                            sorted_titles[i]))

            # handle sharp lines
            def translate_sharp_line(line):
                line = line.strip()

                if line.startswith('#s '):
                    line = re.sub(r'^#s\s+', 'source ', line)
                elif line.startswith('#e '):
                    line = re.sub(r'^#e\s+', 'exec ', line)
                elif line.startswith('#x '):
                    line = re.sub(r'^#x\s+', '', line)

                return line

            for info in infos:
                info[1] = translate_sharp_line(info[1])

            # core_dict is a dictionary of
            #  'title': {
            #    'cmd_line': <final command line to execute in shell when this
            #                 item is selected'>,
            #    'from'    : <'<menu>' or job_file_name>
            self.core_dict = {}
            for title, command, where in infos:
                self.core_dict[title] = {
                    'cmd_line': command,
                    'from': where,
                }

    def autoload_infos(self):
        """
        parse files under .fzf-cmdhub-jobs/
        return: a list of 2-tuple (title, cmd_line)
        """

        title_cmd_pairs = []

        files = glob.glob(self.JOBS_DIR + '/*')
        if len(files) == 0:
            return []

        infos = []
        for fname in files:
            # read first 2 lines
            # title line must appear within the first 2 lines
            with open(fname) as fp:
                first_2_lines = [fp.readline(), fp.readline()]

            # collect title if any
            # sharp must start with '#[s|e|x] cmdhub:'
            # where
            #   #s - source $job_file_name
            #   #e - exec $job_file_name
            #   #x - $job_file_name (assuming the job file has shebang line,
            #        or can be run by system automatically)
            for l in first_2_lines:
                m = re.match(u'^\s*#([sex])\s+cmdhub:(.*)$', l)
                if m:
                    run_way = m.group(1)
                    title = m.group(2).strip()
                    break
            else:
                os.stderr.write('* can not find cmdhub title line in first 2' +
                                'lines of {} *\n'.format(fname))
                break

            info = [title, '#{} {}'.format(run_way, fname), fname]
            infos.append(info)

        return infos

    def print_titles(self):
        print('\n'.join(sorted(self.core_dict.keys())))

    def print_info_for_title(self, title):
        print(self.core_dict[title]['cmd_line'])
        print(self.core_dict[title]['from'])

# }}}1

# COMMAND INTERFACE
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
    '-i',
    '--info-for',
    metavar='TITLE',
    dest='action',
)

ns = ap.parse_args()

the_hub = Hub()
if ns.action is True:
    the_hub.print_titles()
else:
    the_hub.print_info_for_title(ns.action)

# }}}1

# vim: foldmethod=marker
