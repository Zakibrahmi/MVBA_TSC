from hashlib import new
from rich.console import Console
import uuid
VERSION = "1.3.0"

class View(object):
    
    #region menu info
    def __init__(self) -> None:
        self.console = Console()
    
    def display_intro_screen(self):
        self.console.print(f"\nConsensus Inference v {VERSION}\n",style= "bold")
    
    def display_missing_files(self):
        self.console.print("Missing news File, please place and try again...\n",style= "bold")
        
   
    def display_make_sure_files_present(self):
        self.console.print("Please Make sure that the files :")
        self.console.print(" - fact_checkers.txt\n - news.txt\n - ratings.tx",style="blue")
        self.console.print("are in the source folder before proceding")
        print("\n")
    
    def display_not_parsed_files(self,files_names):
        self.console.print("The Following files could not be parsed:")
        fileString = ""
        for file in files_names:
            fileString+="- "+file+"\n"
        self.console.print(fileString,style="blue")
        self.console.print("please ensure that the format is correct and try again\n")
    
    
    def display_command_list(self):
        self.console.print("- viewallnews\n- viewnews <newsId>\n")
        self.console.print("- viewallfactcheckers\n- viewfactchecker<factCheckerId>\n")
        self.console.print("- viewallratings\n- viewrating <ratingId>\n")
        self.console.print("- computeconsensus <newsId>\n")
        self.console.print("- clear(erase screen)\n")
        self.console.print("- exit")
    #endregion

    #region news
    def display_news_info(self,table,news):
        table.add_column("id",style="cyan")
        table.add_column("url",style ="white")
        table.add_column("headline",style="white")
        table.add_column("centroid rating",style ="white")
        table.add_column("std rating",style="white")

        table.add_row(
            str(news[0]["id"]),
            str(news[0]["url"]),
            str(news[0]["headLine"]),
            str(news[0]["centroidRating"]),
            str(news[0]["std"])
            )
        self.console.print(table)
       
    def display_all_news_info(self,table,newList):
        table.add_column("id",style="cyan")
        table.add_column("url",style ="white")
        table.add_column("headline",style="white")
        for news in newList:
            table.add_row(str(news["id"]),str(news["url"]),str(news["headLine"]))
        self.console.print(table)
    #endregion

    #region fact_checkers
    def display_fact_checker_info(self,table,fact_cheker):
        table.add_column("id",style="cyan")
        table.add_column("name",style ="white")
        table.add_column("newsReviewed",style="white")
        table.add_column("accurate news",style ="white")
        table.add_column("scale",style="white")

        table.add_row(
            str(fact_cheker[0]["id"]),
            str(fact_cheker[0]["name"]),
            str(fact_cheker[0]["newsReviewed"]),
            str(fact_cheker[0]["accurateNews"]),
            str(fact_cheker[0]["scale"])
            )
        self.console.print(table)
      
    def display_all_fact_checkers_info(self,table,fact_cheker_list):
        table.add_column("id",style="cyan")
        table.add_column("name",style ="white")
        for fact in fact_cheker_list:
            table.add_row(str(fact["id"]),fact["name"])

        self.console.print(table)
    #endregion

    #region ratings
    def display_rating_info(self,table,rating):
        table.add_column("id",style="cyan")
        table.add_column("score",style ="white")
        table.add_column("scale",style="white")
        table.add_column("assossiated factChecker",style="white")

        table.add_row(
            str(rating[0]["id"]),
            str(rating[0]["score"]),
            str(rating[0]["scale"]),
            str(rating[0]["factCheck"])
            )
        self.console.print(table)
        
           
    def display_all_ratings_info(self,table,ratingList):
        table.add_column("id",style="cyan")
        table.add_column("score",style ="white")
        table.add_column("factCheck",style="white")
        for rate in ratingList:
            table.add_row(str(rate["id"]),rate["score"],str(rate["factCheck"]))

        self.console.print(table)
    #endregion

    #region errors 
    def display_no_element_with_id(self,id:str):
        self.console.print(f"Not able to find the element with id: {id}")
    #endregion

    #region consensus
    def display_consensus_calculation(self,consensus_value,news_id):
        self.console.print(f"The consensus value is for the news {str(news_id)} is: {consensus_value}")
    #endregion 
