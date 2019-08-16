import A3_UpsSTP_dataStruc as STUC
import numpy as np
import itertools
import math


#来自于算法2生成的切割好的片段Sess_dict[user id][sess id]=time_list
Sess_dict=np.load("new-data/Sess_dict.npy").item(0)
#来自于Twitter-LDA生成的话题及概率
LDA_dict=np.load("new-data/LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load("new-data/Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list

#the finial result
STPSUPP_dict={}
STP_Supp_list=[]


#***1***find all the possible topic in S_beta record in E
#default there is no same topic
def findTopic(uid,S,S_beta,beta):
    #beta是整形数组，保存的是话题号
    if len(beta)==0:
        prov_topic=[]
    else:
        prov_topic=beta

    #topices save in a list
    E=[]
    for sid in sorted(list(S_beta.keys())):
        j=S_beta[sid]
        #j+1=min position
        #S[i] is a time_list
        if j+1 < len(S[sid]):
            #往后找
            time_list=S[sid][j+1:]
            #LDA_dict[uid][time]是一个列表，同一时刻存在多个可能的话题,
            #二层循环拉成一维数组
            lda_list=[topic for time in time_list for topic in LDA_dict[uid][sid][time] ]#find lda by the [uid][time]

            #无重复
            lda_list=[lda for lda in lda_list if int(lda) not in prov_topic]

            E.extend(lda_list)

    #distincted
    E=set(E)
    #print("findTopic :",E)
    return sorted(list(E))

#***2***find all the dicuments as instances of z record as <j,pj,tj>
#已知z 要找到z的信息（pos,prob,time）
#LDA_dict[uid][time]是一个列表，存放可能存在的话题
def findInstanceList(uid,S_i,sid,j0,z):
    J=[]
    for pos,time in enumerate(sorted(S_i)):
        if pos>j0 and z in LDA_dict[uid][sid][time]:
            ind = LDA_dict[uid][sid][time].index(z)
            prob=Prob_dict[uid][sid][time][ind]
            J.append((pos,prob,time))
    #print("findInstance: ",J)
    return J

#***3***find all the prefix which can be merge record in K ; Temp{sessID,pos,prob,time}
#已知:i,  tau,    j=<posj,pj,tj>,
# 求:k,    p,
def findTemp(Temp_beta,i,j,tau):
    K=[]
    Temp_beta_i=[temp for temp in Temp_beta if temp.sessID==i and temp.pos<j[0] and temp.tau==tau and j[-1]-temp.time<=tau]
    if len(Temp_beta_i):
        K=sorted(Temp_beta_i,key=lambda temp:temp.pos)
    return K
'''
#***4***find instance tdk in session Si base on the location k to get the origina
def getOrigProb(S_i,k,uid):
    if k >= len(S_i):
        print("error_getOrigProb!!!")
        exit(0)

    time=sorted(S_i)[k]
    #Prob_dict[uid][time]是一个列表，还需要在列表中找到话题的概率
    prob = Prob_dict[uid][time]
    return prob
'''
'''
S=Sess_dict[uid] is a dict; S[i] is a dict; key=i value=time list
S_beta is a dict; key=i value=position
'''

'''人工判定包含假币犯罪的话题'''


def UpsSTP(uid,beta,Temp_beta,S,S_beta,STP_SUPP_list,TI=STUC.TI):
    #print("strat: ",beta)
    #***1***find all the possible topic in S_beta record in E
    E=findTopic(uid, S, S_beta,beta)
    for z in E:
        # _____________________init1_______________________________改动gamma是整形数组
        gamma=beta.copy()
        gamma.append(int(z))

        gamma_len=len(gamma)

        S_gamma={}
        Temp_gamma=[]

        Supp_gamma_tau={}
        for tau in TI:
            Supp_gamma_tau[tau]=0

        COUNT = {}
        for tau in TI:
            COUNT[tau] = 0
        # ____________________init1__end____________________________________

        for i in sorted(list(S_beta.keys())):
            j0=S_beta[i]

            # ___________________init2__________________________________________________
            # ***2***find all the dicumenta as instances of z record as <j,pj,tj>
            J = findInstanceList(uid, S[i], i, j0, z)
            # J=[(pos,prob,time),...]
            if len(J):  # if J is not empty:
                S_gamma[i]=min([J_elem[0] for J_elem in J])

            # ________________init2__end________________________________________________
            for tau in TI:
                p_j2=0
                P=0

                for j in J:
                    #j[0]=pos,j[1]=prob,j[-1]=time

                    #_____if gamma_is_not_the_first_topic______________________________________________________
                    if len(Temp_beta):  #if Temp_beta is not empty
                        #***3***find all the temp(sorted) which can be merge record in K
                        K=findTemp(Temp_beta,i,j,tau)

                        #   开始合并满足时间要求的上一个字符,合并之后的概率为p_k2
                        p_k2 = 0
                        p_star = 0

                        for k in K:     # K is a temp_list:<id,tau,pos,prob,time>
                            #***4***find instance tdk in session Si base on the location k to get the original prob of k
                            #Temp add a oriProb
                            p_k_orig=k.oriProb
                            p_star = k.prob+(1-p_k_orig)*p_k2
                            p_k2=p_star
                        #   合并完成

                        P = j[1]*p_star+(1-j[1])*p_j2
                        Temp_gamma.append(STUC.Temp(i=i,tau=tau,pos=j[0],prob=j[1]*p_star,time=j[-1],oriProb=j[1]))
                    # ____endif___gamma_is_not_the_first_topic______________________________

                    # _______if gamma_is__the_first_topic______________________________
                    else:   #if Temp_beta is empty
                        P = j[1] + (1 - j[1]) * p_j2
                        Temp_gamma.append(STUC.Temp(i=i, tau=tau, pos=j[0], prob=j[1], time=j[-1],oriProb=j[1]))
                    # ____endif___gamma_is__the_first_topic______________________________

                    p_j2=P
                #end for j in J

                #此处P是每个session中的概率
                if P > 0.0:
                    # Supp_gamma_tau[tau]+=P
                    Supp_gamma_tau[tau]+= math.pow(P,1/gamma_len)
                    #用于标记带有周期性的模式
                    COUNT[tau]+=1

            #EDN FOR TAU IN TI
        #end for i in sorted(list(S_beta.keys())):

        #_______________result_and_interial__________________________________________
        #print(uid,gamma)
        '''
        过滤掉长度小于2 以及 支持度为0的模式, 过滤掉不与假币犯罪有关的模式
        '''
        #print(set(gamma),set(crime))
        if gamma_len >= 2 and len(set(gamma)&set([5,15]))<=0:
            for tau in TI:
                if Supp_gamma_tau[tau] > 0.0 and COUNT[tau] > 1:
                    Supp_gamma_tau[tau] /= (len(list(S.keys())))
                    STP_SUPP_list.append(STUC.STP_Supp(ldaStr=tuple(gamma),tau=tau,supp=Supp_gamma_tau[tau],l=gamma_len))
        #控制长度在2-4之间
        if gamma_len < 4:
            UpsSTP(uid=uid, beta=gamma, Temp_beta=Temp_gamma, S=S, S_beta=S_gamma,STP_SUPP_list=STP_SUPP_list)
        #________end___result_and_interial__________________________________________


def run_oneUser_TISTP(userID):
    STP_Supp_list = []

    time_list=list(LDA_dict[userID].keys())
    if len(time_list) <= 0 :
        print("error: run_oneUser_TUSTP timelist is empty")
    else:
        global Sess_dict

        beta = []
        # Temp is a list, Temp[i]=class Temp{sessID,pos,prob,time}
        Temp_beta = []
        # Session is a dict; key=sess id; value=time_list
        S = Sess_dict[userID]
        # suffix is a dict; key=sess id; value=position;
        S_beta = {}

        for ind in sorted(list(S.keys())):
            S_beta[ind] = -1

        # 结果都保留在了STP_Supp_list里面
        UpsSTP(userID, beta, Temp_beta, S, S_beta, STP_Supp_list)

    print("_________", userID, "_____________:", len(STP_Supp_list))
    # 将所有user的STP_SUPP存储在一个dict中
    # STPSUPP_dict[uid] = STP_Supp_list
    np.save("new-data/TISTP_User/STPSUPP_dict_%s.npy" % (userID), STP_Supp_list)



if __name__ =='__main__':
    uid_list=sorted(list(Sess_dict.keys()))
    '''
    #使用多进程并发执行(多用户并行)
    import multiprocessing
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for uid in uid_list:
        print(uid)
        pool.apply_async(run_oneUser_TISTP, (uid,))
    pool.close()
    pool.join()


    '''
    #不使用多进程，纯串行执行
    for uid in uid_list:
        run_oneUser_TISTP(uid)
