
from numpy import random
from bson.objectid import ObjectId
import numpy as np
from scipy.stats import truncnorm
from sklearn.cluster import KMeans
from . import mongo
from controller.ServiceProvider import ServiceProvider

class dataSetGeneration():
    

    # This function create the dataset of services. Each service Provider -SP- is connected to an alpha % to others SP. 
    # Each SP deploy a numbre n of services
    # Input: - numberSP: numbre of service provider
    #        - transactions: Number of transaction made by a service provider with another     
    #        - n: number of services per SP
    #        - IO_Classes: An array of input and output of classes. For example [['A', 'B'], ['B', C]],
    #                      fsirt item is: input 'A' and output 'B' of the first class, and so one
    
    def dataSet(self, numberSP, n, transactions, IO_Classes):
                
        nameCollection_SP = "SProviders_" + str(numberSP)
        nameCollectionSP = mongo[nameCollection_SP] 
        
        nameCollection_Services= "Services_" + str(n)
        nameCollection_Services = mongo[nameCollection_Services] 
        nameCollection_Class= "Classes_" + str(n)
        nameCollection_Class = mongo[nameCollection_Class] 
        # Create classes according to the array IO_Classes
        for c in IO_Classes:             
            services =[] 
            datas = {}
            datas['Input'] = c[0]
            datas["Output"] = c[1]
            datas['Services'] = services
            nameCollection_Class.insert_one(datas)
        
        # Choose a random class from IO_Classes with equal probability using a an array of weights
        weights = []
        w = 1/len(IO_Classes)
        for x  in IO_Classes:
            weights.append(w)           
        
        services = [] 
        for _ in range(numberSP):
        
            #Create Service provider
            dataSP = {}
            netWork =[]
            dataSP["NetWork"] = netWork
            res = nameCollectionSP.insert_one(dataSP)
            
            #Choosen classes  for services of the current service provider
            chosen = np.random.choice(len(IO_Classes), n, p=weights)
            # Create n services
            for i in range(n):
                data = {}
                data["QoS"] = random.uniform(0, 1)
               
                cl = IO_Classes[chosen[i]]  # cl contain input and output    
                #print(cl[0])            
                data["Input"] = cl[0]                
                data["Output"] = cl[1]
                data["MyProvider"] = res.inserted_id                
            
                ws = nameCollection_Services.insert_one(data) 
                nameCollection_Class.update_one({"Input": data["Input"], "Output": data["Output"]}, {"$addToSet":{"Services" :ws.inserted_id}}) 
            
        self.creatNetwork(nameCollectionSP, transactions)   
    
    
    # Function to create the network of each service provider and compute the trustValue
    def creatNetwork(self, nameCollectionSP, number_Of_Transaction):
       
        serviderProviders = nameCollectionSP.find()    
        for sp in serviderProviders:
            NetWork = []
            
            for p in nameCollectionSP.find():
                if p['_id'] != sp['_id']: 
                    trust = []
                    for _ in range(number_Of_Transaction):      
                        trust.append(random.uniform(0, 1))
                    NetWork.append({'providerID':p['_id'], "trust": trust})
           
            nameCollectionSP.update_one({"_id": ObjectId(sp['_id'])} , {"$set":{"NetWork" : NetWork}})
            
        # Compute Trust Value of each service provicer
        for sp in nameCollectionSP.find():
            p = ServiceProvider(sp['_id'])
            for ss in nameCollectionSP.find(): 
                if ss['_id'] != p.id:           
                    p.trustValueOf_SP(ss['_id'], nameCollectionSP)
            
   