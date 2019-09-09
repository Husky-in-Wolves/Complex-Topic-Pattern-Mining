import _3_myClass as STUC
import numpy as np
import math, os

'''ROOT is the file dir of dataset'''
ROOT="new-data-syn-3/"

Sess_dict=np.load(ROOT+"Sess_dict.npy").item(0) #Sess_dict[user id][sess id]=time_list
LDA_dict=np.load(ROOT+"LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load(ROOT+"Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list



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


'''***3'***find all the prefix which can be merged; Prefix_CTP in myClass'''
def findR_CTP(R_alpha_i, min_time, max_time, tau):
    list_=list(filter(lambda item:item.tau==tau and item.time_start >= min_time and item.time_end < max_time, R_alpha_i))
    if len(list_) <= 0:
        return 0.0
    else:
        min_start = min([item.time_start for item in list_])
        max_end = max([item.time_end for item in list_])
        targets = list(filter(lambda i:i.time_start<=min_start and i.time_end>=max_end, list_))
        return targets[0].prob


def TICTP(uid,alpha,S_len,R_alpha,S_alpha,STP_SUPP_list,min_Count,TI=STUC.TI):
    E=findTopic(LDA_dict[uid], S_alpha, alpha)  #***1***find all the possible topic in S_alpha record in E
    for z in E:
        # _____________________init_______________________________
        beta=alpha.copy(); beta.append(int(z)); beta_len=len(beta)
        S_beta, R_beta, Supp_beta = {}, {i: [] for i in S_alpha.keys()}, {tau:{} for tau in TI}
        # _____________________init__________________________________

        for i in list(S_alpha.keys()):
            '''InstanceList is a message list.  item[0]=pos,item[1]=prob,item[-1]=time'''
            InstanceList = findInstanceList(LDA_dict[uid], Prob_dict[uid], S_alpha[i], z)
            for tau in TI:
                P_beta = 0
                for j, mes_start in enumerate(InstanceList):
                    IList_ = InstanceList[j:] if j == 0 else [item for index, item in enumerate(InstanceList) if index >= j and item[-1] <= mes_start[-1] + tau]
                    p_j2, P = 0, 0
                    for k, mes_end in enumerate(IList_):
                        '''if alpha is the first topic p_star=1, else p_star=findR(R_alpha[i],j)'''
                        p_star = 1.0 if len(alpha) <= 0 else findR_CTP(R_alpha[i], tau=tau, min_time=mes_end[-1] - tau, max_time=mes_end[-1])
                        P = float(mes_end[1]) * p_star + float(1 - mes_end[1]) * p_j2
                        p_j2 = P
                        if P > 0.0:
                            R_beta[i].append(STUC.Prefix_CTP(tau=tau, time_start=mes_start[-1], time_end=mes_end[-1], prob=P))
                    if j == 0 and len(IList_) == len(InstanceList) and P > 0.0:
                        P_beta = P
                if P_beta > 0.0:
                    Supp_beta[tau][i] = math.pow(P_beta, 1 / beta_len)
            if len(InstanceList) and InstanceList[0][0] + 1 < len(S_alpha[i]):
                S_beta[i] = S_alpha[i][InstanceList[0][0]+1:]

        #_______________result_and_interial__________________________________________
        '''filter out patterns with support equal to 0 and limit pattern to between 2 and 4'''
        if beta_len >=2:
            for tau in TI:
                if len(Supp_beta[tau].values()) >= min_Count:
                    support = sum(Supp_beta[tau].values()) / S_len
                    STP_SUPP_list.append(STUC.STP_Supp(ldaStr=tuple(beta), tau=tau, prob_list=Supp_beta, supp=support, l=beta_len, contain=tuple([tuple(beta)])))
        if beta_len < 4 and max([len(Supp_beta[tau].values()) for tau in TI]) >= min_Count:
            TICTP(uid=uid, alpha=beta, S_len=S_len, R_alpha=R_beta, S_alpha=S_beta, STP_SUPP_list=STP_SUPP_list,min_Count=min_Count)
        #_________________end___result_and_interial_________________________________


def run_oneUser(userID, min_Count=1):
    time_list=list(LDA_dict[userID].keys())
    if len(time_list) <= 0 :
        print("error: run_oneUser_TUSTP timelist is empty",userID)
        exit(0)
    global Sess_dict
    '''Session is a dict; key=sess id; value=time_list;'''
    S_alpha = Sess_dict[userID]; S_len = len(S_alpha)
    '''Temp is a list, Temp[i]=myClass Temp{sessID,pos,prob,time}'''
    alpha, R_alpha, STP_Supp_list = [], {i: [] for i in S_alpha.keys()}, []
    '''The patterns with respect to the ``userID'' are retained in STP_Supp_list'''
    TICTP(userID, alpha, S_len, R_alpha, S_alpha, STP_Supp_list, min_Count=min_Count)
    '''save the mining result'''
    if not os.path.exists(os.path.join(ROOT, "User_TISTP")):
        os.makedirs(os.path.join(ROOT, "User_TISTP"))
    np.save(os.path.join(ROOT, "User_TISTP") + "/STPSUPP_dict_%s.npy" % (userID), STP_Supp_list)
    print("_________", userID, "_____________:",len(STP_Supp_list), "end")


if __name__ =='__main__':
    uid_list=sorted(list(Sess_dict.keys()))
    uid_list.reverse()

    '''Using multi-process concurrent execution (one process per user)'''
    import multiprocessing
    pool = multiprocessing.Pool(min([multiprocessing.cpu_count(),3]))
    for uid in uid_list:
        pool.apply_async(run_oneUser, (uid,))
    pool.close()
    pool.join()

    '''
    for uid in uid_list:
        run_oneUser(uid)
    '''