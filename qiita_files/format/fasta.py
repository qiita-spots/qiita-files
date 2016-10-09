# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------


def format_fasta_record(seqid, seq, qual):
    """Format a fasta record

    Parameters
    ----------
    seqid : str
        The sequence ID
    seq : str
        The sequence
    qual : ignored
        This is ignored

    Returns
    -------
    str
        A formatted sequence record
    """
    return b'\n'.join([b'>' + seqid, seq, b''])
