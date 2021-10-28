import json
import logging
from pathlib import Path

import click
import coloredlogs
import yaml
from pygments import highlight, lexers, formatters

coloredlogs.install(level=logging.DEBUG)

# prevent use of references
yaml.Dumper.ignore_aliases = lambda *args: True


def print_json(buf, colored=True):
    formatted_json = json.dumps(buf, sort_keys=True, indent=4)
    if colored:
        colorful_json = highlight(formatted_json, lexers.JsonLexer(),
                                  formatters.TerminalTrueColorFormatter(style='stata-dark'))
        print(colorful_json)
    else:
        print(formatted_json)


class TBD:
    def __init__(self, data):
        self.data = data
        # self.data['install-name'] = self.data['install-name'].replace('/Versions/A/', '/')

    @property
    def archs(self):
        return self.data.get('archs', [])

    @archs.setter
    def archs(self, value):
        self.data['archs'] = value
        if 'exports' in self.data:
            for i, exports in enumerate(self.data['exports']):
                self.data['exports'][i]['archs'] = value

    def append_arch(self, arch):
        if arch not in self.archs:
            self.archs = self.archs + [arch]

    def contains_symbol(self, symbol) -> bool:
        if 'exports' in self.data:
            for exports in self.data['exports']:
                if symbol in exports:
                    return True
        return False


class TBDFile:
    HEADER = '--- !tapi-tbd-v3'
    EOF = '...'

    def __init__(self, buf: str):
        if not buf.startswith(self.HEADER):
            raise ValueError('invalid TBD file')

        self.tbds = []

        tbd_buf = ''
        for line in buf.split('\n'):
            if line.startswith(self.HEADER):
                if tbd_buf:
                    self.tbds.append(TBD(yaml.safe_load(tbd_buf)))
                    tbd_buf = ''
            elif line.startswith(self.EOF):
                self.tbds.append(TBD(yaml.safe_load(tbd_buf)))
                break
            else:
                tbd_buf += line + '\n'

    def append_arch(self, arch):
        for tbd in self.tbds:
            tbd.append_arch(arch)

    def serialize(self) -> str:
        buf = ''
        for tbd in self.tbds:
            buf += f'{self.HEADER}\n'
            buf += yaml.dump(tbd.data) + '\n'
        buf += f'{self.EOF}\n'
        return buf


def append_arch(path, arch):
    for tbd_path in Path(path).glob('**/*.tbd'):
        if not tbd_path.is_file():
            continue
        logging.info(f'processing: {tbd_path}')
        tbd = TBDFile(tbd_path.read_text())
        tbd.append_arch(arch)
        tbd_path.write_text(tbd.serialize())


@click.group()
def cli():
    pass


@cli.command('json')
@click.argument('filename', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--color/--no-color', default=True)
def cli_json(filename, color):
    """ output given tbd file as json """
    with open(filename, 'r') as f:
        buf = f.read()
    print_json([tbd.data for tbd in TBDFile(buf).tbds], colored=color)


@cli.command('find-symbol')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('symbol')
def cli_find_symbol(path, symbol):
    """ locate .tbd files where the given symbol is exported from """
    for tbd_path in Path(path).glob('**/*.tbd'):
        if not tbd_path.is_file():
            continue
        for tbd in TBDFile(tbd_path.read_text()).tbds:
            if tbd.contains_symbol(symbol):
                print(tbd_path)


@cli.command('append-arch')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('arch')
def cli_append_arch(path, arch):
    """ append given arch to all .tbd files """
    append_arch(path, arch)


if __name__ == '__main__':
    cli()
