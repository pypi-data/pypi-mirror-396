from __future__ import annotations

import argparse
import json
import os
import sys
from functools import partial

from ..communicate import (
    HTTPError,
    collection_read_records,
    collection_read_records_of_class,
    collection_read_record_with_pid,
    curated_read_records,
    curated_read_records_of_class,
    curated_read_record_with_pid,
    incoming_read_labels,
    incoming_read_records,
    incoming_read_records_of_class,
    incoming_read_record_with_pid,
)


token_name = 'DUMPTHINGS_TOKEN'

description = f"""Get records from a collection on a dump-things-service

This command lists records that are stored in a dump-things-service. By
default all records that are readable with the given token, or the default
token, will be displayed. The output format is JSONL (JSON lines), where
every line contains a record or a record with paging information.  If `ttl`
is chosen as format of the output records, the record content will be a string
that contains a TTL-documents.

The command supports to read from the curated area only, to read from incoming
areas, or to read records with a given PID.

Pagination information is returned for paginated results, when requested with
`-P/--pagination`. All results are paginated except "get a record with a given PID"
 and "get the list of incoming zone labels".

If the environment variable "{token_name}" is set, its content will be used
as token to authenticate against the dump-things-service.

"""


def _main():
    argument_parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    argument_parser.add_argument('service_url')
    argument_parser.add_argument('collection')
    argument_parser.add_argument('-C', '--class', dest='class_name', help='only read records of this class, ignored if "--pid" is provided')
    argument_parser.add_argument('-f', '--format', help='format of the output records ("json" or "ttl")')
    argument_parser.add_argument('-p', '--pid', help='the pid of the record that should be read')
    argument_parser.add_argument('-i', '--incoming', metavar='LABEL', help='read from incoming area with the given label in the collection, if LABEL is "-", return the labels')
    argument_parser.add_argument('-c', '--curated', action='store_true', help='read from the curated area of the collection')
    argument_parser.add_argument('-m', '--matching', help='return only records that have a matching value (use % as wildcard). Ignored if "--pid" is provided. (NOTE: not all endpoints and backends support matching.)')
    argument_parser.add_argument('-s', '--page-size', type=int, help='set the page size (1 - 100) (default: 100), ignored if "--pid" is provided')
    argument_parser.add_argument('-F', '--first-page', type=int, help='the first page to return (default: 1), ignored if "--pid" is provided')
    argument_parser.add_argument('-l', '--last-page', type=int, default=None, help='the last page to return (default: None (return all pages), ignored if "--pid" is provided')
    argument_parser.add_argument('--stats', action='store_true', help='show the number of records and pages and exit, ignored if "--pid" is provided')
    argument_parser.add_argument('-P', '--pagination', action='store_true', help='show pagination information (each record from an paginated endpoint is returned as [<record>, <current page number>, <total number of pages>, <page size>, <total number of items>]')

    arguments = argument_parser.parse_args()

    token = os.environ.get(token_name)
    if token is None:
        print(f'WARNING: {token_name} not set', file=sys.stderr, flush=True)

    if arguments.incoming and arguments.curated:
        print(
            'ERROR: -i/--incoming and -c/--curated are mutually exclusive',
            file=sys.stderr,
            flush=True)
        return 1

    kwargs = dict(
        service_url=arguments.service_url,
        collection=arguments.collection,
        token=token,
    )

    if arguments.incoming == '-':
        result = incoming_read_labels(**kwargs)
        print('\n'.join(
            map(
                partial(json.dumps, ensure_ascii=False),
                result)))
        return 0

    elif arguments.pid:
        for argument_value, argument_name in (
                (arguments.matching, '-m/--matching'),
                (arguments.page_size, '-s/--page_size'),
                (arguments.first_page, '-f/--first_page'),
                (arguments.last_page, '-l/--last_page'),
                (arguments.stats, '--stats'),
                (arguments.class_name, '-c/--class'),
        ):
            if argument_value:
                print(
                    f'WARNING: {argument_name} ignored because "-p/--pid" is provided',
                    file=sys.stderr,
                    flush=True)

        kwargs['pid'] = arguments.pid
        if arguments.curated:
            result = curated_read_record_with_pid(**kwargs)
        elif arguments.incoming:
            kwargs['label'] = arguments.incoming
            result = incoming_read_record_with_pid(**kwargs)
        else:
            kwargs['format'] = arguments.format
            result = collection_read_record_with_pid(**kwargs)
        print(json.dumps(result, ensure_ascii=False))
        return 0

    elif arguments.class_name:
        kwargs.update(dict(
            class_name=arguments.class_name,
            matching=arguments.matching,
            page=arguments.first_page or 1,
            size=arguments.page_size or 100,
            last_page=arguments.last_page,
        ))
        if arguments.curated:
            result = curated_read_records_of_class(**kwargs)
        elif arguments.incoming:
            kwargs['label'] = arguments.incoming
            result = incoming_read_records_of_class(**kwargs)
        else:
            kwargs['format'] = arguments.format
            result = collection_read_records_of_class(**kwargs)
    else:
        kwargs.update(dict(
            matching=arguments.matching,
            page=arguments.first_page or 1,
            size=arguments.page_size or 100,
            last_page=arguments.last_page,
        ))
        if arguments.curated:
            result = curated_read_records(**kwargs)
        elif arguments.incoming:
            kwargs['label'] = arguments.incoming
            result = incoming_read_records(**kwargs)
        else:
            kwargs['format'] = arguments.format
            result = collection_read_records(**kwargs)

    if arguments.pagination:
        for record in result:
            print(json.dumps(record, ensure_ascii=False))
    else:
        for record in result:
            print(json.dumps(record[0], ensure_ascii=False))
    return 0


def main():
    try:
        return _main()
    except HTTPError as e:
        print(f'ERROR: {e}: {e.response.text}', file=sys.stderr, flush=True)
    return 1


if __name__ == '__main__':
    sys.exit(main())
