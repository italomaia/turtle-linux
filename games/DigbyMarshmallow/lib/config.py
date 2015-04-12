"""Configuration parameters stored in a module namespace.

Parameters come in two types, those that are stored in the config file and those
that aren't. Running the profiler is an example of the former; fullscreen mode
would be an example of the latter.

Just because an option is stored in the config file doesn't mean it can't also
be changed by, for example, a command line switch. But doing so should not
alter the config file's value.

The `save_option` method is used to alter a value here and in the config file.
It can only be called for a predefined list of options. The `save_all` method
should probably not be used. It will write all current values for config file
parameters to the config file.

"""

# IMPORTANT!
# Never do "from config import *". This module relies on manipulation of its
# own namespace to work properly.
__all__ = []


class LocalConfig(object):
    """Manager for the local config file.

    """

    def __init__(self, **defaults):
        self.defaults = defaults
        self.locals = dict(defaults)
        self.config_file = "local.py"
        self.load()

    def load(self):
        """Read the config file.

        """
        open(self.config_file, "a").close()
        exec open(self.config_file) in self.locals
        for name, value in self.locals.iteritems():
            globals()[name] = value

    def save(self):
        """Write the config file.

        """
        config_fd = open(self.config_file, "w")
        for key in self.defaults:
            value = self.locals[key]
            if value != self.defaults[key]:
                line = "%s = %r\n" % (key, value)
                config_fd.write(line)
        config_fd.close()

    def save_option(self, name, value=None):
        """Change an option in the config file.

        :Parameters:
            `name` : str
                The name of the option to save.
            `value` : any
                Default None. If not None, the value to set, otherwise uses the
                current value.

        """
        assert name in self.defaults, "%r is not a local option" % name
        if value is None:
            value = globals()[name]
        globals()[name] = self.locals[name] = value
        self.save()

    def save_all(self):
        """Save all current values to the config file.

        """
        for name in self.defaults:
            self.save_option(name)


# Default values for options not in the config file
profile = False
start_mode = "menu"
start_level = None

# Default values for options in the config file
local = LocalConfig(
    fullscreen = True,
)

# See the module docstring for details
save_option = local.save_option
save_all = local.save_all

# Clean up the module namespace
del local, LocalConfig
