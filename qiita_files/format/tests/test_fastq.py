# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import TestCase, main
import numpy as np

from qiita_files.format.fastq import (format_fastq_record, _phred_to_ascii33,
                                      _phred_to_ascii64)


class FastqTests(TestCase):
    def setUp(self):
        self.qual_scores = np.array([38, 39, 40], dtype=np.int8)
        self.args = (b'abc', b'def', self.qual_scores)

    def test_format_fastq_record_phred_offset_33(self):
        exp = b"@abc\ndef\n+\nGHI\n"
        obs = format_fastq_record(*self.args, phred_offset=33)
        self.assertEqual(obs, exp)

    def test_format_fastq_record_phred_offset_64(self):
        exp = b"@abc\ndef\n+\nfgh\n"
        obs = format_fastq_record(*self.args, phred_offset=64)
        self.assertEqual(obs, exp)

    def test_format_fastq_record_invalid_phred_offset(self):
        with self.assertRaises(ValueError):
            format_fastq_record(*self.args, phred_offset=42)

    def test_phred_to_ascii33(self):
        obs = _phred_to_ascii33(self.qual_scores)
        self.assertEqual(obs, b'GHI')

    def test_phred_to_ascii64(self):
        obs = _phred_to_ascii64(self.qual_scores)
        self.assertEqual(obs, b'fgh')


if __name__ == '__main__':
    main()
