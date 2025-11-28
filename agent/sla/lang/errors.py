class ErrorMessage:
    def __init__(self, given: str):
        self._given = given

    def __str__(self):
        return f"Error at: {self._given}"

class NotInEnum(ErrorMessage):
    def __init__(self, given: str, category: str):
        super().__init__(given)
        self._category = category

    def __str__(self):
        return f"{self._given} is not a valid type of {self._category}"

class UndefinedLabel(ErrorMessage):
    def __init__(self, given: str, category: str):
        super().__init__(given)
        self._category = category

    def __str__(self):
        return f"{self._given} is undefined. No {self._category} with this name exist"

class OutOfBound(ErrorMessage):
    def __init__(self, given: str):
        super().__init__(given)

    def __str__(self):
        return f"{self._given} is not a valid ratio. It should be in the interval [0,1]"

class NoUnit(ErrorMessage):
    def __init__(self, given: str):
        super().__init__(given)

    def __str__(self):
        return f"No unit defined for {self._given}"
