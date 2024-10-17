import numpy as np
from sklearn.cluster import KMeans
from . import mongo
from bson.objectid import ObjectId
#from numpy.ma.tests.test_core import pi

class ServiceProvider():
    
    #Constructor of the class ServiceProvider
    
    def __init__(self, idSP):
        self.id = idSP
          
    #  Current service provider, self.id,  evaluates the service provider idSP
    # beta is a paremeter to accept or disable a service provider from the netwrok
    def trustValueOf_SP(self, idSP, serviceProvidersCollection, alpha =0.5, constante_C=4, beta=0.3):
        
        #Find All rating/trust_Value given by other SPs to the service provider idSP
        collectionSP = serviceProvidersCollection
        ratings = collectionSP.find({'NetWork.providerID': ObjectId(idSP)}) #set of SPs that rate idSP
        
        #Calculate the bayesian_average by each service provider: result array of trust value
        baysian_Avgr =[] # Array of all trust values sent by all SP
        self_Network = []
       
        for r in ratings:   
            if str(r['_id']) != str(self.id):
                #print(r['_id'],"; ", self.id, r['NetWork'])                 
                baysian_Avgr.append(self.bayesian_average_History(r['NetWork'], idSP, constante_C) )
            else:
                self_Network = r['NetWork']
        #self_Network
       
        personal_Rating = self.bayesian_average_History(self_Network, idSP, constante_C)
        majority_Rating = self.centroidK(baysian_Avgr, 2) # Number of classes = 2 
        trustValue = majority_Rating*alpha +(1-alpha)*personal_Rating
        decision = "enabled"
        if trustValue <	beta:
            decision = "disabled"
           
        collectionSP.update_one({"_id": ObjectId(self.id), "NetWork.providerID" : ObjectId(idSP) } , {"$set":{"trust_Bayesien_Majority" : trustValue, "NetWork.$.decision":  decision}}) 
        collectionSP.update_one({"_id": ObjectId(idSP) } , {"$set":{"trust_Bayesien_Majority" : trustValue}})     
        return  trustValue  
    
    # function to compute the centroid of the largest cluster 
    def centroidK(self, ratings, number_Clusters: int):
    
        #ratings = [1, 5, 4, 2, 5]
        X = np.array(ratings)
        X= np.reshape(X, (-1, 1))
        kmeans = KMeans(n_clusters=number_Clusters, random_state=0, n_init="auto").fit(X)
        kmeans.cluster_centers_
        kmeans.labels_
        # mydic contains the indices of the points for each corresponding cluster
        mydict = {i: np.where(kmeans.labels_ == i)[0] for i in range(kmeans.n_clusters)}
       
        longest = max(len(item) for item in mydict.values())
        # Get the indices of the largest clusters => an arry of simulaire indices,
        # so we need only the first one indice_Largest_Cluster[0] 
        indice_Largest_Cluster = [ key for key, value in mydict.items() if len(value) == longest] 
        # Get the the centroid of the largest cluster from the array of center clusters    
        center = kmeans.cluster_centers_[indice_Largest_Cluster[0]]
        
        return center[0]
    
    def bayesian_average_History(self, Network, idSP, constante_C):
            
        # The avrg rating of the idSP by a service provider SPi
        avg_Of_idSP =0
        all_Intraction =0
        global_Sum=0
        
        for p in Network:                   
            if p['providerID'] == ObjectId(idSP):
                sum_rating = sum(p['trust'])                  
                #avg_Of_idSP = float(sum_rating / number_Of_Interaction)
                global_Sum+= sum_rating
                
            number_Of_Interaction = len(p['trust'])    
                      
            all_Intraction += number_Of_Interaction
        
        global_Avg = float(global_Sum /all_Intraction)
        #global Avrg for all service providers in the network of the service Provider SPi        
        return float((sum_rating*number_Of_Interaction +constante_C*global_Avg)/(all_Intraction + constante_C)) 
    
    
    