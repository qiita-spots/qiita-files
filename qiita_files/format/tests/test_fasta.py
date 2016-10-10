# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

from unittest import TestCase, main
from qiita_files.format.fasta import format_fasta_record


class FastaTests(TestCase):
    def test_format_fasta_record(self):
        exp = b">a\nxyz\n"
        obs = format_fasta_record(b"a", b"xyz", b'ignored')
        self.assertEqual(obs, exp)

if __name__ == '__main__':
    main()
