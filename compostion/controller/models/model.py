from lib2to3.pytree import convert
from urllib.request import proxy_bypass
from .data import database
from .data.objects.newsElement import NewsElement
from .data.objects.factChecker import FactChecker
from .data.objects.rating import Rating

import uuid

class Model (object):

    def __init__(self):
        pass 

    #region newsTable
    def create_news(self,url:str,headLine:str):
        database.create_news(NewsElement(url,headLine))

    def get_all_news(self):
        return database.get_all_news()
    
    def read_news(self,id:str):
       return database.read_news_id(self.convert_to_uuid(id))

    def read_news_headLine(self,headLine:str,url:str):
        return database.read_news_headLine(headLine,url)

    def add_rating_to_news(self,news_id,rating_id):
        database.add_rating_to_news(news_id,rating_id)

    def update_std_value(self, news_id:str):
        database.update_std_value(self.convert_to_uuid(news_id))
    
    def delete_news(self,news_id:str):
        database.delete_news(self.convert_to_uuid(news_id))
    
    def get_news_id_with_url(self,news_url:str):
        return database.get_news_id_with_url(news_url)
        
    def validate_news_has_score(self, news_id:str):
       return database.validate_news_has_score(self.convert_to_uuid(news_id))



    def print_news(self):
        database.print_news_table()
    #endregion

    #region Factchecker
    def create_fact_checker(self,name:str,scale:int):
        database.create_fact_checker(FactChecker(name,scale))
        
    def read_fact_checker(self,id:str):
        return database.read_fact_checker(self.convert_to_uuid(id))

    def update_fact_checker_credibility(self,id:str,consensus_score,centroid,sigma):
        database.update_fact_checker_credibility(id,consensus_score,centroid,sigma)

    def update_reviewed_news(self,id:str):
        database.update_reviewed_news(self.convert_to_uuid(id))

    def update_accurate_news(self,id:str):
        database.update_accurate_news(self.convert_to_uuid(id))

    def update_fact_checker_name(self,id:str,newName:str):
        database.update_fact_checker_name(self.convert_to_uuid(id),newName)
    
    def  get_fact_checker_id_with_name(self,name:str):
        return database.get_fact_checker_id_with_name(name)

    def get_associated_factChecker(self,rating_id):
        return database.get_associated_factChecker(rating_id)
    
    def get_credibility(self,fact_check_id):
        return database.get_credibility(fact_check_id)

    def print_facts(self):
        database.print_facts()
    
    #endregion 

    #region rating 
    def create_rating(self,score:int,scale:int,factCheckerID:str):
        database.create_rating(Rating(score,scale,self.convert_to_uuid(factCheckerID)))

    def create_rating_and_return_id(self,score:int,scale:int,factCheckerID):
        rating = Rating(score,scale,factCheckerID)
        database.create_rating(rating)
        return rating.id
        
    def read_rating(self,rating_id:str):
        return database.read_rating(self.convert_to_uuid(rating_id))
    
    # return all the ratings from a news 
    def get_all_ratings_from_newsid(self,news_id:str):
        return database.get_all_ratings_from_news(self.convert_to_uuid(news_id))

    def delete_rating(self,rating_id:str):
        database.delete_rating(rating_id)

    def get_score(self,rating_id):
        return database.get_score(rating_id)
    
    def print_ratings(self):
        database.print_ratings()
    #endregion

    #region helpers  methods 
    def convert_to_uuid(self,id:str):
        return uuid.UUID(id)

    def get_all_ratings(self):
        return database.get_all_ratings()

    def get_all_facts(self):
        return database.get_all_facts()

    def get_centroid(self, news_id:str):
        return database.get_centroid(self.convert_to_uuid(news_id))

    def get_std(self, news_id:str):
        return database.get_std(self.convert_to_uuid(news_id))

    def update_centroid_value(self,news_id:str):
        database.update_centroid_value(self.convert_to_uuid(news_id))

    def initialize_all_centroid_values_and_std(self):
        database.initialize_all_centroid_values_and_std()

    #endregion
    
    #Consensus computation algorithm and 
    #values updates of the diferents variables 
    def get_consensus(self,news_id):

        has_score = self.validate_news_has_score(news_id)
        consensus = None

        if(not has_score):
            ratings= self.get_all_ratings_from_newsid(news_id)
            sum_of_credibilities = 0
            sum_of_fact_time_cred = 0
            associated_fact_checkers = []

            for rating in ratings:
                fact_check = self.get_associated_factChecker(rating)
                associated_fact_checkers.append(fact_check)
                cred = self.get_credibility(fact_check)
                sum_of_credibilities+=cred
                sum_of_fact_time_cred+=float(cred)*float(self.get_score(rating))
            
            if sum_of_credibilities!=0:
                consensus = sum_of_fact_time_cred/sum_of_credibilities
            

            centroid = self.get_centroid(news_id)
            sigma = self.get_std(news_id)

            if centroid!=None and sigma!=None :
                for fact_check in associated_fact_checkers:
                    self.update_fact_checker_credibility(fact_check,consensus,centroid,sigma)
            
        return consensus


            

    
