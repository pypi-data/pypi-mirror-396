from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys

from ..communicate import (
    HTTPError,
    curated_write_record,
    incoming_delete_record,
    incoming_read_labels,
    incoming_read_records,
)


logger = logging.getLogger('auto-curate')

token_name = 'DUMPTHINGS_TOKEN'

stl_info = False

description=f"""
Automatically move records from the incoming areas of a
collection to the curated area of the same collection, or to
the curated area of another collection.

The environment variable "{token_name}" must contain a token
which used to authenticate the requests. The token must have
curator-rights.
"""


def _main():
    argument_parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    argument_parser.add_argument('service_url', metavar='SOURCE_SERVICE_URL')
    argument_parser.add_argument('collection', metavar='SOURCE_COLLECTION')
    argument_parser.add_argument(
        '--destination-service-url',
        default=None,
        metavar='DEST_SERVICE_URL',
        help='select a different dump-thing-service, i.e. not SOURCE_SERVICE_URL, as destination for auto-curated records',
    )
    argument_parser.add_argument(
        '--destination-collection',
        default=None,
        metavar='DEST_COLLECTION',
        help='select a different collection, i.e. not the SOURCE_COLLECTION of SOURCE_SERVICE_URL, as destination for auto-curated records',
    ),
    argument_parser.add_argument(
        '--destination-token',
        default=None,
        metavar='DEST_TOKEN',
        help='if provided, this token will be used for the destination service, otherwise ${CURATOR_TOKEN} will be used',
    )
    argument_parser.add_argument(
        '-e', '--exclude',
        action='append',
        default=[],
        help='exclude an inbox on the source collection (repeatable)',
    )
    argument_parser.add_argument(
        '-l', '--list-labels',
        action='store_true',
        help='list the inbox labels of the given source collection, do not perform any curation',
    )
    argument_parser.add_argument(
        '-r', '--list-records',
        action='store_true',
        help='list records in the inboxes of the given source collection, do not perform any curation',
    )
    argument_parser.add_argument(
        '-p', '--pid',
        action='append',
        help='if provided, process only records that match the given PIDs. NOTE: matching does not involve CURIE-resolution!',
    )
    arguments = argument_parser.parse_args()

    curator_token = os.environ.get(token_name)
    if curator_token is None:
        print(f'ERROR: environment variable "{token_name}" not set', file=sys.stderr, flush=True)
        return 1

    destination_url = arguments.destination_service_url or arguments.service_url
    destination_collection = arguments.destination_collection or arguments.collection
    destination_token = arguments.destination_token or curator_token

    output = None

    # If --list-labels and --list-records are provided, keep only the latter,
    # because it includes listing of labels
    if arguments.list_records:
        if arguments.list_labels:
            print('WARNING: `-l/--list-labels` and `-r/--list-records` defined, ignoring `-l/--list-labels`', file=sys.stderr, flush=True)
            arguments.list_labels = False
        output = {}
    if arguments.list_labels:
        output = []

    for label in incoming_read_labels(
                 service_url=arguments.service_url,
                 collection=arguments.collection,
                 token=curator_token):

        if label in arguments.exclude:
            logger.debug('ignoring excluded incoming label: %s', label)
            continue

        if arguments.list_labels:
            output.append(label)
            continue

        if arguments.list_records:
            output[label] = []

        for record, _, _, _, _ in incoming_read_records(
                                  service_url=arguments.service_url,
                                  collection=arguments.collection,
                                  label=label,
                                  token=curator_token):

            if arguments.pid:
                if record['pid'] not in arguments.pid:
                    logger.debug(
                        'ignoring record with non-matching pid: %s',
                        record['pid'])
                    continue

            if arguments.list_records:
                output[label].append(record)
                continue

            # Get the class name from the `schema_type` attribute. This requires
            # that the schema type is either stored in the record or that the
            # store has a "Schema Type Layer", i.e., the store type is
            # `record_dir+stl`, or `sqlite+stl`.
            try:
                class_name = re.search('([_A-Za-z0-9]*$)', record['schema_type']).group(0)
            except IndexError:
                global stl_info
                if not stl_info:
                    print(
                        f"""Could not find `schema_type` attribute in record with
                            pid {record['pid']}. Please ensure that `schema_type` is stored in
                            the records or that the associated incoming area store has a backend
                            with a "Schema Type Layer", i.e., "record_dir+stl" or
                            "sqlite+stl".""",
                        file=sys.stderr,
                        flush=True)
                    stl_info = True
                print(
                    f'WARNING: ignoring record with pid {record["pid"]}, `schema_type` attribute is missing.',
                    file=sys.stderr,
                    flush=True)
                continue

            # Store record in destination collection
            curated_write_record(
                service_url=destination_url,
                collection=destination_collection,
                class_name=class_name,
                record=record,
                token=destination_token)

            # Delete record from incoming area
            incoming_delete_record(
                service_url=arguments.service_url,
                collection=arguments.collection,
                label=label,
                pid=record['pid'],
                token=curator_token,
            )

    if output is not None:
        print(json.dumps(output, ensure_ascii=False))

    return 0


def main():
    try:
        return _main()
    except HTTPError as e:
        print(f'ERROR: {e}: {e.response.text}', file=sys.stderr, flush=True)
    return 1


if __name__ == '__main__':
    sys.exit(main())
