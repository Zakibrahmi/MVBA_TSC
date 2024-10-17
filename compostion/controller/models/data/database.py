from multiprocessing import Value
import uuid
import math 
import statistics
from .objects import dataExceptions as db_exc
from .objects.newsElement import NewsElement
from .objects.factChecker import FactChecker
from .objects.rating import Rating 

newsTable = []
ratingTable = []
fact_checker_table = []
EPS_ACC = 1

#region  NewsTable 
def create_news(news):
    global newsTable

    if validateNewsInDB_headLine(news.url,news.headLine,newsTable):
        raise db_exc.ObjectAlreadyInDB('"{}"already in stored in the database'.format(news.headLine))

    newsTable.append({
        'id':news.id,
        'url':news.url,
        'headLine':news.headLine,
        'centroidRating':None,
        'std':None,
        'associatedRatings':[],
        'score':None
    })
       
# returns a substring info of the given news 
def read_news_id(id:uuid):
    global newsTable

    value = returnNewsFromDB_id(id,newsTable)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(id))
    return value

# returns a substring info of the given news 
def read_news_headLine(headLine:str, url:str):
    global newsTable

    value = returnNewsFromDB_headLine(headLine,url,newsTable)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(headLine))
    return value
    
# Add an associated rating in the list of ratings that are handled
# by the factCheckers
def add_rating_to_news(news_id,rating_id):
    global newsTable
    global ratingTable

    #check if news in DB
    if not validateNewsInDB_id(news_id,newsTable):
        raise db_exc.ObjectNotInDB('"{}"is not stored in the database'.format(news_id))

    #check if rating in DB 
    if not validate_rating_in_db(rating_id,ratingTable):
        raise db_exc.ObjectNotInDB('"{}"is not stored in the database'.format(rating_id))
    
  
    # look if rating is already in associatedRatings
    associatedRatings = returnNewsFromDB_id(news_id,newsTable)[0]["associatedRatings"]
    #-->need edge case for adding the same rating many time
    associatedRatings.append(rating_id)

#This function deal with a individual news
def update_centroid_value(news_id):
    # get all the values 
    # sort and separate them -> compute the value
    # if we have no rating the score = None
    ratings_score = get_ratings_from_news(news_id)
    rating_score_int = []

    if ratings_score ==[]:
        set_centroid_value(news_id,None)

    for score in ratings_score:
        rating_score_int.append(int(score))

    # compute actual centroid
    computedScore = compute_centroid(rating_score_int)
    set_centroid_value(news_id,computedScore)

#Everytime an new rating is added/delete to the object,
#The std  value is updated 
def  update_std_value(news_id):
    ratings_score = get_ratings_from_news(news_id)
    if ratings_score ==[]:
        set_std_value(news_id,None)
    computedScore = compute_std(ratings_score)
    set_std_value(news_id,computedScore)

def get_news_id_with_url(news_url:str):
    global newsTable
    value = returnNewsFromDB_url(news_url,newsTable)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(news_url))
    return value[0]['id']

def get_centroid(id):
    centroid = read_news_id(id)[0]['centroidRating']
    if centroid == None:
        initialize_all_centroid_values_and_std()
        centroid = read_news_id(id)[0]['centroidRating']
    return centroid

def get_std(id):
    return read_news_id(id)[0]['std']

#remove a centroid value from a news element
def delete_news(id:uuid): 
    global newsTable

    for  indx, elem in enumerate(newsTable):
        if elem["id"] ==id:
            newsTable.pop(indx)
        break

def print_news_table():
    global newsTable
    for n in newsTable:
        print(n)

def validate_news_has_score(news_id):
    global newsTable

    value = returnNewsFromDB_id(news_id,newsTable)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(id))
    return value[0]['score']!=None

#endregion 

#region FactCheckerTable 
def create_fact_checker(factChecker):
    global fact_checker_table

    if validate_fact_checker_in_db(factChecker.id,fact_checker_table):
         raise db_exc.ObjectAlreadyInDB('"{}"already in stored in the database'.format(factChecker.id))

    fact_checker_table.append({
        'id':factChecker.id,
        'name':factChecker.name,
        #h_i
        'newsReviewed':factChecker.newsReviewed,
        #r_x
        'accurateNews':factChecker.accurateNews,
        'scale':factChecker.scale,
        # initialize at this value when first created
        # Later will have a process to store those value in it
        'credibility':0.5,
        'alpha':0,
        'beta':0,
        'h_r':1
    })

def get_fact_checker_id_with_name(fact_checker_name):
    global fact_checker_table
    value = list(filter(lambda x: (x['name']==fact_checker_name),fact_checker_table))
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(fact_checker_name))
    return value[0]["id"]

def get_credibility(fact_checker_id):
    global fact_checker_table
    value = list(filter(lambda x: (x['id']==fact_checker_id),fact_checker_table))
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(fact_checker_id))
    return value[0]["credibility"]

def read_fact_checker(id:uuid):
    global fact_checker_table
    value = returnFactCheckerFromDB_id(id,fact_checker_table)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(id))
    return value

#computing the credibility Score 
def update_fact_checker_credibility(id:uuid,consensus_score,centroid,sigma):
   fact_checker = read_fact_checker(id)[0]
   fact_checker['beta']= update_beta(consensus_score,centroid,sigma)
   fact_checker['alpha'] = update_alpha(fact_checker['credibility'],consensus_score,centroid)
   accurate = compute_accuracy(fact_checker['credibility'],consensus_score,EPS_ACC)
   if accurate:
    fact_checker['accurateNews']+=1
   fact_checker['newsReviewed']+=1

   fact_checker['h_r']=fact_checker['accurateNews']/fact_checker['newsReviewed']
   fact_checker['credibility'] = compute_credibility(fact_checker)
    
def update_reviewed_news(id:uuid):
    global fact_checker_table
    if not validate_fact_checker_in_db(id,fact_checker_table):
        raise db_exc.ObjectNotInDB('"{}"is not stored in the database'.format(id))

    returnFactCheckerFromDB_id(id,fact_checker_table)[0]["newsReviewed"]+=1

def update_accurate_news(id:uuid):
    global fact_checker_table
    if not validate_fact_checker_in_db(id,fact_checker_table):
        raise db_exc.ObjectNotInDB('"{}"is not stored in the database'.format(id))
    
    returnFactCheckerFromDB_id(id,fact_checker_table)[0]["accurateNews"]+=1

def update_fact_checker_name(id:uuid,newName:str):
    global fact_checker_table
    if not validate_fact_checker_in_db(id,fact_checker_table):
        raise db_exc.ObjectNotInDB('"{}"is not stored in the database'.format(id))
    
    returnFactCheckerFromDB_id(id,fact_checker_table)[0]["name"]=newName
 
##credibility methods 
def compute_credibility (factChecker):
    return factChecker['h_r']*(factChecker['credibility']+factChecker['alpha']*factChecker['beta'])

def update_alpha(credibility,rating,centroid):
    return credibility*(1- abs(rating - centroid))

def update_beta(rating,centroid,sigma):
    sqrt_operation = math.sqrt((centroid-rating)**2)

    if sqrt_operation<sigma:
        return 1 - (sqrt_operation/sigma)
    return (sigma/sqrt_operation) -1 

def compute_accuracy(rating,consensus_score,eps_acc):
    return abs(rating-consensus_score)<eps_acc

#endregion

#region ratingTable
def create_rating(rating):
    global ratingTable

    if validate_rating_in_db(rating.id,ratingTable):
        raise db_exc.ObjectAlreadyInDB('"{}"already in stored in the database'.format(rating.id))

    ratingTable.append({
        'id':rating.id,
        'score':rating.score,
        'scale':rating.scale,
        'factCheck':rating.fact_checkers_id
    })

def read_rating(id):
    global ratingTable
    value = returnRatingFromDB_id(id,ratingTable)
    if value ==[]:
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(id))
    return value

#return the factchecker that is linked to the given rating
def get_associated_factChecker(rating_id):
    return read_rating(rating_id)[0]['factCheck']

def get_score(rating_id):
    return read_rating(rating_id)[0]['score']

def delete_rating(id):
    global ratingTable
    for  indx, elem in enumerate(ratingTable):
        if elem["id"] ==id:
            ratingTable.pop(indx)
        break
  
def print_facts():
    global fact_checker_table
    for n in fact_checker_table:
        print(n)

def print_ratings():
    global ratingTable
    for n in ratingTable:
        print(n)

def get_all_ratings():
    return ratingTable

def get_all_facts():
    return fact_checker_table

def get_all_news():
    return newsTable

#endregion

#region Helper methods
def validate_rating_in_db(id,table):
    return list(filter(lambda x:(x['id']==id),table))!=[]

def validateNewsInDB_headLine(url:str,headLine:str,table):
    return list(filter(lambda x: (x['url']==url)and(x['headLine']==headLine),table))!=[]

def validateNewsInDB_id(id,table):
    return list(filter(lambda x: (x['id']==id),table))!=[]

def validate_fact_checker_in_db(id,table):
    return list(filter(lambda x:(x['id']==id),table))!=[]

def returnNewsFromDB_id(id,table):
     return list(filter(lambda x: (x['id']==id),table))

def returnNewsFromDB_url(url,table):
     return list(filter(lambda x: (x['url']==url),table)) 

def returnNewsFromDB_headLine(headLine:str,url:str,table):
     return list(filter(lambda x: (x['url']==url)and(x['headLine']==headLine),table))

def returnRatingFromDB_id(id,table):
     return list(filter(lambda x: (x['id']==id),table))

def returnFactCheckerFromDB_id(id,table):
    return list(filter(lambda x: (x['id']==id),table))

#get all the rating associated to a given news element
def get_ratings_from_news(news_id):
    global newsTable
    if not validateNewsInDB_id(news_id,newsTable):
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(news_id))

    ratings = returnNewsFromDB_id(news_id,newsTable)[0]["associatedRatings"]
    ratings_numeric = []
    # updating the rating_id by the rating index 
    for  rating_id in ratings:
        ratings_numeric.append(returnRatingFromDB_id(rating_id,ratingTable)[0]["score"])
    ratings_numeric.sort()
    return ratings_numeric

def get_all_ratings_from_news(news_id):
    global newsTable
    if not validateNewsInDB_id(news_id,newsTable):
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(news_id))

    ratings = returnNewsFromDB_id(news_id,newsTable)[0]["associatedRatings"]
    return ratings

def set_centroid_value(news_id,value):
    global newsTable
    if not validateNewsInDB_id(news_id,newsTable):
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(news_id))
    returnRatingFromDB_id(news_id,newsTable)[0]["centroidRating"] = value

def set_std_value(news_id,value):
    global newsTable

    if not validateNewsInDB_id(news_id,newsTable):
        raise db_exc.ObjectNotInDB('"{}" not in the database!'.format(news_id))
    returnRatingFromDB_id(news_id,newsTable)[0]["std"] = value

# for now the value resemble the one of centroid but it will be updated as centroid gets more dimensions
def compute_mean(values):
    lower_sum = len(values)
    upper_sum = 0
    for val in values:
        upper_sum +=int(val)
    try:
        return upper_sum/lower_sum
    except ZeroDivisionError:
        print("Invalid Equation")

#the centroid value is updated: sum(n_i *i)/sum(n_i)
def compute_centroid(values):
    lower_sum = len(values)
    upper_sum = 0
    for val in values:
        upper_sum +=val
    
    try:
        return upper_sum/lower_sum
    except ZeroDivisionError:
        print("Invalid Equation")

def compute_std(values):
    if len(values)>0:
        mean = compute_mean(values)
        sum_of_distances =0

        for val in values:
            sum_of_distances+= math.fabs(int(val)-mean)**2
        try:
            if values !=[]:
                return  math.sqrt(sum_of_distances/len(values))
        except ZeroDivisionError:
            print("Invalid Equation")

#endregion

#region scoreHelpers
def compute_mj(values_list,eps):
    cluster_list = compute_clusters(values_list,eps)
    max_indice = 0
    for i in range(len(cluster_list)):
        if len(cluster_list[i])>len(cluster_list[max_indice]):
            max_indice = i
    return compute_centroid(cluster_list[max_indice])

def compute_centroid(values_list):
    if values_list!=[]:
        return sum(values_list)/len(values_list)

# taken from stackOverflow >>>(1D)
def compute_clusters(points,eps_value):
    clusters = []
    eps = eps_value
    points_sorted = sorted(points)
    curr_point = points_sorted[0]
    curr_cluster = [curr_point]
    for point in points_sorted[1:]:
        if point <= curr_point + eps:
            curr_cluster.append(point)
        else:
            clusters.append(curr_cluster)
            curr_cluster = [point]
        curr_point = point
    clusters.append(curr_cluster)
    return clusters

def compute_std_value(values_list):
    values_list_int = []
    for value in values_list:
        values_list_int.append(int(value))
    return statistics.stdev(values_list_int)

#Apply the operation of initialization
#centroid and std calculation to all the values 
def initialize_all_centroid_values_and_std():
    global newsTable 
    for news in newsTable:
        update_centroid_value(news['id'])
        update_std_value(news['id'])

#endregion

    