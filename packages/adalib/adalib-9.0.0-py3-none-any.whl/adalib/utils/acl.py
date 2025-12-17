"""Utilities for ACL validation and handling."""

from typing import Literal


def validate_acl(
    obj: Literal["app", "card", "schedule", "volume"],
    allow_none: bool = False,
    *acls: list[str],
):
    """Validate ACL objects, based on the given object type.

    :param obj: The object type to validate the ACLs for
    :type obj: Literal["app", "card", "schedule"]
    :param allow_none: Allow None as a valid ACL, defaults to False
    :type allow_none: bool
    :raises AssertionError: If the ACLs are invalid
    """
    allowed_acls = {
        "app": ["public", "logged_in", "userlist", "grouplist"],
        "card": ["public", "logged_in", "userlist", "grouplist"],
        "schedule": ["public", "logged_in", "userlist", "grouplist"],
        "volume": ["public", "logged_in", "userlist", "grouplist"],
    }

    assert obj in allowed_acls, f"Object does not support ACL: {obj}"
    for _acl in acls:
        if allow_none and _acl is None:
            continue

        assert (
            _acl.lower() in allowed_acls[obj]
        ), f"Invalid ACL value for {obj}: '{_acl}'. Allowed values: {allowed_acls[obj]}"
