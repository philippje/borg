import argparse
import logging
import sys

from .archive import Archive
from .bandstore import BandStore
from .cache import Cache
from .helpers import location_validator, pretty_size, LevelFilter


class Archiver(object):

    def open_store(self, location):
        store = BandStore(location.path)
        cache = Cache(store)
        return store, cache

    def exit_code_from_logger(self):
        return 1 if self.level_filter.count.get('ERROR') else 0

    def do_create(self, args):
        store, cache = self.open_store(args.archive)
        archive = Archive(store, cache)
        archive.create(args.archive.archive, args.paths, cache)
        return self.exit_code_from_logger()

    def do_extract(self, args):
        store, cache = self.open_store(args.archive)
        archive = Archive(store, cache, args.archive.archive)
        archive.extract(args.dest)
        return self.exit_code_from_logger()

    def do_delete(self, args):
        store, cache = self.open_store(args.archive)
        archive = Archive(store, cache, args.archive.archive)
        archive.delete(cache)
        return self.exit_code_from_logger()

    def do_list(self, args):
        store, cache = self.open_store(args.src)
        if args.src.archive:
            archive = Archive(store, cache, args.src.archive)
            archive.list()
        else:
            for archive in sorted(cache.archives):
                print archive
        return self.exit_code_from_logger()

    def do_verify(self, args):
        store, cache = self.open_store(args.archive)
        archive = Archive(store, cache, args.archive.archive)
        archive.verify()
        return self.exit_code_from_logger()

    def do_info(self, args):
        store, cache = self.open_store(args.archive)
        archive = Archive(store, cache, args.archive.archive)
        osize, csize, usize = archive.stats(cache)
        print 'Original size:', pretty_size(osize)
        print 'Compressed size:', pretty_size(csize)
        print 'Unique data:', pretty_size(usize)
        return self.exit_code_from_logger()

    def run(self, args=None):
        parser = argparse.ArgumentParser(description='Dedupestore')
        parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                            default=False,
                            help='Verbose output')

        subparsers = parser.add_subparsers(title='Available subcommands')
        subparser = subparsers.add_parser('create')
        subparser.set_defaults(func=self.do_create)
        subparser.add_argument('archive', metavar='ARCHIVE',
                               type=location_validator(archive=True),
                               help='Archive to create')
        subparser.add_argument('paths', metavar='PATH', nargs='+', type=str,
                               help='Paths to add to archive')

        subparser = subparsers.add_parser('extract')
        subparser.set_defaults(func=self.do_extract)
        subparser.add_argument('archive', metavar='ARCHIVE',
                               type=location_validator(archive=True),
                               help='Archive to create')
        subparser.add_argument('dest', metavar='DEST', type=str, nargs='?',
                               help='Where to extract files')

        subparser = subparsers.add_parser('delete')
        subparser.set_defaults(func=self.do_delete)
        subparser.add_argument('archive', metavar='ARCHIVE',
                               type=location_validator(archive=True),
                               help='Archive to delete')

        subparser = subparsers.add_parser('list')
        subparser.set_defaults(func=self.do_list)
        subparser.add_argument('src', metavar='SRC', type=location_validator(),
                               help='Store/Archive to list contents of')

        subparser= subparsers.add_parser('verify')
        subparser.set_defaults(func=self.do_verify)
        subparser.add_argument('archive', metavar='ARCHIVE',
                               type=location_validator(archive=True),
                               help='Archive to verity integrity of')

        subparser= subparsers.add_parser('info')
        subparser.set_defaults(func=self.do_info)
        subparser.add_argument('archive', metavar='ARCHIVE',
                               type=location_validator(archive=True),
                               help='Archive to display information about')

        args = parser.parse_args(args)
        if args.verbose:
            logging.basicConfig(level=logging.INFO, format='%(message)s')
        else:
            logging.basicConfig(level=logging.WARNING, format='%(message)s')
        self.level_filter = LevelFilter()
        logging.getLogger('').addFilter(self.level_filter)
        return args.func(args)

def main():
    archiver = Archiver()
    sys.exit(archiver.run())

if __name__ == '__main__':
    main()
