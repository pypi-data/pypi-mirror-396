#  SPDX-FileCopyrightText: © 2024 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Low-level utils for filesystem implementations.
"""
import base64
import json
import urllib.parse

import parzzley.fs


async def site_for_key(site: "parzzley.fs.Site", key: str) -> "parzzley.fs.Site":
    """
    Return an inner site for an existing one by a key. The key is used for generating a subdirectory name on the given
    site.

    :param site: The original site.
    :param key: The key.
    """
    control_item = parzzley.fs.item(urllib.parse.quote_plus(key).encode())
    try:
        await site.create_item(control_item, parzzley.fs.ItemType.DIRECTORY)
    except parzzley.fs.Site.ItemExistsError:
        pass

    return site.sub_site(control_item)


def serialize_bytes_dict(xattrs: dict[bytes, bytes]) -> bytes:
    """
    Convert a dictionary with extended attributes to serialized binary content (as used for
    :py:func:`deserialize_bytes_dict`).

    :param xattrs: Dictionary with extended attributes.
    """
    return json.dumps(
        {base64.b64encode(key).decode(): base64.b64encode(value).decode() for key, value in sorted(xattrs.items())}
    ).encode()


def deserialize_bytes_dict(xattrs_bin: bytes) -> dict[bytes, bytes]:
    """
    Convert a serialized binary content (as returned by :py:func:`serialize_bytes_dict`) to a dictionary with extended
    attributes.

    :param xattrs_bin: Serialized binary content.
    """
    if not xattrs_bin:
        return {}
    return {base64.b64decode(key): base64.b64decode(value) for key, value in json.loads(xattrs_bin.decode()).items()}
