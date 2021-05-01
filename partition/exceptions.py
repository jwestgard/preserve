class ConfigError(Exception):
    """ Custom exception class raised by invalid args """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DuplicateFileError(Exception):
    """ Custom exception class raised when encountering repeated filenames """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)