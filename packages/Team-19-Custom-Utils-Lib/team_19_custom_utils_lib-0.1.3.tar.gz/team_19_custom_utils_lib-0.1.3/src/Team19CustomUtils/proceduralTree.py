import numpy as np
from Team19CustomUtils import generalUtils

class tree:
    #the goal of procedural generation is to conserve computer resources and generate the tree only as required.
    #due to the unique constraints of the situation, that being the user is not able to perform backwards manipulation,
    #preceding portions of the tree can be "forgotten" and future paths are generated as-needed
    #using computer memory for this task makes for a simple solution as the code already operates upon memory by default

    #this allows for the loading of extremely high-dimension matrices with unknown projected memory sizes to be
    #represented with a predetermined amount of memory space using lower-dimension local representations
    #specifically, the parts of the larger matrix loaded composes of a "present" buffer and a "look-ahead buffer"

    #this is most often used in games featuring linear progression (ie. the player can only move forward to the next map, level, etc.)
    #this is also another reason why most of these games do not feature extensive save capabilities and instead opt for gameplay loops 
    #as any saved data would probably be invalid due to a limited amount of memory being alternated to compress data


    seed = [0, 0, 0] 
    currentDepth = 1 #a variable used for external monitoring of current 'explored' depth
    presentBuffer = None 
    lookAheadBuffer = None
    populator = None
    seeded = 0
    
    

    def setSeed(self, depth:int, branchPopulation:int, divergence:int, populator:list) -> None:
        #depth:  bounding range for random depth generation
        #branchPopulation:  bounding range for random branch population
        #divergence:  bounding ranges for branch count

        self.seed[0] = depth
        self.seed[1] = branchPopulation
        self.seed[2] = divergence
        self.presentBuffer = [0] * self.seed[1]
        self.lookAheadBuffer = np.zeros(divergence, branchPopulation)
        self.populator = populator

        self.seeded = 1

    def populateBuffers(self):
        match self.seeded:
            case 1:
                for i in range(0, len(self.presentBuffer)):
                    #fills the present buffer with random numbers from the populator list
                    self.presentBuffer[i] = self.populator[np.random.randint(0, len(self.populator))]
                    self.populateFutureBuffer()
                    return None
            case _:
                return RuntimeError("the specified tree is currently unseeded")


    def advanceDepths(self, selector:int):
        match self.seeded:
            case 1:
                if(selector > len(self.lookAheadBuffer)):
                    return OverflowError("selector %d ", selector ,"exceeds possible selections %d", len(self.lookAheadBuffer))
                else:
                    #set the selected index of future buffer to current buffer
                    self.currentDepth += 1
                    self.presentBuffer = self.lookAheadBuffer[selector - 1]
                    #regenerate future buffer
                    self.populateFutureBuffer()
                    return None

                    #this operation effectively 'forgets' the previous buffer set
            case _:
                return RuntimeError("the specified tree is currently unseeded")

    def populateFutureBuffer(self):
        match self.seeded:
            case 1:
                for i in range(0, len(self.lookAheadBuffer)):
                    #populates future buffer with different 'choices' of random values
                    #each subset in the future buffer is of equivalent length to the current buffer
                    for j in range(0,len(self.lookAheadBuffer[0])):
                        self.lookAheadBuffer[i][j] = self.populator[np.random.randint(0,len(self.populator))]
                return None
            case _:
                return RuntimeError("the specified tree is currently unseeded")
        







    
        

    

            

