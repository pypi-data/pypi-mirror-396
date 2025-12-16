def register_podman():
    # Import _podman has side-effect of registering podmand sandbox env
    from .podman import podman  # noqa: F401


__all__ = ["register_podman"]
