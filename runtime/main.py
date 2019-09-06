import runtime.myClass as myClass
import runtime.baseAlgorithm as baseAlg
import numpy as np
import math, time, os



STP_Supp_list=[]
LDA_dict, Prob_dict, Sess_dict = {},{},{}
tau=5



def UpsSTP(uid,alpha,S_len,R_alpha,S_alpha,STP_SUPP_list):
    E = baseAlg.findTopic(LDA_dict[uid], S_alpha, alpha) # find all the possible topic in S_alpha record in E
    for z in E:
        # ______________________Initialization_______________________________________
        '''beta is the new pattern'''
        beta=alpha.copy(); beta.append(int(z)); beta_len=len(beta)
        '''S_beta is the suffix set; R_beta is the ; Supp_beta is the ;'''
        S_beta, R_beta, Supp_beta={}, {i: [] for i in S_alpha.keys()}, {}
        # ______________________Initialization______________________________________
        '''i represents the index of session in the list'''
        for i in list(S_alpha.keys()):
            InstanceList = baseAlg.findInstanceList(LDA_dict[uid], Prob_dict[uid], S_alpha[i], z)
            '''P is the occurrence probability in each session, p_j2 recaod the last probability'''
            P, p_j2 = 0, 0
            '''J is a message set.  j[0]=pos,j[1]=prob,j[-1]=time'''
            for k, mes_end in enumerate(InstanceList):
                '''if beta is the first topic p_star=1, else p_star=findR(R_alpha[i],j)'''
                p_star = 1.0 if beta_len-1 <=0 else baseAlg.findR_STP(R_alpha[i],mes_end[-1])
                P = mes_end[1] * p_star + (1 - mes_end[1]) * p_j2
                p_j2 = P
                if P > 0.0:
                    R_beta[i].append(myClass.Prefix_STP(tau=-1, pos=mes_end[0], prob=P, time=mes_end[-1]))
            if P > 0.0:
                Supp_beta[i] = P
            if P > 0.0 and InstanceList[0][0] + 1 < len(S_alpha[i]):
                S_beta[i] = S_alpha[i][InstanceList[0][0] + 1:]
        #_______________result_and_interial__________________________________________
        '''filter out patterns with support equal to 0 and limit pattern to between 2 and 4'''
        if beta_len >= 2 and len(S_beta.keys()) >= 2:
            support = sum(Supp_beta.values()) / S_len
            # STP_SUPP_list.append(myClass.STP_Supp(ldaStr=tuple(beta), tau=tau, prob_list=Supp_beta[tau], supp=support, l=beta_len, contain=tuple([tuple(beta)])))
        if beta_len < 4 and len(S_beta.keys()) >= 2:
            UpsSTP(uid=uid, alpha=beta, S_len=S_len, R_alpha=R_beta, S_alpha=S_beta, STP_SUPP_list=STP_SUPP_list)
        #_________________end___result_and_interial_________________________________


def TICTP(uid,alpha,S_len,R_alpha,S_alpha,STP_SUPP_list):
    E=baseAlg.findTopic(LDA_dict[uid], S_alpha, alpha)
    for z in E:
        # _____________________init_______________________________
        beta=alpha.copy(); beta.append(int(z)); beta_len=len(beta)
        S_beta, R_beta, Supp_beta ={}, {i: [] for i in S_alpha.keys()}, {}
        # ____________________init____________________________________
        for i in list(S_alpha.keys()):
            '''InstanceList is a message list.  item[0]=pos,item[1]=prob,item[-1]=time'''
            InstanceList = baseAlg.findInstanceList(LDA_dict[uid], Prob_dict[uid], S_alpha[i], z)
            P_beta=0
            for j, mes_start in enumerate(InstanceList):
                IList_ = InstanceList[j:] if j==0 else [item for index, item in enumerate(InstanceList) if index >= j and item[-1] <= mes_start[-1] + tau]
                p_j2, P = 0, 0
                for k, mes_end in enumerate(IList_):
                    '''if alpha is the first topic p_star=1, else p_star=findR(R_alpha[i],j)'''
                    p_star = 1.0 if len(alpha) <= 0 else baseAlg.findR_CTP(R_alpha[i], min_time=mes_end[-1]-tau, max_time=mes_end[-1])
                    P = float(mes_end[1]) * p_star + float(1 - mes_end[1]) * p_j2
                    p_j2 = P
                    if P > 0.0:
                        R_beta[i].append(myClass.Prefix_CTP(tau=tau, time_start=mes_start[-1], time_end=mes_end[-1], prob=P))
                if j == 0 and len(IList_)==len(InstanceList) and P > 0.0:
                    P_beta=P
            if P_beta > 0.0:
                Supp_beta[i] = math.pow(P_beta, 1 / beta_len)
            if  P_beta > 0.0 and InstanceList[0][0] + 1 < len(S_alpha[i]):
                S_beta[i] = S_alpha[i][InstanceList[0][0]+1:]
        #_________________result_and_interial__________________________________________
        '''filter out patterns with support equal to 0 and limit pattern to between 2 and 4'''
        # if beta_len >= 2 and
        if len(S_beta.keys()) >= 2:
            support = sum(Supp_beta.values()) / S_len
            # STP_SUPP_list.append(myClass.STP_Supp(ldaStr=tuple(beta), tau=tau, prob_list=Supp_beta, supp=support, l=beta_len,contain=tuple([tuple(beta)])))
        if beta_len < 4 and len(S_beta.keys()) >= 2:
            TICTP(uid=uid, alpha=beta, S_len=S_len, R_alpha=R_beta, S_alpha=S_beta, STP_SUPP_list=STP_SUPP_list)
        #_________________end___result_and_interial_________________________________


def TIDFS(userID, alpha, S_len, R_alpha, S_alpha, STP_SUPP_list):
    E = baseAlg.findTopic(LDA_dict[uid], S_alpha, alpha)
    for z in E:
        # _________________________init1___________________________________
        beta = alpha.copy(); beta.append(int(z)); beta_len = len(beta)
        S_beta, R_beta, Supp_beta = {}, {i: [] for i in S_alpha.keys()}, {}
        # ____________________init1__end____________________________________
        for i in sorted(S_alpha.keys()):
            ''' Naive depth-first search calculates probability values recursively '''
            P_beta = DFS_Traverse(userID, S_alpha[i], beta, min(S_alpha[i]), max(S_alpha[i])+1)
            if P_beta > 0.0:
                Supp_beta[i] = math.pow(P_beta, 1 / beta_len)
                S_beta[i] = S_alpha[i]
        # _________________result_and_interial__________________________________________
        '''filter out patterns with support equal to 0 and limit pattern to between 2 and 4'''
        if beta_len >= 2 and len(S_beta.keys()) >= 2:
            support = sum(Supp_beta.values()) / S_len
            # STP_SUPP_list.append(myClass.STP_Supp(ldaStr=tuple(beta), tau=tau, prob_list=Supp_beta, supp=support, l=beta_len,contain=tuple([tuple(beta)])))
        if beta_len < 4 and len(S_beta.keys()) >= 2:
            TIDFS(userID=userID, alpha=beta,S_len=S_len,R_alpha={},S_alpha=S_beta,STP_SUPP_list=STP_SUPP_list)
        # _________________result_and_interial__________________________________________

def DFS_Traverse(uid, S_i, beta, min_time, max_time, ):
    z = beta[-1]; alpha = beta[0:-1]; alpha_len = len(alpha)
    sub_S_i = sorted(list(filter(lambda i: i >= min_time and i < max_time, S_i)))
    if len(sub_S_i) <= 0:
        return 0.0
    '''InstanceList is a message list.  item[0]=pos,item[1]=prob,item[-1]=time'''
    InstanceList = baseAlg.findInstanceList(LDA_dict[uid], Prob_dict[uid], sub_S_i, z)
    p_j2, P = 0.0, 0.0
    for mes in InstanceList:
        p_star = 1.0 if alpha_len <= 0 else DFS_Traverse(uid, S_i, alpha, mes[-1]-tau, mes[-1])
        P = float(mes[1]) * p_star + float(1 - mes[1]) * p_j2
        p_j2=P
    return P





def run_oneUser(dir_, userID, algorithm=UpsSTP):
    time_list=list(LDA_dict[userID].keys())
    if len(time_list) <= 0 :
        print("error: run_oneUser_TUSTP timelist is empty")
    else:
        global Sess_dict
        '''Session is a dict; key=sess id; value=time_list;'''
        S = Sess_dict[userID]
        S_len=len(S)
        '''Temp is a list, Temp[i]=myClass Temp{sessID,pos,prob,time}'''
        alpha, R_alpha, STP_Supp_list = [], {i:[] for i in S.keys()}, []
        ''' The algorithm for mining topic pattern is one of three candidates '''
        algorithm(userID, alpha,S_len, R_alpha, S, STP_Supp_list)
        '''only record the calculation time, omitting the steps to save the data '''
        # if not os.path.exists(os.path.join("new-data/", dir_)):
        #     os.makedirs(os.path.join("new-data/", dir_))
        # np.save(os.path.join("new-data/", dir_)+"/STPSUPP_dict_%s.npy" % (userID), STP_Supp_list)


if __name__ =='__main__':
    ''' There are 3 methods for mining sequential topic patterns, 
    the former is for no time-interval constraint, 
    and the last two are for time-interval constraints.(tau=5) '''

    Algorithm = [UpsSTP, TICTP, TIDFS]
    print("*** The algorithm for mining topic pattern is %s" % (str(TIDFS)),"***")
    root_="data/"
    file_list=os.listdir(root_)
    for dir_ in file_list:
        LDA_dict = np.load(root_ + dir_ + "/LDA_dict.npy").item(0)  # LDA_dict[user id][time]=[LDA id,...] list
        Prob_dict = np.load(root_ + dir_ + "/Prob_dict.npy").item(0)  # Prob_dict[user id][time]=[prob,...] list
        Sess_dict = np.load(root_ + dir_ + "/Sess_dict.npy").item(0)  # Sess_dict[user id][sess id]=time_list
        uid_list = sorted(list(Sess_dict.keys()))

        # serial execution
        start_time = time.time()
        for uid in uid_list:
            run_oneUser(dir_, uid, algorithm=TIDFS)
        end_time = time.time()
        print(dir_, (end_time - start_time) / len(uid_list))