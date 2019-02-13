# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test token expire duration."""

# import pytest

from flask_security import url_for_security
from flask_security.recoverable import generate_reset_password_token


# @pytest.mark.parametrize("duration,expected", [(2, True), (5, False)])
def test_forgot_password_token(app, users):
    """."""
    ds = app.extensions['invenio-accounts'].datastore
    with app.app_context():
        user = ds.create_user(
            email='info@inveniosoftware.org', password='1234', active=True
        )
        token = generate_reset_password_token(user)
        reset_link = url_for_security('reset_password', token=token)

    with app.test_client() as client:
        # 1) test case: wait x secs
        # 2) test caseL no wait
        res = client.get(reset_link)
        # tres.get_text()
        # resp = client.get(forgot_password_url, follow_redirects=True)
    import ipdb
    ipdb.set_trace()
