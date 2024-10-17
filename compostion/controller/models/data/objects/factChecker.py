import uuid


class FactChecker():

    def __init__(self, name:str,scale:int):
        self.id = uuid.uuid4()
        self.name = name
        self.newsReviewed = 0
        self.accurateNews = 0
        self.scale = scale 