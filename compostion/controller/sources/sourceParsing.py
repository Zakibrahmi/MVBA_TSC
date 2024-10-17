import csv 

#Files source names
FACT_CHECKER_SOURCE ="controller/sources/factCheck.csv"
NEWS_SOURCE = "controller/sources/news.csv"
RATING_SOURCE = "controller/sources/rating.csv"

class SourceParser(object):

    #Format of the csv files to 
    #Json structures 
    def build_json_formatter(line,type):    
        json_val = None

        if type ==NEWS_SOURCE:
            json_val= {
            'headLine':line['headline'],
                'url':line['url']  
                }
        elif type ==FACT_CHECKER_SOURCE:
            json_val={
                'name':line['name'],
                'scale':line['scale']
                }
        else:
            json_val={
            "factCheckName":line['factCheckName'],
                "newsUrl":line['newsUrl'],
                "score":line['score'],
                "scale":line["scale"] 
            }
        return json_val
    
    # general parsing logic
    def parse(source):
        returnList = []
        try:
            with open(source,'r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for line in csv_reader:
                    returnList.append(SourceParser.build_json_formatter(line,source))
        except FileNotFoundError:
            print(source)
            return False
        return returnList
    
    @staticmethod
    def parse_news():
        return SourceParser.parse(NEWS_SOURCE)

    @staticmethod
    def parse_fact_checkers():
        return SourceParser.parse(FACT_CHECKER_SOURCE)

    @staticmethod
    def parse_rating():
        return SourceParser.parse(RATING_SOURCE)


"""
For debugging
def main():
    print (SourceParser.parse_news())
    print("\n")
    print(SourceParser.parse_fact_checkers())
    print("\n")
    print(SourceParser.parse_rating())
if __name__ == "__main__":
    main()
"""