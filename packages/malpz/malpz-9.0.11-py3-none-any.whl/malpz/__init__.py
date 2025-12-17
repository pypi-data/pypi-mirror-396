"""The Malpz (Malware Pickled Zip) format describes a method of neutering malware.

The format provides a simple, extensible mechanism for capturing metadata
alongside the neutered sample data.

This module provides a Python implementation of the format and does not
include pickling since version 0003.

Version Description:
    0001 - removed prescribed 'optional' fields from maldict
    0002 - deprecated due to perceived security risk
    0003 - current version.

Note: Malpz is not backwards compatible.
"""

from __future__ import print_function, unicode_literals, with_statement

import binascii
import getopt
import hashlib
import json
import os.path
import re
import sys
import zlib

# Redefine Py2's input statement to behave like in Py3 (aka Py2 raw_input)
# This means we can just use `input(...)` and be compatible with both
if sys.version_info[0] == 2:
    input = raw_input  # noqa: F821


# VERSION must be four characters long as per the spec!
VERSION = b"0003"

MALPZ_HEADER = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % VERSION
MALPZ_MAGIC = re.compile(b"\xf0\xf0.malpz_v[\\d]{4}\x00\x0f\x0f")
VERSION_SEARCH = re.compile(b".malpz_v(?P<version>\\d+)")


class MetadataException(Exception):
    """Exception class for errors in malpz metadata."""

    def __init__(self, msg):
        """Create a new exception containing msg."""
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        """Return string representation escaping any non-ascii."""
        return repr(self.msg)


def wrap(data, classification, meta=None):
    """Turn passed parameters into JSON object, zip it then return buffer."""
    # Create the output dict.
    maldict = dict(
        data=binascii.hexlify(data).decode('ascii'),  # hexlify produces bytes as output
        md5sum=hashlib.md5(data).hexdigest(),  # noqa: S303 # nosec
        classification=classification,
    )
    if meta is not None:
        maldict["meta"] = meta

    # Compress our resultant JSON.
    # (Note that we rely on the default param ensure_ascii=True to guarantee an ascii-encodable output.)
    buf = zlib.compress(json.dumps(maldict).encode('ascii'))
    return b'%s%s' % (MALPZ_HEADER, buf)


def validate_version(buf):
    """Return the version if version is valid, else raise a MetadataException."""
    header = buf[0 : len(MALPZ_HEADER)]

    if MALPZ_MAGIC.search(header) is None:
        raise MetadataException("Incorrect malpz magic")

    version = VERSION_SEARCH.search(header).groupdict()['version']

    if version != VERSION:
        msg = "version '%s' not supported - currently supporting %s" % (version, VERSION)
        raise MetadataException(msg)
    return version


def unwrap(buf):
    """Unpacks a malpz formatted buffer.

    All values in the returned dict are unicode strings, except for `data` which is a bytes string.
    """
    version = validate_version(buf)
    buf = buf[len(MALPZ_HEADER) :]

    # extract the dictionary
    maldict = json.loads(zlib.decompress(buf).decode('ascii'))
    maldict["data"] = binascii.unhexlify(maldict["data"])
    maldict['version'] = version

    # return the resultant dictionary
    return maldict


def wrap_to_file(filepath, data, classification, **kwargs):
    """Wrap some data than store it to the specified filepath.

    kwargs:
        filepath - out filepath
        data - data to wrap
        classification - classification of this data
        **optional metadata keyword arguments
    """
    with open(filepath, 'wb') as handle:
        handle.write(wrap(data, classification, **kwargs))


def unwrap_from_file(filepath):
    """Unwrap data from a file and return an unwrapped malpz dictionary."""
    with open(filepath, "rb") as handle:
        maldict = unwrap(handle.read())
    return maldict


def supported_file(filepath):
    """Check if the filepath is supported."""
    with open(filepath, 'rb') as handle:
        header = handle.read(len(MALPZ_HEADER))

    try:
        validate_version(header)
    except MetadataException:
        return False
    else:
        return True


#
# Above these hashes is the "library" component of this module.
###############################################################################
# Below these hashes is the "script" component of this module.
#


__help__ = """NAME
    malpz

SYNOPSIS
    malpz.py [OPTIONS] file

DESCRIPTION
    If the specified file is in Malpz format, this script will un-Malpz it.

    If the specified file is not in Malpz format, this script will convert it
    into a Malpz format. In the current implementation, if no classification
    is specified on the command line the script will prompt the user for a
    classification.

    Arguments:

        -h, --help
            Display this help.

        -c, --classif="classification"
            If specified for wrapping operations, the specified value will be
            used as the classification. This field is ignored for unwrap
            operations.

        -l, --list
            Print file info for viewing. This field is ignored for
            wrapping operations.

        --include_filename
            (malpz only) Set the filename feature in the malpz meta field.

        --use_filename
            (unmalpz only) When unmalpzing write the output file to the
            filename in the metafield that was set by ``--use_filename``.

LIBRARY
    This Python module, when imported, can be used as a library for all your
    Malpz file format needs. You're probably most interested in the wrap(),
    wrap_to_file(), unwrap(), and unwrap_from_file() functions.

EXTENSION
    The Malpz format is extensible and provides more functionality than is made
    available through this command line interface. If you are interested in
    extending the command line interface to expose more features of Malpz and/or
    are interested in extending the file format itself, please raise a github issue or pull request.
"""


def main(argv):
    """Run malpz as a command-line util."""
    # Parse the command line args.
    try:
        opts, args = getopt.getopt(argv, "hc:l", ["help", "classif=", 'list', 'include_filename', 'use_filename'])
    except Exception as exc:
        print("Args error %s\n" % exc, file=sys.stderr)
        print(__help__, file=sys.stderr)
        return 1

    # Print help if needed.
    params = dict([(k.strip('-'), a) for k, a in opts])
    if 'h' in params or 'help' in params:
        print(__help__)
        return 0

    # sanity check path
    if len(args) == 1:
        if not os.path.exists(args[0]):
            print("Path must exist. Try --help for help.", file=sys.stderr)
            return 1
    else:
        print("No path specified. Try --help for help.", file=sys.stderr)
        return 1

    # Path checks out OK - figure out if we're meant to wrap or not.
    in_path = args[0]
    if supported_file(in_path):
        # It's already malpz - unwrap it.
        # Read out the dictionary.
        maldict = unwrap_from_file(in_path)

        # Print info if asked.
        if 'l' in params or 'list' in params:
            # Try to get filename from meta.
            fname = maldict.get('meta', {}).get('features', {}).get('filename', [])
            if fname:
                print('Filename:\t%s' % os.path.basename(fname[0]))

            print('MD5:\t\t%s' % maldict['md5sum'])
            print('Classification:\t%s' % maldict['classification'])
            print('Malpz Version:\t%s' % maldict['version'])

            if 'meta' in maldict:
                print('Meta:\t\tpresent')
            else:
                print('Meta:\t\tabsent')
            return 0

        # Didn't want info, so lets extract it.
        # Figure out what to call the unwrapped file.
        if in_path.lower().endswith(".malpz"):
            out_path = in_path[: 0 - len(".malpz")]
        else:
            out_path = None
            if 'use_filename' in params:
                out_path = maldict.get('meta', {}).get('features', {}).get('filename', [None])[0]
            if out_path is None:
                out_path = in_path + ".unmalpzed"

        if os.path.exists(out_path):
            print("Error: out file already exists (%s)" % out_path, file=sys.stderr)
            return 1
        with open(out_path, "wb") as out_file:
            out_file.write(maldict["data"])
        print("File un-malpzed to %s" % out_path)

    else:
        # It's not malpz - wrap it.
        # Get a classification.
        if "c" in params:
            classif = params["c"]
        elif "classif" in params:
            classif = params["classif"]
        else:
            classif = input("What is the classification (def: UNCLASSIFIED)? ")
            if len(classif) == 0:
                classif = "UNCLASSIFIED"

        # Wrap the file.
        out_path = in_path + ".malpz"
        if os.path.exists(out_path):
            print("Error: out file already exists (%s)" % out_path, file=sys.stderr)
            return 1
        in_path_basename = os.path.basename(in_path)
        meta = None
        if "include_filename" in params:
            meta = {'features': {'filename': [in_path_basename]}}
        with open(in_path, "rb") as in_file:
            wrap_to_file(out_path, in_file.read(), classif, meta=meta)
        print("File malpzed to %s" % out_path)

    return 0


def _entry():
    # Wraps main so that it can be directly passed the argv params -- simplifies testing
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(_entry())
