# -----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# -----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function

import numpy as np

from qiita_files.util import open_file


def is_empty(line):
    """Returns True empty lines and lines consisting only of whitespace."""
    return (not line) or line.isspace()


def LabeledRecordFinder(is_label_line, constructor=str.strip, ignore=is_empty):
    """Returns function that returns successive labeled records from file.
    Includes label line in return value. Returns list of relevant lines.
    Default constructor is string.strip, but can supply another constructor
    to transform lines and/or coerce into correct type. If constructor is None,
    passes along the lines without alteration.
    Skips over any lines for which ignore(line) evaluates True (default is
    to skip empty lines).
    NOTE: Does _not_ raise an exception if the last line is a label line: for
    some formats, this is acceptable. It is the responsibility of whatever is
    parsing the sets of lines returned into records to complain if a record
    is incomplete.
    """
    def parser(lines):
        with open_file(lines) as lines:
            curr = []
            for l in lines:
                try:
                    l = str(l.decode('utf-8'))
                except AttributeError:
                    pass

                if constructor is not None:
                    line = constructor(l)
                else:
                    line = l
                if ignore(line):
                    continue
                # if we find the label, return the previous record
                if is_label_line(line):
                    if curr:
                        yield curr
                        curr = []
                curr.append(line)
            # don't forget to return the last record in the file
            if curr:
                yield curr
    return parser


def is_fasta_label(x):
    """Checks if x looks like a FASTA label line."""
    return x.startswith('>')


def is_blank_or_comment(x):
    """Checks if x is blank or a FASTA comment line."""
    return (not x) or x.startswith('#') or x.isspace()


FastaFinder = LabeledRecordFinder(is_fasta_label, ignore=is_blank_or_comment)


def parse_fasta(infile, strict=True, label_to_name=None, finder=FastaFinder,
                label_characters='>', ignore_comment=False):
    r"""Generator of labels and sequences from a fasta file.

    Parameters
    ----------
    infile : open file object or str
        An open fasta file or a path to a fasta file.
    strict : bool
        If ``True`` a ``ValueError`` will be raised if there is a fasta label
        line with no associated sequence, or a sequence with no associated
        label line (in other words, if there is a partial record). If
        ``False``, partial records will be skipped.
    label_to_name : function
        A function to apply to the sequence label (i.e., text on the header
        line) before yielding it. By default, the sequence label is returned
        with no processing. This function must take a single string as input
        and return a single string as output.
    finder : function
        The function to apply to find records in the fasta file. In general
        you should not have to change this.
    label_characters : str
        String used to indicate the beginning of a new record. In general you
        should not have to change this.
    ignore_comment : bool
        If `True`, split the sequence label on spaces, and return the label
        only as the first space separated field (i.e., the sequence
        identifier). Note: if both ``ignore_comment`` and ``label_to_name`` are
        passed, ``ignore_comment`` is ignored (both operate on the label, so
        there is potential for things to get messy otherwise).

    Returns
    -------
    two-item tuple of str
        yields the label and sequence for each entry.

    Raises
    ------
    ValueError
        If ``strict == True``, raises a ``ValueError`` if there is a fasta
        label line with no associated sequence, or a sequence with no
        associated label line (in other words, if there is a partial record).
    """
    for rec in finder(infile):
        # first line must be a label line
        if not rec[0][0] in label_characters:
            if strict:
                raise ValueError(
                    "Found Fasta record without label line: %s" % rec)
            else:
                continue
        # record must have at least one sequence
        if len(rec) < 2:
            if strict:
                raise ValueError(
                    "Found label line without sequences: %s" % rec)
            else:
                continue

        # remove the label character from the beginning of the label
        label = rec[0][1:].strip()
        # if the user passed a label_to_name function, apply that to the label
        if label_to_name is not None:
            label = label_to_name(label)
        # otherwise, if the user passed ignore_comment, split the label on
        # spaces, and return the first space separated field (i.e., the
        # sequence identifier)
        elif ignore_comment:
            label = label.split()[0]
        else:
            pass

        # join the sequence lines into a single string
        seq = ''.join(rec[1:])

        yield label, seq


def parse_qual(infile, full_header=False):
    r"""yields label and qual from a qual file.

    Parameters
    ----------
    infile : open file object or str
        An open fasta file or path to it.
    full_header : bool
        Return the full header or just the id

    Returns
    -------
    label : str
        The quality label
    qual : array
        The quality at each position
    """

    for rec in FastaFinder(infile):
        curr_id = rec[0][1:]
        curr_qual = ' '.join(rec[1:])
        try:
            parts = np.asarray(curr_qual.split(), dtype=int)
        except ValueError:
            raise ValueError(
                "Invalid qual file. Check the format of the qual file: each "
                "quality score must be convertible to an integer.")
        if full_header:
            curr_pid = curr_id
        else:
            curr_pid = curr_id.split()[0]
        yield (curr_pid, parts)
