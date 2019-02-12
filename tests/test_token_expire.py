# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test token expire duration."""

import pytest
from flask import current_app

from flask_security.confirmable import generate_confirmation_token
from flask_security.utils import get_token_status


class User():
    def __init__(self, id, email):
        self.id = id
        self.email = email


@pytest.mark.settings(reset_password_within='1 milliseconds')
def test_reset_password_token(client, users):
    """."""
    current_app.config['SECURITY_RESET_PASSWORD_WITHIN'] = '1 milliseconds'
    user = User(id=users[0]['id'], email=users[0]['email'])
    token = generate_confirmation_token(user)
    expired, invalid, user = get_token_status(
        token, 'reset', 'RESET_PASSWORD'
    )
    import ipdb
    ipdb.set_trace()
