"""Utility functions for working with volumes."""


def validate_volume_mount(volume_mount: dict[str,]):
    """Validate a volume mount object.

    :param volume_mount: The volume mount object to validate
    :type volume_mount: dict[str,]
    """
    assert "volume_id" in volume_mount, "Volume ID is required"
    assert "mount_path" in volume_mount, "Mount path is required"
    assert "read_only" in volume_mount, "Read-only flag is required"
    assert isinstance(
        volume_mount["volume_id"], int
    ), "Volume ID must be an integer"
    assert isinstance(
        volume_mount["mount_path"], str
    ), "Mount path must be a string"
    assert isinstance(
        volume_mount["read_only"], bool
    ), "Read-only flag must be a boolean"
