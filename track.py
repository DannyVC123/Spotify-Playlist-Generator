class Track:
    def __init__(self, id, name, artists):
        self.id = id
        self.name = name
        self.artists = artists
    
    def get_uri(self):
        return f'spotify:track:{self.id}'
    
    def __str__(self):
        str = f'{self.name}'
        for artist in self.artists:
            str = f'{str}\n  {artist}'
        return str