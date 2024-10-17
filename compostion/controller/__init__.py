from bson.objectid import ObjectId
from pymongo import MongoClient


from . import *
#Password amiraAMIRA2000
uri = "mongodb+srv://sebrifaten:composer1234@cluster0.kaukx74.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
mongo = client['CompositionDB']

#class collection
news = mongo.news

