import logging
from abstract_flask import get_Flask_app
from .app import bp_list

def login_app(
    allowed_origins=None,
    name=None
    ):
    ALLOWED_ORIGINS = allowed_origins or ["*"]
    name= name or "abstract_logins"
    return get_Flask_app(
        name=name,
        bp_list=bp_list,
        allowed_origins=allowed_origins
        )
