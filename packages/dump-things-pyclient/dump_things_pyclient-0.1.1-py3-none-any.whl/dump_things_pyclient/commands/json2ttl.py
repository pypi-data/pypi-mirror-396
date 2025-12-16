from __future__ import annotations

import argparse
import json
import re
import sys

from dump_things_service.converter import (
    Format,
    FormatConverter,
)


description = f"""Read JSON records from stdin and convert them to TTL

This command reads one record per line, either JSON format or a JSON-string
with a TTL-document from stdin, converts them to TTL or JSON and prints them
to stdout.

"""


def main():
    argument_parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    argument_parser.add_argument('schema', help='URL of the schema that should be used')

    arguments = argument_parser.parse_args()

    print(f'Creating converter for schema {arguments.schema} ...', file=sys.stderr, end='', flush=True)
    converter = FormatConverter(
        arguments.schema,
        input_format=Format.json,
        output_format=Format.ttl,
    )
    print(' done', file=sys.stderr, flush=True)

    error = False
    for line in sys.stdin:
        json_object = json.loads(line)

        object_class = json_object.get('schema_type')
        if object_class is None:
            error = True
            print(f'ERROR: No schema_type in {json_object}', file=sys.stderr, flush=True)
            continue

        class_name = re.search('([_A-Za-z0-9]*$)', object_class).group(0)

        try:
            ttl = converter.convert(json_object, class_name)
        except ValueError as ve:
            print(f'ERROR: conversion failed for {json_object}: {ve}', file=sys.stderr, flush=True)
            continue

        print(json.dumps(ttl))

    return 1 if error else 0


if __name__ == '__main__':
    sys.exit(main())
