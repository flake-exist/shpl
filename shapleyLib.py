import pandas as pd
import numpy as np
from PropertiesShapley import Properties,FilterTheDict

class Shapley:
    
    def __init__(self,data,channel_delimiter='=>',loyal=False,loyal_position=None):
        
        if (loyal==False) and (loyal_position==None):
            self.data = data
        elif (loyal==True) and isinstance(loyal_position,int) and (loyal_position > 0):
            self.data = data[data.path.str.count(channel_delimiter) > loyal_position - 1]
        else:
            raise ValueError('`loyal`:Boolean,`loyal_position`:Int | None.If `loyal`==True ,then loyal_position==Int')
           
        self.channel_delimiter = channel_delimiter   
        self.total_conversion = self.data.total_conversions.values # commited conversions corresponding channel chains
        self.total_campaign = self.data.total_conversions.sum() #total sum ov conversions
        self.chain_list = self.data.path.values #list with unique chains (paths)
            
        self.channel_dict = {} #dict for incoding channel names
        self.size = None  #number of unique chains (paths)
        self.channel_unique = None #list of unique channel names
        self.channel_size = None #size of unique channles
        self.shapley_dict = {} #decoding dict with shapley values
        
    def UniqueChainCheck(self):
        '''
        Check if `self.chain_list` contains only unique chains or not
        RETURN : [1] Boolean
        '''
        size = len(self.chain_list) # length of input list
        unique_size = len(set(self.chain_list)) # length of unique chains(paths)
        
        if size == unique_size:
            self.size = unique_size
            return True       
        else:
            raise ValueError('`self.chain_list` must contain only unique values')
            
    def ChainSplit(self,chain): return chain.split(self.channel_delimiter)
    
    
    def ChannelDict(self,channel_store):
        '''
        Create `self.channel_dict` indicating each unique channel its unique ID
        Format -> {channel_1 : ID_1,
                     ...
                     ...
                     ...
                   channel_n : ID_n}

        INPUT: [1] `channel_store` list with unique channels
        RETURN: [1] Unit
        '''

        for ID,channel in enumerate(channel_store):
            self.channel_dict[channel] = ID
    
    
    
    def UniqueChannel(self):
        '''
        Count number of unique channels in `chain_list`
        RETURN : [1] Unit
        '''

        self.UniqueChainCheck() # UDF method
        channel_store = []
        
        for chain in self.chain_list:
            channel_store.extend(self.ChainSplit(chain)) #UDF method
        channel_store = set(channel_store)
        
        self.channel_unique = channel_store #all unique channels in `self.chain_list`
        self.channel_size = len(channel_store) #size of unique channles
        
        self.ChannelDict(self.channel_unique) #UDF method                 
        
    
    def ChanneltoID(self,channel_seq): return [self.channel_dict[channel] for channel in channel_seq]
    '''
    Convert channel[s] into ID[s]
    INPURT: [1] `channel_seq` list of channels
    RETURN: [1] list of IDs (List[Int])
    '''
        
    def ZeroMatrix(self,row_num ,col_num): return np.zeros((row_num,col_num))
    '''
    Create zero matrix (size = (number of unique chains) x (number of unique channels))
    '''
    
    def Vectorization(self):
        '''
        Convert from `chain_list` format to Matrix format.Each ID in matrix is allocated to a channel (see `self.ChannelDict`)
        RETURN: [1] Matrix[Int]. If i-th chain(row) has j-th channel(ID) -> M(i,j) = 1.In case channel(ID) meets multiple
        times in chain , M ignoring it and anyway , despite of frequency channel(ID) in chain M(i,j)=1
        '''
        M = self.ZeroMatrix(self.size,self.channel_size) #create empty Matrix
        for index,chain in enumerate(self.chain_list):
            channel_seq = self.ChainSplit(chain)
            target_ID = self.ChanneltoID(channel_seq)
            M[index,target_ID] = 1
            
        return M
            
    def Calc(self,M):
        
        for i in range(M.shape[1]): # iterate by channels
            mask = M[:,i]>0 # create mask
            M_buffer = M[mask] # rows contiaining i-th channel
            channel_cardinality = M_buffer.sum(axis=1) #channel cardinality           
            conversion = self.total_conversion[mask] # conversions allocated to i-th channel
            result = np.stack((conversion, channel_cardinality), axis=-1) #
            self.shapley_dict[i] = np.array(result[:,0]/result[:,1]).sum() # 
    
    def DecodeDict(self):
        '''
        Decode `shapley_dict`, where each unique channel is incoded into unique ID to "human" string format
        Before: -> {0:val1,
                    1:val2,
                    ...,
                    ...,
                    ...,
                    N: val_N} where N - number of unique channels and val_N its values (weights)
        
        After-> {channel_name_1:val1,
                 channel_name_2:val2,
                    ...,
                    ...,
                    ...,
                 channel_name_N: val_N} where N - number of unique channels and val_N its values (weights)
        
        '''
        
        decode_dict = {}
        
        inv_channel_dict = {v: k for k, v in self.channel_dict.items()} # create invert `channel_dict
        
        for key in self.shapley_dict.keys():
            decode_dict[inv_channel_dict[key]] = self.shapley_dict[key]
            
        return decode_dict
    
    def Evaluate(self):
        
        Proper = Properties()
        
        self.UniqueChannel()
        M = self.Vectorization()
        self.Calc(M)
        decode_dict = self.DecodeDict()
        
        efficient = Proper.Efficiency(self.shapley_dict,self.total_campaign)
        dummy_players = Proper.DummyPlayer(M,self.shapley_dict,self.total_conversion)
        
        return decode_dict
    
       
    
if __name__ == '__main__':
    
    data = pd.read_csv('path_to_example_file.csv',';')
    
    shapley = Shapley(data)
    Proper = Properties()
    
    decode_dict = shapley.Evaluate()
    efficient = Proper.Efficiency(shapley.shapley_dict,shapley.total_campaign)
    dummy_players = Proper.DummyPlayer(M,shapley.shapley_dict,shapley.total_conversion)
    
#     shapley = Shapley(data)
#     shapley.UniqueChannel()
#     M = shapley.Vectorization()
#     shapley.Calc(M)
#     shapley_decode = shapley.DecodeDict()
    