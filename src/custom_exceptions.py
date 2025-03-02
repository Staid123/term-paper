class TestException(Exception):
    """Base exception for Test related errors."""
    
    def __init__(self, action: str, message: str):
        self.message = message
        super().__init__(f"Failed to {action} test: {self.message}")

class TestCreateException(TestException):
    """Error creating test."""
    
    def __init__(self, message: str):
        super().__init__("create", message)

class TestDeleteException(TestException):
    """Error deleting test."""
    
    def __init__(self, message: str):
        super().__init__("delete", message)


class TestGetException(TestException):
    """Error deleting test."""
    
    def __init__(self, message: str):
        super().__init__("get", message)

class TestUpdateException(TestException):
    """Error deleting test."""
    
    def __init__(self, message: str):
        super().__init__("update", message)


class QuestionException(Exception):
    """Base exception for Question related errors."""
    
    def __init__(self, action: str, message: str):
        self.message = message
        super().__init__(f"Failed to {action} test: {self.message}")

class QuestionCreateException(TestException):
    """Error creating question."""
    
    def __init__(self, message: str):
        super().__init__("create", message)

class QuestionDeleteException(TestException):
    """Error deleting question."""
    
    def __init__(self, message: str):
        super().__init__("delete", message)
        
class QuestionUpdateException(TestException):
    """Error deleting question."""
    
    def __init__(self, message: str):
        super().__init__("update", message)
        