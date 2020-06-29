import numpy as np
import pandas as pd


def FilterTheDict(dictObj,callback):
    newDict = dict()
    for (key, value) in dictObj.items():
        if callback((key, value)):
            newDict[key] = value
    return newDict

class Properties:
    
    def __init__(self):
        pass
    
    
    def Efficiency(self,shapley_incode,total_campaign):
        '''
        This ensures that sum of Shapley values (attribution values) of channels equals to the total
        campaign value
        '''
        
        shapley_val_sum = int(round(np.array(list(shapley_incode.values())).sum(),1))
        total_campaign = int(round(total_campaign,1))
        print("Total Shapley values : {} | Total campaign values : {}".format(shapley_val_sum,total_campaign))
        
        if shapley_val_sum == total_campaign:
            return True
        else:
            raise ValueError(
                '''Total campaign contribution equals the sum of Shapley values contributions.
                Find : total_campaign - {} | Shapley values Sum : {}'''.format(total_campaign,total_campaign))
        
    def DummyPlayer(self,M,shapley_incode,total_conversion):
        '''
        A channel that makes no contribution to any coalition will get zero credit
        '''
        
        newDict = FilterTheDict(shapley_incode, lambda elem : elem[1] == 0) # IDs(channels) having zero credit (value)
        M_dummy = M[:,list(newDict.keys())] # Matrix consists of IDs(channels) with zero credit (value)
        dummy_ID = np.unique(np.where(M_dummy > 0)[0]) 
        dummy_sum = total_conversion[dummy_ID].sum()
        print("Dummy sum : {}".format(dummy_sum))
        
        if dummy_sum == 0:
            return True
        else:
            raise ValueError('''
            Sum of Dummy Players equals 0. Channels did not contribute any value could not have Shaple value greater than 0.
            Find : Sum of Dummy Players : {}
            '''.format(dummy_sum))