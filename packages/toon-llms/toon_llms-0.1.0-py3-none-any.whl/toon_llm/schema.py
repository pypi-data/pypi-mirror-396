class Schema:
    def __init__(self, fields: dict):
        self.fields = fields
        self.id_to_name = {v.id: k for k, v in fields.items()}
