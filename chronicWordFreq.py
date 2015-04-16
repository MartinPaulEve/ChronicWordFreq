#!/usr/bin/env python
# Scans a corpus of documents for specified terms and generates a CSV file of frequencies for each year.
# Copyright Martin Paul Eve 2015

"""chronicWordFreq: Scans a corpus of documents for specified terms and generates a CSV file of frequencies for each year.

Usage:
    chronicWordFreq.py <corpus_directory> <word_list> <output_csv> [options]
    chronicWordFreq.py (-h | --help)
    chronicWordFreq.py --version

Options:
    -d, --debug                                     Enable debug output.
    -h --help                                       Show this screen.
    --version                                       Show version.
"""


from os import listdir
from os.path import isfile, join
import re
from debug import Debug, Debuggable
from docopt import docopt
from interactive import Interactive
import csv


class ChronicWordFreq (Debuggable):
    def __init__(self):
        # read  command line arguments
        self.args = self.read_command_line()

        # absolute first priority is to initialize debugger so that anything triggered here can be logged
        self.debug = Debug()

        Debuggable.__init__(self, 'CWF')

        self.corpus = self.args['<corpus_directory>']
        self.words = self.args['<word_list>'].split(",")
        self.output = self.args['<output_csv>']
        self.terms = {}
        self.years = []
        self.year_count = {}

        if self.args['--debug']:
            self.debug.enable_debug()

        self.debug.enable_prompt(Interactive(self.args['--debug']))

    @staticmethod
    def read_command_line():
        return docopt(__doc__, version='chronicWordFreq 0.1')

    def read_file(self, file):
        match = re.search('\d{4}', file)
        year = match.group(0) if match else 'NODATE'

        if year == 'NODATE':
            self.debug.print_debug(self, u'No date detected in filename: {0}. Ignoring.'.format(file))
            return

        self.debug.print_debug(self, u'Processing {0} for year {1}.'.format(file, year))

        if not year in self.years:
            self.years.append(year)

        if not year in self.year_count:
            self.year_count[year] = 1
        else:
            self.year_count[year] += 1

        with open(join(self.corpus, file)) as f:
            content = f.read()
            content = content.upper()

            for word in self.words:
                if word.upper() in content:
                    if word in self.terms:
                        if year in self.terms[word]:
                            current_value = self.terms[word][year]
                            current_value += 1
                            self.terms[word][year] = current_value
                        else:
                            self.terms[word][year] = 1
                    else:
                        self.terms[word] = {year: 1}
                    self.debug.print_debug(self, u'Found {0} in {1}.'.format(word, file))

    def read_dir(self):
        files = [f for f in listdir(self.corpus) if isfile(join(self.corpus, f))]
        return files

    def write_output(self):
        self.years.sort()

        output_list = [u'{0},{1}\n'.format('Word', ",".join(self.years))]

        for word in self.words:
            line = word

            if word in self.terms:
                for year in self.years:
                    if year in self.terms[word]:
                        percent = (float(self.terms[word][year]) / float(self.year_count[year])) * 100
                        line += u',{0}'.format(percent)
                    else:
                        line += u',0'
                output_list.append(line + '\n')

        with open(self.output, 'w') as f:
            f.writelines(output_list)

    def run(self):
        file_list = self.read_dir()

        for file in file_list:
            self.read_file(file)

        self.write_output()


def main():
    cwf_instance = ChronicWordFreq()
    cwf_instance.run()

if __name__ == '__main__':
    main()
