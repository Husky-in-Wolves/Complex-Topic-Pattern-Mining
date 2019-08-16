import numpy as np
import random

'''
label_dict=np.load('new-data/label_dict.npy').item(0)
name_dict=np.load('new-data/name_dict.npy').item(0)
print(name_dict.keys())
'''


def OnlineTw_data():
    data_dict=np.load('new-data/data_dict.npy').item(0)
    index_list=list(data_dict.keys())
    for i,index in enumerate(index_list):
        if i % 500 == 0:
            num = i / 50
        time_list=list(data_dict[index].keys())
        for time in time_list:
            with open("new-data/20152016%d.text"%num, 'a') as text_file:
                text_file.write(data_dict[index][time] + '\n')
            with open("new-data/20152016%d.time"%num, 'a') as time_file:
                time_file.write(str(time) + '\n')

def createLDA():
    LDA_dict={}
    data_dict = np.load('new-data/data_dict.npy').item(0)
    index_list = list(data_dict.keys())
    for uid in index_list:
        LDA_dict[uid]={}
        time_list = list(data_dict[uid].keys())
        for time in time_list:
            #uid,time对齐，赋予LDA的编号
            LDA_dict[uid][time]=int(random.uniform(0,20))
    np.save("new-data/LDA_dict.npy",LDA_dict)

if __name__ =='__main__' :
    #OnlineTw_data()
    #createLDA()
    import nltk

    nltk.download('stopwords')
