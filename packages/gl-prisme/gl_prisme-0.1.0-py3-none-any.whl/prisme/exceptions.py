class PrismeException(Exception):
    def __init__(self, code, text, context):
        super().__init__()
        self.code = int(code)
        self.text = text
        self.context = context

    def __str__(self):
        return f"Error in response from Prisme. Code: {self.code}, Text: {self.text}"
