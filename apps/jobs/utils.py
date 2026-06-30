"""
Shared helpers for the jobs app.
"""
import re


def normalize_title(title):
    """
    Normalize a job title for de-duplication.

    Lowercases, strips HTML, removes punctuation (so "A - B" and "A – B"
    collapse to the same key), and squeezes whitespace. Deliberately
    conservative: it merges punctuation/case variants of the SAME role but
    keeps genuinely different listings (different cities, clearance levels,
    etc.) distinct.
    """
    t = (title or '').lower()
    t = re.sub(r'<[^>]+>', ' ', t)        # drop any stray HTML
    t = re.sub(r'[^a-z0-9]+', ' ', t)     # punctuation -> space
    t = re.sub(r'\s+', ' ', t).strip()
    return t
