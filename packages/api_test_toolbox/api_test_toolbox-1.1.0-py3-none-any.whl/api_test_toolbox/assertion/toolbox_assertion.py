class WrongStatusAssertionError(AssertionError):
    def __init__(self, description: str):
        self.description = description
        super().__init__(description)


class WrongResultLengthAssertionError(AssertionError):
    def __init__(self, description: str):
        self.description = description
        super().__init__(description)

class WrongObjectEnumValueAssertionError(AssertionError):
    def __init__(self, description: str):
        self.description = description
        super().__init__(description)
