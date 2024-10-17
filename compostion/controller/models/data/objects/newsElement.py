import uuid

class NewsElement():

    def __init__(self,url:str,headLine:str):
        self.id = uuid.uuid4()
        self.url = url
        self.headLine = headLine
        self.centroidRating = None
        self.std = None
        self.associatedRatings =[]

    def __str__(self):
       return f'id: {self.id}\nurl: {self.url}\nheadLine: {self.headLine} \ncentroidRating: {self.centroidRating}' 