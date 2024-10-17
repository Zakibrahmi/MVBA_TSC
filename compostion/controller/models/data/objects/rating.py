import uuid

class Rating():

    def __init__(self,score:int,scale:int,fact_checkers_id:int):
        self.id = uuid.uuid4()
        self.score = score
        self.scale = scale
        self.fact_checkers_id =fact_checkers_id

    def __str__(self):
       return f'Rating\n\tid:{self.id}\n\tscore:{self.score}\n\tscale:{self.scale}\n\tfactCheckId:{self.fact_checkers_id}' 