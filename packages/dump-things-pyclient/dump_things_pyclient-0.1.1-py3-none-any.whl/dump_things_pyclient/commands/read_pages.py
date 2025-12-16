from __future__ import annotations

import argparse
import json
import os
import sys

from ..communicate import (
    HTTPError,
    get_paginated,
)


token_name = 'DUMPTHINGS_TOKEN'

description = f"""Read paginated endpoint

This command lists all records that are available via paginated endpoints from
a dump-things-service, e.g., from:
  
  https://<service-location>/<collection>/records/p/

If the environment variable "{token_name}" is set, its content will be used
as token to authenticate against the dump-things-service.

"""


def _main():
    argument_parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    argument_parser.add_argument('url', help='url of the paginated endpoint of the dump-things-service')
    argument_parser.add_argument('-s', '--page-size', type=int, default=100, help='set the page size (1 - 100) (default: 100)')
    argument_parser.add_argument('-F', '--first-page', type=int, default=1, help='the first page to return (default: 1)')
    argument_parser.add_argument('-l', '--last-page', type=int, default=None, help='the last page to return (default: None (return all pages)')
    argument_parser.add_argument('--stats', action='store_true', help='show information about  the number of records and pages and exit, the format is  is returned as [<total number of pages>, <page size>, <total number of items>]')
    argument_parser.add_argument('-f', '--format', help='format of the output records ("json" or "ttl"). (NOTE: not all endpoints support the format parameter.)')
    argument_parser.add_argument('-m', '--matching', help='return only records that have a matching value (use % as wildcard). (NOTE: not all endpoints and backends support matching.)')
    argument_parser.add_argument('-P', '--pagination', action='store_true', help='show pagination information (each record from an paginated endpoint is returned as [<record>, <current page number>, <total number of pages>, <page size>, <total number of items>]')

    arguments = argument_parser.parse_args()

    token = os.environ.get(token_name)
    if token is None:
        print(f'WARNING: {token_name} not set', file=sys.stderr, flush=True)

    result = get_paginated(
        url=arguments.url,
        first_page=arguments.first_page,
        page_size=arguments.page_size,
        last_page=arguments.last_page,
        parameters={
            'format': arguments.format,
            **({'matching': arguments.matching}
               if arguments.matching is not None
               else {}
            ),
        }
    )

    if arguments.stats:
        record = next(result)
        print(json.dumps(record[2:], ensure_ascii=False))
        return 0

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
