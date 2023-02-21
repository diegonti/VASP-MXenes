import os

class OUTCAR():
    def __init__(self,path) -> None:

        self.path = path
        self.data,self.raw_data = self.getData()


        pass

    def getData(self):

        data = []
        with open(self.path,"r") as inFile:
            raw_data = inFile.readlines()
            for line in inFile:
                line = line.strip().split()
                data.append(line)

        return data, raw_data
    
    def getOpt(self):
        pass

    def search(self,target,after,before,until):
        pass
