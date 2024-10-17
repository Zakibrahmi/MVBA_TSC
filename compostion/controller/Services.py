from typing import Any
import numpy as np
from sklearn.cluster import KMeans
from . import mongo
from bson.objectid import ObjectId

class Service():
    
    #Constructor of the class ServiceProvider
    
    def __init__(self, idService, inputWS, outputWS, value =0, QoS=0):
        self.id = idService
        self.input = inputWS
        self.output = outputWS
        self._Trust_value = value # trustValue of provider + QoS
        self._QoS = QoS
    
    def get_Input(self):
        return self.input
    
    def get_Output(self):
        return self.output
    
    def get__Trust_value(self):
        return self._Trust_value
    
    def get_QoS(self):
        return self._QoS