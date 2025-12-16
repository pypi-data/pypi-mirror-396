class PDFError(Exception):
    """Base exception for all PDF errors."""
    pass

class MalformedMagicHeader(PDFError):
    def __init__(self, result, expected):
        self.result = result 
        self.expected = expected
        super().__init__(f"Malformed Magic Header: \n\nFound:\n{self.result}\n\nExpected:\n{self.expected}")

class MalformedFileHead(PDFError):
    def __init__(self, result, expected):
        self.result = result 
        self.expected = expected
        super().__init__(f"Malformed File Head: \n\nFound:\n{self.result}\n\nExpected:\n{self.expected}")

class SyntaxErrorInPDFStructure(PDFError):
    def __init__(self, result):
        self.result = result 
        super().__init__(f"Syntax Error in PDF Structure: \n\n{self.result}")

class ErrorInPDFStructure(PDFError):
    def __init__(self, result):
        self.result = result 
        super().__init__(f"Error in PDF Structure: \n\n{self.result}")

class InvalidDataTypeHTML(PDFError):
    def __init__(self, result):
        self.result = result 
        super().__init__(f"PDF file is actually of type HTML, maybe due to download error?: \n\n{self.result}")

class InvalidMimeType(PDFError):
    def __init__(self, result, expected):
        self.result = result 
        self.expected = expected
        super().__init__(f"PDF file is actually incorrect MIMETYPE: \n\nFound:\n{self.result}\n\nExpected:\n{self.expected}")
