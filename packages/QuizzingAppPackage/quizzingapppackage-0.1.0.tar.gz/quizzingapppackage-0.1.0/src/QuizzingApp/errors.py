# error defined by ourselves

class InvalidAgeError(Exception):
    pass

class InvalidEmailError(Exception):
    pass

class DataFileNotFoundError(Exception):
    pass

class InvalidNameError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class EmptyQuestionDataError(Exception):
    pass