#!/usr/bin/python

import datetime
import hashlib
import os
import tempfile
import unittest

import malpz

test_data = b'bob'
test_md5 = hashlib.md5(test_data).hexdigest()
test_sha1 = hashlib.sha1(test_data).hexdigest()
test_classification = 'UNCLASSIFIED'
test_unprintable = u'\xd3\xca\xbc\xfe\xb5\xc7\xbc\xc7\xb1\xed.xls'
test_unprintable_meta = dict(features=dict(filename=test_unprintable))

test_maldict = dict(
    data=test_data, md5sum=test_md5, classification=test_classification, meta=dict(features=dict(sha1=test_sha1))
)


class TestValidateVersion(unittest.TestCase):
    """malpz.validate_version"""

    def test_ok(self):
        """malpz.validate_version - test ok"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % malpz.VERSION
        data = header + b"_more_data_" * 8
        version = malpz.validate_version(data)
        self.assertTrue(version, malpz.VERSION)

    def test_current_ok(self):
        """malpz.validate_version - test current version ok"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % malpz.VERSION
        data = header + b"_more_data_" * 8
        version = malpz.validate_version(data)
        self.assertTrue(version, malpz.VERSION)

    def test_bad_magic(self):
        """malpz.validate_version - test bad magic"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % malpz.VERSION
        # corrupt the magic
        header = header.replace(b'm', b'M')
        data = header + b"_more_data_" * 8

        self.assertRaises(malpz.MetadataException, malpz.validate_version, data)

    def test_not_ok(self):
        """malpz.validate_version - test not supported"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % b"ZXCV"
        data = header + b"_more_data_" * 8
        self.assertRaises(malpz.MetadataException, malpz.validate_version, data)

    def test_too_short(self):
        """malpz.validate_version - test too short data"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % b"ZXCV"
        # make it shorter
        header = header[:-1]
        data = header
        self.assertRaises(malpz.MetadataException, malpz.validate_version, data)

    def test_bad_version(self):
        """malpz.validate_version - test bad version"""

        header = b"\xf0\xf0.malpz_v%s\x00\x0f\x0f" % b"9999"
        self.assertRaises(malpz.MetadataException, malpz.validate_version, header)


class TestWrap(unittest.TestCase):
    """malpz.wrap - test can wrap"""

    def test_ok(self):
        """malpz.wrap - test can wrap then unwrap"""

        wrapped = malpz.wrap(test_data, test_classification, meta=dict(features=dict(sha1=test_sha1)))
        unwrapped = malpz.unwrap(wrapped)

        self.assertEqual(unwrapped['version'], malpz.VERSION)
        self.assertEqual(unwrapped['data'], test_data)
        self.assertEqual(unwrapped['classification'], test_classification)
        self.assertEqual(unwrapped['meta']['features']['sha1'], test_sha1)

    def test_unprintable_chars(self):
        """malpz.wrap - test wrap & unwrap with non-printable char, opt meta"""

        wrapped = malpz.wrap(test_data, test_classification, meta=test_unprintable_meta)
        unwrapped = malpz.unwrap(wrapped)

        self.assertEqual(unwrapped['version'], malpz.VERSION)
        self.assertEqual(unwrapped['data'], test_data)
        self.assertEqual(unwrapped['classification'], test_classification)
        self.assertEqual(unwrapped['meta']['features']['filename'], test_unprintable)


class TestWrapToFile(unittest.TestCase):
    """malpz.wrap - test can wrap to file"""

    def setUp(self):
        filehandle, self.temp_filename = tempfile.mkstemp()

    def tearDown(self):
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def test_ok(self):
        """malpz.wrap - test can wrap to file then unwrap"""

        malpz.wrap_to_file(
            self.temp_filename, test_data, test_classification, meta=dict(features=dict(sha1=test_sha1))
        )

        self.assertTrue(os.path.exists(self.temp_filename))
        filesize = os.path.getsize(self.temp_filename)
        msg = 'file size is %d for %s, must be at least %d' % (filesize, self.temp_filename, len(malpz.MALPZ_HEADER))
        self.assertTrue(filesize > len(malpz.MALPZ_HEADER), msg)

        self.assertTrue(malpz.supported_file(self.temp_filename))

        unwrapped = malpz.unwrap_from_file(self.temp_filename)

        self.assertEqual(unwrapped['version'], malpz.VERSION)
        self.assertEqual(unwrapped['data'], test_data)
        self.assertEqual(unwrapped['classification'], test_classification)


class TestMain(unittest.TestCase):
    """Code coverage for main."""

    def setUp(self):
        _, self.temp_filename = tempfile.mkstemp()
        with open(self.temp_filename, "w") as f:
            f.write("testdata")

    def tearDown(self):
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def test_help(self):
        self.assertEqual(malpz.main(["--help"]), 0)

    def test_wrap_and_unwrap(self):
        res = malpz.main(["--classif=UNCLASSIFIED", self.temp_filename])
        self.assertEqual(res, 0)

        # Assert the new exists, do list.
        outfile_path = self.temp_filename + ".malpz"
        self.assertTrue(os.path.exists(outfile_path))
        res = malpz.main(["-l", outfile_path])
        self.assertEqual(res, 0)

        # Remove the original.
        os.remove(self.temp_filename)
        self.assertFalse(os.path.exists(self.temp_filename))

        # Convert back and ensure original file is back.
        res = malpz.main([outfile_path])
        self.assertEqual(res, 0)
        self.assertTrue(os.path.exists(self.temp_filename))
        self.assertTrue(os.path.exists(outfile_path))
        os.remove(outfile_path)
        self.assertFalse(os.path.exists(outfile_path))


if "__main__" == __name__:
    unittest.main()
