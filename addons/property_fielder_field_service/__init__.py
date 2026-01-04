# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import wizard


def _post_init_hook(env):
    """Post-init hook to fix permissions for existing inspectors.

    When the module is installed or upgraded, this ensures all existing
    inspector profiles with linked users have the Field Service/User group.
    """
    env['property_fielder.inspector'].fix_existing_inspector_permissions()
