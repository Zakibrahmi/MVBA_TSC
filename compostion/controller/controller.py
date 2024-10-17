
from numpy import random
from bson.objectid import ObjectId
import numpy as np
from scipy.stats import truncnorm
from sklearn.cluster import KMeans
from . import *
import statistics
import math
class Controller(object):

    def __init__(self,model,view):
        self.model = model 
        self.view = view 
    
    
    def get_truncated_normal(self, mean=0, sd=1, low=0, upp=10):
        return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
    # For each created news we generate decision for each fact-cheker, 
    # 1. using Gaussian distribution to model the behavior of fact-chacker: mean is the news’s real decision 
    # 2. calculate the consensus of news and update credibility of fact-cheker. At time 0 credibility = 0.5
    # The analytic evaluation use numberFactCherke (=100 by default) fact-chekers. 
    # honest is the % of honest sample(factchekers). Therefore dishonest will be 1- honest
    # gamma, phi, and H are used by Analytic method. Epsilon is used by simulation method
    # Params: honest = % of honest, gamma, phi, and H used for the analytic purpose. H is higher means fact-checker has a good raiting in the past 
    def dataSet(self, numberNews, numberFactCherker, honest,  gamma, phi, Epsilon, H):
                
        #Create collection according to percent of honest.
        nameCollection_Name = "Penality_FactCheckers_" + str(honest*100)
        nameCollection = mongo[nameCollection_Name]        
        
        nameCollection_News_Name = "Penality_News_" + str(honest*100)
        nameCollection_News = mongo[nameCollection_News_Name] 
        for w in range(numberNews):
            
            # Random decsion of a news w:
            dec = random.randint(1, 5)
            
            # to generate dishonet, we set mean (= dec) to +2 if dec <0 lese -2
            decDishonet = (dec + 2) if dec <= 2 else (dec - 2)
            #Generate fact-chekerer decisions follwing a normal distribution with means(loc) = dec
              # 1.Genrate % hostest close to mean
            #xHonet = random.normal(loc=dec, scale= 0.5, size= round(numberFactCherker*honest))
            #xDisHonnet = random.normal(loc=dec, size= (numberFactCherker- round(numberFactCherker*honest)))
            checkers =[]
            i = 1
            xHonet = self.get_truncated_normal(dec, 0.4, 1, 5).rvs(round(numberFactCherker*honest))
            xDisHonnet = self.get_truncated_normal(decDishonet, 0.4, 1, 5).rvs(round(numberFactCherker - numberFactCherker*honest))
            res = nameCollection_News.insert_one({"virtualDecision": dec})
            
            name=""
            x = np.concatenate((xHonet, xDisHonnet))
            for a in np.round(x):
              
                name = "FC"+ str(i)+""
                i +=1
                checkers.append({"id": name, "decision": a})
                data={}
                data["name"]= name
                history =[]
                history.append({"news":res.inserted_id, "decision": a})
                data["history"] = history
                
                data["credibility_No_Penality"]= 0.5
                data["credibility_Simulation"]= 0.5
                fact = nameCollection.find_one({"name": name})
                #Fact checker doesn't exist => create new One
                if fact == None:
                   nameCollection.insert_one(data)
                else:
                   nameCollection.update_one({"name": name}, {"$addToSet":{"history": {"news":res.inserted_id, "decision": a }}})    
                    
            # Update news by checkers decision
            nameCollection_News.update_one({"_id": res.inserted_id} , {"$set":{"checkers" : checkers}})

            # Calculate consensus=> agregation of decion and update news by consensus
            #consensus = self.consensus_Analytic(res.inserted_id, nameCollection_Name, nameCollection_News_Name, gamma, phi, Epsilon, H)
            
            consensus, consensus_No_Penal = self.consensus_Simulation(res.inserted_id, nameCollection_Name, nameCollection_News_Name, Epsilon)
            nameCollection_News.update_one({"_id": res.inserted_id} , {"$set":{"consensus_No_Penality": consensus_No_Penal, "consensus_Simulation": consensus}})
           
    # Function to compute consensus about the  news news_id. Analytic method
    def consensus_Analytic(self, news_id, name_Fact_Collection, name_Collection_News, gamma, phi, Epsilon, H):

        consensus = None
        name_Collection_News= mongo[name_Collection_News]
        name_Fact_Collection = mongo[name_Fact_Collection]
        w = name_Collection_News.find_one({"_id": ObjectId(news_id)})
        #fact = nameCollection.find_one({"name": name})
        if(w != None):
            ratings= w["checkers"]
            sum_of_credibilities = 0
            sum_of_fact_time_cred = 0
                        
            consensus =0
            # rating is a couple <id/name of fact-cheker and its decision about the given news
            for rating in ratings:
                fact_check = name_Fact_Collection.find_one({"name": rating["id"]})                
                
                cred = self.fact_checker_credibility_Analytic(w, rating["decision"], fact_check ['credibility'], gamma, phi, Epsilon, H )
                #print(cred)
                name_Fact_Collection.update_one({"name": rating["id"]}, {"$set": {'credibility': cred}})
                sum_of_credibilities+=cred
                
                sum_of_fact_time_cred+=float(cred)*float(rating["decision"])                          
            
            if sum_of_credibilities!=0:
                consensus = float(sum_of_fact_time_cred)/float(sum_of_credibilities)        
                                   
        return float(consensus / 5)
    
    # alpha and beta are constants value between 0 and 1 used on the analytic model.
    # sigma if constant used to evaluate if fact-checker is honet or dishonet: factRate - Epsilon 
    def fact_checker_credibility_Analytic(self, w, fact_checker_rating_w, current_credibility, gamma, phi, Epsilon, H ):
        
        # Calculate the mean of all rating
        # List of fact-checkers rates are in w['chekers']
        sum_of_rating =0
        for rate in w['checkers']:
            sum_of_rating+= rate['decision']
        
        M = float(sum_of_rating)/len(w['checkers'])  
        
        
        if abs(fact_checker_rating_w - w["virtualDecision"]) <= 2: #Honet; close to real decison of the news
            credibility  = float(current_credibility * (1 + gamma * (1 - float(abs(fact_checker_rating_w - M) / 5)) * H))
        else: # Dishonet 
            credibility  = float(current_credibility * (1 - phi * (1 - float(abs(fact_checker_rating_w - M) / 5)) * H))
        
        if credibility > 1:
            credibility = 1 
        if credibility < 0.09: #to avoid credibility = 0
            credibility = 0.09
        return credibility
        
#------------------------------------- Simulation --------------------

    def consensus_Simulation(self, news_id, name_Fact_Collection, name_Collection_News, Epsilon):

        consensus = 0
        Collection_News= mongo[name_Collection_News]
        Fact_Collection = mongo[name_Fact_Collection]
        w = Collection_News.find_one({"_id": ObjectId(news_id)})
        #fact = nameCollection.find_one({"name": name})
        if(w != None):
            ratings = w["checkers"]
            sum_of_credibilities = 0
            sum_of_fact_time_cred = 0
            sum_of_credibilities_No_Panality = 0
            sum_of_fact_time_cred_NoPenality = 0
                        
            consensus = 0
            consensus_No_Penality = 0
            # rating is a couple <id/name of fact-cheker and its decision about the given news
            for rating in ratings:
                fact_check = Fact_Collection.find_one({"name": rating["id"]})                
                
                cred = self.fact_checker_credibility_Simulation(w, rating["id"], rating["decision"], fact_check ['credibility_Simulation'], name_Collection_News, name_Fact_Collection, Epsilon )
                cred_No_penality = self.fact_checker_credibility_No_Penality(w, rating["id"], rating["decision"], fact_check ['credibility_No_Penality'], name_Collection_News, name_Fact_Collection, Epsilon )
                Fact_Collection.update_one({"name": rating["id"]}, {"$set": {'credibility_Simulation': cred, "credibility_No_Penality": cred_No_penality}})
                sum_of_credibilities+=cred
                sum_of_credibilities_No_Panality += cred_No_penality
                
                sum_of_fact_time_cred+=float(cred)*float(rating["decision"])   
                sum_of_fact_time_cred_NoPenality +=  float(cred_No_penality)*float(rating["decision"])                    
            
            if sum_of_credibilities!=0:
                consensus = float(sum_of_fact_time_cred)/float(sum_of_credibilities)  
            if sum_of_credibilities_No_Panality!=0:
                consensus_No_Penality = float(sum_of_fact_time_cred_NoPenality)/float(sum_of_credibilities_No_Panality)     
                                   
        return float(consensus / 5), float(consensus_No_Penality / 5)
    
    def fact_checker_credibility_Simulation(self, w, checker_Id, fact_checker_rating_w, current_credibility, collection_News, Collecton_factChecker, Epsilon):        
        
        # Calculate the mean of all rating
        # List of fact-checkers rates are in w['checkers']
        sum_of_rating =0
       
        alpha = 1
        ratings_Fact_Checkers= []
        for rate in w['checkers']:
            sum_of_rating+= rate['decision']
            ratings_Fact_Checkers.append(rate['decision'])
        
        M = self.centroidK(ratings_Fact_Checkers)
        alpha = current_credibility * (1 - float(float(abs(fact_checker_rating_w - M)) / 5))
        H = self.bayesian_average_History(checker_Id, Collecton_factChecker, collection_News, Epsilon)
       
        credibility = current_credibility + alpha * self.beta(ratings_Fact_Checkers, M, fact_checker_rating_w) * H 
        if credibility > 1:
            credibility = 1
        if credibility < 0.09: #to avoid credibility = 0
            credibility = 0.09    
        return credibility
    
    # Compute Beta
    def beta (self, ratings_Array, Mj, Nr):
        
        # Standard diviation
        rho = statistics.stdev(ratings_Array); 
        d = math.sqrt(pow((Mj - Nr), 2))
        if d < rho:
            return (1 - float(d/rho))
        else:
            return -(1 - float(rho/d)) 
    
    # function to compute the centroid of the largest cluster 
    def centroidK(self, ratings):
    
        #ratings = [1, 5, 4, 2, 5]
        X = np.array(ratings)
        X= np.reshape(X, (-1, 1))
        kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(X)
        kmeans.cluster_centers_
        kmeans.labels_
        # mydic contains the indices of the points for each corresponding cluster
        mydict = {i: np.where(kmeans.labels_ == i)[0] for i in range(kmeans.n_clusters)}
       
        longest = max(len(item) for item in mydict.values())
        # Get the indices of the largest clusters= > an arry of simulaire indices,
        # so we need only the first one indice_Largest_Cluster[0] 
        indice_Largest_Cluster = [ key for key, value in mydict.items() if len(value) == longest] 
        # Get the the centroid of the largest cluster from the array of center clusters    
        center = kmeans.cluster_centers_[indice_Largest_Cluster[0]]
        
        return round(center[0])

    def bayesian_average_History(self, fact_cheker_id, name_Collection_FactChekers, collection_News, Epsilon=0.5):
        
        sum_rating =0
        fact_checker = mongo[name_Collection_FactChekers]
        news_Collection = mongo[collection_News]
        fact_checker = fact_checker.find_one({"name": fact_cheker_id})
        W_count = len(fact_checker['history']) - 1 # To remove the current news
        if len(fact_checker["history"]) <= 1: 
            return 1    
        for h in fact_checker["history"]:
            
            d = h['decision']
            
            w = news_Collection.find_one({"_id": ObjectId(h['news']), "consensus_Simulation" : {"$exists": True}})
            if w != None:             
                if abs(float(d / 5) - w['consensus_Simulation']) <= Epsilon:
                    sum_rating += 1
        total_Accurate = self.tolal_Accurate_FactCheckers(name_Collection_FactChekers, collection_News, Epsilon)
        if total_Accurate == 0:
            W_Avg = 0
        else:        
            W_Avg = float(sum_rating) /  total_Accurate
       
        # Mean of fact-checked news/claims across the whole data-set => 
        # La somme de toutes les rates divisée par le nombre de rates
        #  number of rates = somme des number de rates done by each fact-checker.
        W_mean = self.W_mean(collection_News)  
        W_min = 1      
        
        return float((W_Avg *  W_count + W_mean * W_min) / (W_count +1)) / 5 # To scale to between 0 and 1
    
    
    def W_mean(self, name_Collection_News):        
        sum_rating = 0
        number_rating =0
        name_Collection_News = mongo[name_Collection_News]
        for w in name_Collection_News.find({"consensus_Simulation" : {"$exists": True}}):
            # Computer the number of all rating of the data base
            number_rating += len(w['checkers'])
            for r in w['checkers']:
                sum_rating += r['decision']
                
        return (float(sum_rating / number_rating))
    
    
    # Return the number of ratings done by all fact-chekers    
    def count_Rating_All_FC(self, name_Collection_News):
        
        # Computer the number of all rating of the database  
        sum_rating = 0
        collection_News = mongo[name_Collection_News]
        for w in collection_News.find({"consensus_Simulation" : {"$exists": True}}):
                      
            number_rating += len(w['checkers'])
            for r in w['checkers']:
                sum_rating += r['decision']
           
        return sum_rating
    
    # Total number of accurate rating of all fact-checkers
    def tolal_Accurate_FactCheckers(self, name_Collection_FactChekers, name_Collection_News, Epsilon):
        
        total_Accurate = 0
        name_Collection_FactChekers = mongo[name_Collection_FactChekers]
        news_Collection = mongo[name_Collection_News]
        for f in name_Collection_FactChekers.find():
            
            for new in f["history"]:
                d = new['decision']
                w = news_Collection.find_one({"_id": ObjectId(new['news']), "consensus_Simulation" : {"$exists": True}})
                if w!= None: 
                    if abs(float(d/5) - w['consensus_Simulation'] <= Epsilon):
                        total_Accurate += 1
            
        return total_Accurate
    
    #Credibility by simulation without take into account penality of history 
    def fact_checker_credibility_No_Penality(self, w, checker_Id, fact_checker_rating_w, current_credibility, collection_News, Collecton_factChecker, Epsilon):        
        
        # Calculate the mean of all rating
        # List of fact-checkers rates are in w['checkers']
        sum_of_rating =0
        Beta = 1
        alpha = 1
        ratings_Fact_Checkers= []
        for rate in w['checkers']:
            sum_of_rating+= rate['decision']
            ratings_Fact_Checkers.append(rate['decision'])
        
        M = self.centroidK(ratings_Fact_Checkers)
        alpha = current_credibility * (1 - float(float(abs(fact_checker_rating_w - M)) / 5))       
        credibility = current_credibility + alpha * self.beta(ratings_Fact_Checkers, M, fact_checker_rating_w)  
        if credibility > 1:
            credibility = 1
        if credibility < 0.09: #to avoid credibility = 0
            credibility = 0.09    
        return credibility 
    

