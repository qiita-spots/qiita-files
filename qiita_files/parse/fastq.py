# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np
from qiita_files.util import open_file
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


def _ascii_to_phred(s, offset):
    """Convert ascii to Phred quality score with specified ASCII offset."""
    return np.frombuffer(s, dtype='|S1').view(np.int8) - offset


def ascii_to_phred33(s):
    """Convert ascii string to Phred quality score with ASCII offset of 33.
    Standard "Sanger" ASCII offset of 33. This is used by Illumina in CASAVA
    versions after 1.8.0, and most other places. Note that internal Illumina
    files still use offset of 64
    """
    return _ascii_to_phred(s, 33)


def ascii_to_phred64(s):
    """Convert ascii string to Phred quality score with ASCII offset of 64.
    Illumina-specific ASCII offset of 64. This is used by Illumina in CASAVA
    versions prior to 1.8.0, and in Illumina internal formats (e.g.,
    export.txt files).
    """
    return _ascii_to_phred(s, 64)


def _drop_id_marker(s):
    """Drop the first character and decode bytes to text"""
    id_ = s[1:]
    try:
        return str(id_.decode('utf-8'))
    except AttributeError:
        return id_


def parse_fastq(data, strict=False, enforce_qual_range=True, phred_offset=33):
    r"""yields label, seq, and qual from a fastq file.

    Parameters
    ----------
    data : open file object or str
        An open fastq file (opened in binary mode) or a path to it.
    strict : bool, optional
        Defaults to ``False``. If strict is true a FastqParse error will be
        raised if the seq and qual labels dont' match.
    enforce_qual_range : bool, optional
        Defaults to ``True``. If ``True``, an exception will be raised if a
        quality score outside the range [0, 62] is detected
    phred_offset : {33, 64}, optional
        What Phred offset to use when converting qual score symbols to integers

    Returns
    -------
    label, seq, qual : (str, bytes, np.array)
        yields the label, sequence and quality for each entry
    """

    if phred_offset == 33:
        phred_f = ascii_to_phred33
    elif phred_offset == 64:
        phred_f = ascii_to_phred64
    else:
        raise ValueError("Unknown PHRED offset of %s" % phred_offset)

    with open_file(data, 'rb') as data:
        iters = [iter(data)] * 4
        for seqid, seq, qualid, qual in zip_longest(*iters):
            seqid = seqid.strip()
            # If the file simply ended in a blankline, do not error
            if seqid == b'':
                continue
            # Error if an incomplete record is found
            # Note: seqid cannot be None, because if all 4 values were None,
            # then the loop condition would be false, and we could not have
            # gotten to this point
            if seq is None or qualid is None or qual is None:
                raise ValueError("Incomplete FASTQ record found at end "
                                 "of file")

            seq = seq.strip()
            qualid = qualid.strip()
            qual = qual.strip()

            seqid = _drop_id_marker(seqid)

            try:
                seq = str(seq.decode("utf-8"))
            except AttributeError:
                pass

            qualid = _drop_id_marker(qualid)
            if strict:
                if seqid != qualid:
                    raise ValueError('ID mismatch: {} != {}'.format(
                        seqid, qualid))

            # bounds based on illumina limits, see:
            # http://nar.oxfordjournals.org/content/38/6/1767/T1.expansion.html
            qual = phred_f(qual)
            if enforce_qual_range and ((qual < 0).any() or (qual > 62).any()):
                raise ValueError("Failed qual conversion for seq id: %s. "
                                 "This may be because you passed an incorrect "
                                 "value for phred_offset." % seqid)

            yield (seqid, seq, qual)
