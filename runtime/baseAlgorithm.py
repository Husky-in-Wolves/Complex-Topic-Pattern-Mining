
'''***1***find all the possible topic in S_alpha record in E (default: there is no same topic)'''
def findTopic(LDA_list,S,alpha):
    E = {}
    prov_topic = [] if len(alpha)==0 else alpha
    for i in S.keys():
        time_list=S[i]
        lda_list=set([int(topic) for time_ in time_list for topic in LDA_list[time_] if int(topic) not in prov_topic])
        for topic in lda_list:
            if topic not in E.keys():
                E[topic]=0
            E[topic]+=1
    E=set([key for key in E if E[key]>=2])
    return sorted(list(E))


'''***2*** find all the dicuments as instances of z record as <j,pj,tj>, which represent truple(pos,prob,tim)'''
def findInstanceList(LDA_list,Prob_list,S_i,z):
    InstanceList=[]
    for pos,time_ in enumerate(sorted(S_i)):
        if z in LDA_list[time_]:
            ind = LDA_list[time_].index(z)
            prob=Prob_list[time_][ind]
            InstanceList.append([pos,prob,time_])
    if len(InstanceList):
        InstanceList = sorted(InstanceList, key=lambda item: item[0])
    return InstanceList


'''***3***find all the prefix which can be merged; Prefix_STP in myClass'''
def findR_STP(R_beta_i, max_time):
    list_ = list(filter(lambda item:item.time < max_time, R_beta_i))
    list_ = sorted(list_, key=lambda item:item.time)
    p = list_[-1].prob if len(list_) > 0 else 0.0
    return p
'''***3'***find all the prefix which can be merged; Prefix_CTP in myClass'''
def findR_CTP(R_alpha_i, min_time, max_time):
    list_=list(filter(lambda item:item.time_start >= min_time and item.time_end < max_time, R_alpha_i))
    if len(list_) <= 0:
        return 0.0
    else:
        min_start = min([item.time_start for item in list_])
        max_end = max([item.time_end for item in list_])
        targets = list(filter(lambda i:i.time_start<=min_start and i.time_end>=max_end, list_))
        try:
            return targets[0].prob
        except:
            for x in list_:
                print(x.time_start, x.time_end)
            exit(0)

