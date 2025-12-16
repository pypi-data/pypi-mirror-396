from __future__ import annotations

import logging
import re
from itertools import count
from typing import (
    Callable,
    Generator,
)

import requests
from requests.exceptions import HTTPError

from . import JSON


__all__ = [
    'HTTPError',
    'JSON',
    'get_paginated',
    'get',
    'collection_delete_record',
    'collection_read_records',
    'collection_read_records_of_class',
    'collection_read_record_with_pid',
    'collection_validate_record',
    'collection_write_record',
    'curated_delete_record',
    'curated_read_records',
    'curated_read_records_of_class',
    'curated_read_record_with_pid',
    'curated_write_record',
    'incoming_delete_record',
    'incoming_read_labels',
    'incoming_read_records',
    'incoming_read_records_of_class',
    'incoming_read_record_with_pid',
    'incoming_write_record',
]


logger = logging.getLogger('dump_things_pyclient')


def get_paginated(url: str,
                  token: str | None = None,
                  first_page: int = 1,
                  page_size: int = 100,
                  last_page: int | None = None,
                  parameters: dict[str, str] | None = None,
                  ) -> Generator[tuple[JSON, int, int, int, int], None, None]:
    """Read all records from a paginated endpoint

    :param url: URL of the paginated endpoint, e.g., `https://.../records/p/`
    :param token: [optional] if str: token to authenticate against the endpoint,
           if None: no token will be sent to the endpoint
    :param first_page: [optional] first page to return (default: 1)
    :param page_size: [optional] size of pages (default: 100)
    :param last_page: [optional] last page to return (default: None (return all pages))
    :param parameters: [optional] parameters to pass to the endpoint, the
           parameter `page` is set automatically in this function

    :return: a Generator yielding tuples containing the current record, the
             current page number, the total number of pages, the size of the pages,
             and total number of records
    """
    if last_page and last_page < first_page:
        logger.warning('last_page (%d) < first_page (%d)', last_page, first_page)
        return

    for page in count(start=first_page):
        result = _get_page(url, token, first_page=page, page_size=page_size, parameters=parameters)
        total_pages, page_size, total_items = result['pages'], result['size'], result['total']
        if total_pages == 0:
            return
        if last_page is None:
            last_page = total_pages

        yield from (
            (record, page, total_pages, page_size, total_items)
            for record in result['items'])

        if page == min(last_page, total_pages):
            return


def get(url: str,
        token: str | None = None,
        parameters: dict[str, str] | None = None,
        ) -> JSON:
    """Read JSON object from a non-paginated endpoint

    :param url: URL of the endpoint, e.g., `https://.../records/`.
    :param token: [optional] if str: token to authenticate against the endpoint,
           if None: no token will be sent to the endpoint
    :param parameters: [optional] parameters to pass to the endpoint

    :return: JSON object
    """
    return _get_from_url(url, token, parameters)


def collection_get_classes(service_url: str,
                           collection: str,
                           ) -> Generator[str, None, None]:
    """Read classes that are supported by the collection

    Get the name of the classes that are known in the collection. If the
    collection does not exist on the server, no class names are returned.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection

    :return: a generator yielding names of the supported classes
    """
    service_url = f'{service_url[:-1]}' if service_url.endswith('/') else service_url
    matcher = re.compile(f'/{collection}/record/([A-Z][_a-zA-Z0-9]*)$')
    open_api_spec = _get_from_url(service_url + '/openapi.json', None)
    for path in open_api_spec['paths']:
        match = matcher.match(path)
        if match:
            yield match.group(1)


def collection_read_record_with_pid(service_url: str,
                                    collection: str,
                                    pid: str,
                                    format: str = 'json',
                                    token: str | None = None,
                                    ) -> dict | None:
    """Read record with the given pid from the collection on the service

    Records are read from the curated area of the collection and from the
    incoming area of the user identified by token, if a token is given.
    Records from incoming areas take preference.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param pid: the PID of the record that should be retrieved
    :param format: the format in which the result record should be returned,
           either `json` or `ttl`
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint

    :return: The record, if it exists, None otherwise.
    """
    return get(
            url=_build_url(service_url, collection, 'record'),
            token=token,
            parameters={'pid': pid, 'format': format})


def collection_read_records(service_url: str,
                            collection: str,
                            matching: str | None = None,
                            format: str = 'json',
                            token: str | None = None,
                            page: int = 1,
                            size: int = 100,
                            last_page: int | None = None,
                            ) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records from the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param format: the format in which the result records should be returned,
           either `json` or `ttl` (default: `json`)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint.
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_url(service_url, collection, 'records/p/'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters= {
            'format': format,
            **({'matching': matching} if matching else {})})


def collection_read_records_of_class(
        service_url: str,
        collection: str,
        class_name: str,
        matching: str | None = None,
        format: str = 'json',
        token: str | None = None,
        page: int = 1,
        size: int = 100,
        last_page: int | None = None,
) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records of the specified class from the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param class_name: the name of the class whose instances should be returned
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param format: the format in which the result records should be returned,
           either `json` or `ttl` (default: `json`)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint.
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_url(service_url, collection, f'records/p/{class_name}'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters= {
            'format': format,
            **({'matching': matching} if matching else {})})


def collection_write_record(
        service_url: str,
        collection: str,
        class_name: str,
        record: dict | str,
        format: str = 'json',
        token: str | None = None,
) -> list[JSON]:
    """Write a record of the specified class to an inbox in the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param class_name: the class of the record given in `record`
    :param record: dict | str: the record that should be written
    :param format: the format of `record`, either `json` or `ttl`
           (default: `json`)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           The token must have write access to incoming area in the collection

    :return list[JSON]: a list of records that was written. There might be more
            than one record due to inlined-relations extraction. The individual
            records might have annotations added
    """
    _check_format_value(format)
    return _post_to_url(
        url=_build_url(service_url, collection, f'record/{class_name}'),
        token=token,
        params={'format': format},
        **(dict(json=record) if format == 'json' else dict(data=record)))


def collection_validate_record(
        service_url: str,
        collection: str,
        class_name: str,
        record: dict | str,
        format: str = 'json',
        token: str | None = None,
) -> list[JSON]:
    """Validate a record of the specified class in the collection on the service

    Validation involves conversion of the record from json to ttl, or from
    ttl to json.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param class_name: the class of the record given in `record`
    :param record: dict | str: the record that should be validated
    :param format: the format of `record`, either `json` or `ttl`
           (default: `json`)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           The token must have write access to incoming area in the collection

    :return: True
    """
    _check_format_value(format)
    return _post_to_url(
        url=_build_url(service_url, collection, f'validate/{class_name}'),
        token=token,
        params={'format': format},
        **(dict(json=record) if format == 'json' else dict(data=record)))


def collection_delete_record(
        service_url: str,
        collection: str,
        pid: str,
        token: str | None = None,
) -> bool:
    """Delete the record with the given pid from the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param pid: the PID of the record that should be deleted
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint

    :return: True if the record was deleted, False otherwise
    """
    return _delete_url(
        url=_build_url(service_url, collection, 'record'),
        token=token,
        params={'pid': pid})


def curated_read_record_with_pid(service_url: str,
                                 collection: str,
                                 pid: str,
                                 token: str | None = None,
                                 ) -> dict | None:
    """Read record with the given pid from curated area of the collection on the service

    The record will be returned as it is stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param pid: the PID of the record that should be retrieved
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights

    :return: The record, if it exists, None otherwise
    """
    return get(
        url=_build_url(service_url, collection, 'curated/record'),
        token=token,
        parameters={'pid': pid})


def curated_read_records(service_url: str,
                         collection: str,
                         matching: str | None = None,
                         token: str | None = None,
                         page: int = 1,
                         size: int = 100,
                         last_page: int | None = None,
                         ) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records from the curated area the collection on the service

    Records will be returned as they are stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_url(service_url, collection, 'curated/records/p/'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters={'matching': matching} if matching else {})


def curated_read_records_of_class(
        service_url: str,
        collection: str,
        class_name: str,
        matching: str | None = None,
        token: str | None = None,
        page: int = 1,
        size: int = 100,
        last_page: int | None = None,
) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records of class `class_name` from the curated area the collection on the service

    Records will be returned as they are stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param class_name: the name of the class whose instances should be returned
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights for the collection
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_url(service_url, collection, f'curated/records/p/{class_name}'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters={'matching': matching} if matching else {})


def curated_write_record(
        service_url: str,
        collection: str,
        class_name: str,
        record: dict,
        token: str | None = None,
) -> list[JSON]:
    """Write a record of the specified class to the curated area of the collection on the service

    Records will be written without modification, i.e. there is no
    "Schema-Type-Layer", there is no extraction of inlined records, and there
    is no annotation-adding.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param class_name: the class of the record given in `record`
    :param record: dict: the record that should be written
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           A given token must have curator-rights for the collection

    :return list[JSON]: a list containing the record that was written
    """
    return _post_to_url(
        url=_build_url(service_url, collection, f'curated/record/{class_name}'),
        token=token,
        json=record)


def curated_delete_record(
        service_url: str,
        collection: str,
        pid: str,
        token: str | None = None,
) -> bool:
    """Delete the record with the given pid from the curated area of the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param pid: the PID of the record that should be deleted
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           A given token must have curator-rights for the collection
    :return: True if the record was deleted, False otherwise
    """
    return _delete_url(
        url=_build_url(service_url, collection, 'curated/record'),
        token=token,
        params={'pid': pid})


def incoming_read_labels(service_url: str,
                         collection: str,
                         token: str | None = None,
                         ) -> Generator[str, None, None]:
    """Read all incoming labels for the collection on the service.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           A given token must have curator-rights for the collection

    :return: list[str]: a list of incoming area labels
    """
    yield from _get_from_url(
        url=_build_url(service_url, collection,'incoming/'),
        token=token)


def incoming_read_record_with_pid(service_url: str,
                                  collection: str,
                                  label: str,
                                  pid: str,
                                  token: str | None = None,
                                  ) -> dict | None:
    """Read record with the given pid from the specified incoming area of the collection on the service

    The record will be returned as it is stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param label: the label of the incoming area in the collection
    :param pid: the PID of the record that should be retrieved
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights

    :return: The record, if it exists, None otherwise
    """
    return get(
        url=_build_incoming_url(service_url, collection, label, 'record'),
        token=token,
        parameters={'pid': pid})


def incoming_read_records(service_url: str,
                          collection: str,
                          label: str,
                          matching: str | None = None,
                          token: str | None = None,
                          page: int = 1,
                          size: int = 100,
                          last_page: int | None = None,
                          ) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records from the specified incoming area the collection on the service

    Records will be returned as they are stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param label: the label of the incoming area in the collection
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights for the collection
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_incoming_url(service_url, collection, label,'records/p/'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters={'matching': matching} if matching else {})


def incoming_read_records_of_class(
        service_url: str,
        collection: str,
        label: str,
        class_name: str,
        matching: str | None = None,
        token: str | None = None,
        page: int = 1,
        size: int = 100,
        last_page: int | None = None,
) -> Generator[tuple[dict, int, int, int, int], None, None]:
    """Read records of the specified class from the specified incoming area the collection on the service

    Records will be returned as they are stored in the backend. That means
    there is no "Schema-Type-Layer" involved.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param label: the label of the incoming area in the collection
    :param class_name: the name of the class whose instances should be returned
    :param matching: [optional] return only records that have a matching value
           (string comparison with `%` as wildcard)
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint. A
           token must have curator-rights for the collection
    :param page: int: the first page that should be returned (default: 1)
    :param size: int: the number of records in an individual pages (default: 100)
    :param last_page: int | None: if int, the last page that should be returned
           if None, all pages following `page` will be returned

    :return: A generator yielding tuples containing: the current record, the
             current page number, the total number of pages, the size of the
             pages, the total number of records
    """
    return get_paginated(
        url=_build_incoming_url(service_url, collection, label,f'records/p/{class_name}'),
        token=token,
        first_page=page,
        page_size=size,
        last_page=last_page,
        parameters={'matching': matching} if matching else {})


def incoming_write_record(
        service_url: str,
        collection: str,
        label: str,
        class_name: str,
        record: dict,
        token: str | None = None,
) -> list[JSON]:
    """Write a record of the specified class to the specified incoming area of the collection on the service

    Records will be written without modification, i.e. there is no
    "Schema-Type-Layer", there is no extraction of inlined records, and there
    is no annotation-adding.

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param label: the label of the incoming area in the collection
    :param class_name: the class of the record given in `record`
    :param record: dict: the record that should be written
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           A given token must have curator-rights for the collection

    :return list[JSON]: a list containing the record that was written
    """
    return _post_to_url(
        url=_build_incoming_url(service_url, collection, label, f'record/{class_name}'),
        token=token,
        json=record)


def incoming_delete_record(
        service_url: str,
        collection: str,
        label: str,
        pid: str,
        token: str | None = None,
) -> bool:
    """Delete the record with the given pid from the specified incoming area of the collection on the service

    :param service_url: the base URL of the service, i.e., the URL up to
           `/<collection>/...` or `/server`
    :param collection: the name of the collection
    :param label: the label of the incoming area in the collection
    :param pid: the PID of the record that should be deleted
    :param token: [optional] if set, a token to authenticate against
           the endpoint, if None: no token will be sent to the endpoint
           A given token must have curator-rights for the collection

    :return: True if the record was deleted, False otherwise
    """
    return _delete_url(
        url=_build_incoming_url(service_url, collection, label,'record'),
        token=token,
        params={'pid': pid})


def _get_from_url(url: str,
                  token: str | None,
                  params: dict[str, str] | None = None,
                  ) -> JSON:
    return _do_request(requests.get, url, token, params=params)


def _post_to_url(url: str,
                 token: str | None,
                 params: dict[str, str] | None = None,
                 **kwargs,
                 ) -> JSON:
    return _do_request(requests.post, url, token, params, **kwargs)


def _delete_url(url: str,
                token: str | None,
                params: dict[str, str] | None = None,
                ) -> JSON:
    return _do_request(requests.delete, url, token, params=params)


def _do_request(method: Callable,
                url: str,
                token: str | object | None,
                params: dict[str, str] | None,
                **kwargs,
                ) -> JSON:
    headers = {'x-dumpthings-token': token} if token is not None else {}
    response = method(url, headers=headers, params=params or {}, **kwargs)
    response.raise_for_status()
    if response.headers.get('content-type', '').strip().startswith('text/turtle'):
        return response.text
    return response.json()


def _build_url(
        service_url: str,
        collection: str,
        tail: str,
) -> str:
    service_url = f'{service_url[:-1]}' if service_url.endswith('/') else service_url
    collection = f'{collection[:-1]}' if collection.endswith('/') else collection
    return f'{service_url}/{collection}/{tail}'


def _build_incoming_url(
        service_url: str,
        collection: str,
        label: str,
        tail: str,
) -> str:
    label = f'{label[:-1]}' if label.endswith('/') else label
    return _build_url(service_url, collection, f'incoming/{label}/{tail}')


def _get_page(url_base: str,
              token: str | None = None,
              first_page: int = 1,
              page_size: int = 100,
              parameters: dict | None = None,
              ) -> JSON:
    parameters = parameters or {}
    parameters['page'] = first_page
    parameters['size'] = page_size
    return _get_from_url(url_base, token, parameters)


def _check_format_value(format: str) -> None:
    if format not in ('json', 'ttl'):
        raise ValueError('Format must be either "json" or "ttl"')
