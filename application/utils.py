"""Various helper utilities."""

from flask import request

def request_wants_json():
    """Returns true if application/json in accept."""
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']
