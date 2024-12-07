class Artist:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
    
    def __str__(self):
        return self.name