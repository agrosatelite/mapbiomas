__version__ = '0.0.1-beta_0'


def setup(set_prefix=True):
    """
    Configure the settings (this happens as a side effect of accessing the
    first setting), configure logging and populate the app registry.
    Set the thread-local urlresolvers script prefix if `set_prefix` is True.
    """
    from rsgee.apps import apps
    from rsgee.conf import settings

    apps.populate(settings.INSTALLED_APPS)
