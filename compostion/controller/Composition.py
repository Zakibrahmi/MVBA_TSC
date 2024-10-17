from bson import ObjectId
import  time
#from scipy.stats import truncnorm
from . import mongo
from concurrent.futures import ThreadPoolExecutor
#from controller.Services import Service

class Composition():    
    
    
    def __init__(self, nameSevicesCollection, ClassCollecion, ProvidersCollection):    
        self.data ={} #map: key: id of the trigged class, value: the id of the parent class     
        self.composition = {}
        self.Graph = {}
        self.Service_Collection =  mongo[nameSevicesCollection] 
        self.Class_Collection =  mongo[ClassCollecion] 
        self.Providers_Collection =  mongo[ProvidersCollection] 
    
    #def get_truncated_normal(self, mean=0, sd=1, low=0, upp=10):
    #   return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
    
    
    # Function to comput the final composition given a request R = {InputR, OutputR}
    # -Parm: InputR, OutputR, class_Collection, services_Collection, providers_Collection, alpha
    
    def compute_Composition (self, InputR, outputR):
    
        #1. Create Graph of classes from classes collection using a dictionary; uuid is the key
        self.Graph = self.createGraph(InputR)
      
        #2. Select the start class and Select the best service  
        class_Start = self.Class_Collection.find({"Input": InputR})
        results = list(class_Start)
        
        if  len(results) == 0:
            print("No composition available")
            return 0 
        # Choose the best service
        class_Start = self.Class_Collection.find({"Input": InputR})       
        
        for c in class_Start:
            self.data.update({str(c['_id']): None})       
              
        #3. Prallel runing of all classes
        with ThreadPoolExecutor(len(self.Graph)) as executor:
            futures = [executor.submit(self.parallel_Run_Classes, cid, outputR) for cid in self.Graph.keys()]
        
    # Parallel runing of classes
    def parallel_Run_Classes(self, c, OutputR):         
        while True: 
            if str(c) in self.data.keys():                           
                values_Services = []
                #Choose the best Service
                for s in self.Class_Collection.find_one({'_id':ObjectId(c)})['Services']:                            
                    values_Services.append ({"id": s, "value": self.evaluate_Service(s)})
                     
                values_Services.sort(key=lambda x: x.get('value'), reverse=True)
                best_Service = values_Services[0]['id']
                value =  values_Services[0]['value']
                           
                if self.composition.get(self.data.get(c)) is None:                  
                    self.composition.update({c: [{"service":best_Service, "value": value}]})
                else: 
                    self.composition.update({self.data.get(c) : self.composition.get(self.data.get(c))+[{"service":best_Service, "value": value}]})
                #First case: Output class = output Request; Decision add best service to composition and stop
                output_Class = self.Class_Collection.find_one({'_id': ObjectId(c)})
               
                if OutputR == output_Class['Output']:        
                    break
                # Add next classes to data to trigged them 
                for next_Class in self.Graph.get(c):
                    self.data.update({next_Class: c})       
                break 
            else:
                time.sleep(1)
            
    # Create graph form class collection; 
    def createGraph (self, InputR):
        Graph ={}
        visited = {}
        classStart = self.Class_Collection.find({"Input": InputR})
        for c in classStart:           
            visited.update({str(c['_id']): c['Output']})
        
        while len(visited)!=0:
            head = next(iter(visited))
            # insert if uuid of class in the dic if donesn't exist or Update the current ky
            #Find succor classes of the current class c
            successor_Classes = self.Class_Collection.find({"Input":visited.get(head)})
            succossor = []
            for s in successor_Classes:
                    succossor.append(str(s['_id']))
                    visited.update({str(s['_id']): s['Output']})
            if Graph.get(head) is None:          
                Graph[head] = succossor
            else: # key exist
                Graph[head] = succossor + Graph[head]
            # Remove first item form visited
            
            visited.pop(head)
        return Graph
                 
    # Compute evaluation of a given ws:
    #    Parameters: IdWS, services collection, providers collection, and alpha     
    def evaluate_Service(self, IdWS, alpha=0.3, beta=0.1):
       
        
        ws = self.Service_Collection.find_one({'_id': ObjectId(IdWS)})    
             
        MyProvider = self.Providers_Collection.find_one({'_id': ObjectId(ws['MyProvider'])})
           
        trustValue = MyProvider['trust_Bayesien_Majority']
        if trustValue < beta:
            return 0; #low trust value            
        else:
            return ws['QoS']*alpha + (1-alpha)*trustValue; # disabled from the ne
        