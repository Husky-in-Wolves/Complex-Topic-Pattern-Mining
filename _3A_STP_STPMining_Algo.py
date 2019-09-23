import myClass as STUC
import numpy as np
import math, os, multiprocessing


ROOT = "new-data/russian/2016/"
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

'''***3***find all the prefix which can be merged; Prefix_STP in myClass'''
def findR_STP(R_beta_i, max_time):
    list_ = list(filter(lambda item:item.time < max_time, R_beta_i))
    list_ = sorted(list_, key=lambda item:item.time)
    p = list_[-1].prob if len(list_) > 0 else 0.0
    return p




def UpsSTP(uid,alpha,S_key,R_alpha,S_alpha,STP_SUPP_list,min_Count):
    S_len = len(S_key)
    E = findTopic(LDA_dict[uid], S_alpha, alpha) # find all the possible topic in S_alpha record in E
    for z in E:
        # ______________________Initialization_______________________________________
        '''beta is the new pattern'''
        beta=alpha.copy(); beta.append(int(z)); beta_len=len(beta)
        '''S_beta is the suffix set; R_beta is the ; Supp_beta is the ;'''
        S_beta, R_beta, Supp_beta={}, {i: [] for i in S_alpha.keys()}, {}
        # ______________________Initialization______________________________________
        '''i represents the index of session in the list'''
        for i in list(S_alpha.keys()):
            InstanceList = findInstanceList(LDA_dict[uid], Prob_dict[uid], S_alpha[i], z)
            '''P is the occurrence probability in each session, p_j2 recaod the last probability'''
            P, p_j2 = 0, 0
            '''J is a message set.  j[0]=pos,j[1]=prob,j[-1]=time'''
            for k, mes_end in enumerate(InstanceList):
                '''if beta is the first topic p_star=1, else p_star=findR(R_alpha[i],j)'''
                p_star = 1.0 if beta_len-1 <=0 else findR_STP(R_alpha[i],mes_end[-1])
                P = mes_end[1] * p_star + (1 - mes_end[1]) * p_j2
                p_j2 = P
                if P > 0.0:
                    R_beta[i].append(STUC.Prefix_STP(tau=-1, pos=mes_end[0], prob=P, time=mes_end[-1]))
            if P > 0.0:
                Supp_beta[i] = P
            if P > 0.0 and InstanceList[0][0] + 1 < len(S_alpha[i]):
                S_beta[i] = S_alpha[i][InstanceList[0][0] + 1:]
        #_______________result_and_interial__________________________________________
        '''filter out patterns with support equal to 0 and limit pattern to between 2 and 4'''
        if beta_len >= 2 and len(S_beta.keys()) >= min_Count:
            support = math.pow(sum(Supp_beta.values()) / S_len, 1 / beta_len)
            prob_list = [0.0 if key not in Supp_beta.keys() else Supp_beta[key] for key in S_key]
            STP_SUPP_list.append(STUC.STP_Supp(ldaStr=tuple(beta), tau=-1, prob_list=prob_list, supp=support, l=beta_len, contain=tuple([tuple(beta)])))
        if beta_len < 4 and len(S_beta.keys()) >= min_Count:
            UpsSTP(uid=uid, alpha=beta, S_key=S_key, R_alpha=R_beta, S_alpha=S_beta, STP_SUPP_list=STP_SUPP_list, min_Count=min_Count)
        #_________________end___result_and_interial_________________________________


def run_oneUser(output_dir, userID, min_Count=2):
    time_list=list(LDA_dict[userID].keys())
    if len(time_list) <= 0 :
        print("error: run_oneUser timelist is empty")
        exit(0)
    global Sess_dict
    '''Session is a dict; key=sess id; value=time_list;'''
    S_alpha = Sess_dict[userID]; S_key = list(S_alpha.keys())
    '''Temp is a list, Temp[i]=myClass Temp{sessID,pos,prob,time}'''
    alpha, R_alpha, STP_Supp_list = [], {i: [] for i in S_alpha.keys()}, []
    '''The patterns with respect to the ``userID'' are retained in STP_Supp_list'''
    UpsSTP(userID, alpha, S_key, R_alpha, S_alpha, STP_Supp_list, min_Count)
    '''save the mining result'''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    np.save(output_dir + "/TP_dict_%s.npy" % (userID), STP_Supp_list)
    print("_________", userID, "_____________:", len(STP_Supp_list), "end")



if __name__ =='__main__':
    uid_list=sorted(list(Sess_dict.keys()))
    output_dir = os.path.join(ROOT, "User/STP")
    pool = multiprocessing.Pool(min([multiprocessing.cpu_count(),4]))

    for uid in uid_list:
        print(uid)
        pool.apply_async(run_oneUser, (output_dir, uid,))
    pool.close()
    pool.join()

    '''
    #不使用多进程，纯串行执行
    for uid in uid_list:
        run_oneUser(uid)
    '''