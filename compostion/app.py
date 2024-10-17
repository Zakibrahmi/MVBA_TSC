#view Class for implementation 
from controller.Composition import Composition
from controller.ServiceProvider import ServiceProvider
from controller.dataSetGeneration import dataSetGeneration


dataset = dataSetGeneration()


if __name__ == "__main__":
    
    # Steps ***************
    # 1. Generate dataset:   
    #   a.  IO_Classes: An array of input and output of classes. For example [['A', 'B'], ['B', C]],
    #             fsirt item is: input 'A' and output 'B' of the first class, and so one 
    IO_Classes = [['A', 'B'], ['B', 'C'], ['C', 'L']] # Example
    #   b. To generate dataset we use only One time  dataSet function: check the class dataSetGeneration to understand each param
    dataset.dataSet(4, 10, 4, IO_Classes) # for this example; 10 services per service provider = 4*20 = 80, 
                                          # In this example, the number of classes is 4, So 20 services per class 
                                          # Dans la base de données 3 collection seront crées: Services_10, Classes_4, and SProviders_4
    # 2. Compute the composition; step 1 should be disabled 
    #   a. intanciate the class Composition, using name of collection on the data base created by the first step like the flowing example
   # c = Composition('Services_2','Classes_2',  'SProviders_4')
    #   b. call the function compute_Composition using input and output of the request R
   # c.compute_Composition('A', 'L')
  #  print(c.composition)
  
   
    







