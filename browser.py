from enum import Enum


class ExtendedEnum(Enum):
    def __str__(self):
        """
        Override string representation of the object
        => cancels the need to use "value" attribute when comparing with string.
        This method is called when print or str function is invoked on an object.
        """
        return str(self.value)

    def __repr__(self):
        """
        Returns the object representation in string format.
        This method is called when repr() function is invoked on the object.
        """
        if isinstance(self.value, str):
            return self.value

        return "<%s.%s: %r>" % (self.__class__.__name__, self._name_, self._value_)


class Browsers(str, ExtendedEnum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"


class Browser:
    def __init__(self, browser):
        self.capabilities = {}
        self.screen_width = 1800
        self.screen_height = 900

        if browser == "chrome":
            self.set_chrome()

    def set_chrome(self):
        #  Set CH capabilities
        self.capabilities["browserName"] = Browsers.CHROME