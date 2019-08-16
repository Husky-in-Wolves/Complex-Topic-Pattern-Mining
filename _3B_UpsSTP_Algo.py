import _3A_UpsSTP_dataStruc as STUC
import numpy as np
import itertools
import math

ROOT="new-data-russian/2016"
#来自于算法2生成的切割好的片段
Sess_dict=np.load(ROOT+"Sess_dict.npy").item(0) #Sess_dict[user id][sess id]=time_list
#来自于Twitter-LDA生成的话题及概率
LDA_dict=np.load(ROOT+"LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load(ROOT+"Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list

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
    for i in sorted(list(S_beta.keys())):
        j=S_beta[i]
        #j+1=min position
        #S[i] is a time_list
        if j+1 < len(S[i]):
            #往后找
            time_list=S[i][j+1:]
            #LDA_dict[uid][time]是一个列表，同一时刻存在多个可能的话题,
            #二层循环拉成一维数组
            lda_list=[topic for time in time_list for topic in LDA_dict[uid][time] ]#find lda by the [uid][time]
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
def findInstanceList(uid,S_i,j0,z):
    J=[]
    for pos,time in enumerate(sorted(S_i)):
        if pos>j0 and z in LDA_dict[uid][time]:
            ind = LDA_dict[uid][time].index(z)
            prob=Prob_dict[uid][time][ind]
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


def UpsSTP(uid,beta,Temp_beta,S,S_beta,STP_SUPP_list,min_Count,TI=[3600*36]):
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
        '''key:时间间隔条件   value：'''
        Supp_gamma_tau={}
        for tau in TI:
            Supp_gamma_tau[tau]=[0.0 for i in range(len(list(S.keys())))]

        COUNT = {}
        for tau in TI:
            COUNT[tau] = 0
        # ____________________init1__end____________________________________
        '''i表示session的索引号'''
        for i in sorted(list(S_beta.keys())):
            j0=S_beta[i]

            # ___________________init2__________________________________________________
            # ***2***find all the dicumenta as instances of z record as <j,pj,tj>
            J = findInstanceList(uid, S[i], j0, z)
            # J=[(pos,prob,time),...]
            if len(J):  # if J is not empty:
                S_gamma[i]=min([J_elem[0] for J_elem in J])

            # ________________init2__end________________________________________________
            for tau in TI:
                p_j2=0
                P=0

                for j in J:     # j[0]=pos,j[1]=prob,j[-1]=time
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
                    # print(Supp_gamma_tau,P)
                    Supp_gamma_tau[tau][i]+=P
                    # Supp_gamma_tau[tau][i]+= math.pow(P,1/gamma_len)
                    #用于标记带有周期性的模式
                    COUNT[tau]+=1

            #EDN FOR TAU IN TI
        #end for i in sorted(list(S_beta.keys())):
        #_______________result_and_interial__________________________________________
        #print(uid,gamma)
        '''
        过滤掉长度小于2 以及 支持度为0的模式
        '''
        if gamma_len >= 2:
            for tau in TI:
                average=sum(Supp_gamma_tau[tau]) / len(list(S.keys()))
                average = math.pow(average, 1 / gamma_len)
                if average > 0.0 and COUNT[tau] >= min_Count:
                    STP_SUPP_list.append( STUC.STP_Supp(ldaStr=tuple(gamma),tau=tau,prob_list=Supp_gamma_tau[tau],supp=average,l=gamma_len,
                                                       contain=tuple([tuple(gamma)])) )
        #控制长度在2-4之间
        if gamma_len < 4:
            UpsSTP(uid=uid, beta=gamma, Temp_beta=Temp_gamma, S=S, S_beta=S_gamma,STP_SUPP_list=STP_SUPP_list,min_Count=min_Count)
        #________end___result_and_interial__________________________________________


def run_oneUser_TISTP(userID):
    time_list=list(LDA_dict[userID].keys())
    if len(time_list) <= 0 :
        print("error: run_oneUser_TUSTP timelist is empty")
        exit(0)

    global Sess_dict
    STP_Supp_list = []
    beta = []
    Temp_beta = []          # Temp is a list, Temp[i]=class Temp{sessID,pos,prob,time}
    S = Sess_dict[userID]   # Session is a dict; key=sess id; value=time_list
    S_beta = {}             # suffix is a dict; key=sess id; value=position;
    for ind in sorted(list(S.keys())):
        S_beta[ind] = -1

    UpsSTP(userID, beta, Temp_beta, S, S_beta, STP_Supp_list,min_Count=2)
    np.save(ROOT+"User_STP_/STPSUPP_dict_%s.npy" % (userID), STP_Supp_list)
    print("_________", userID, "_____________:", len(STP_Supp_list), "end")


if __name__ =='__main__':
    uid_list=sorted(list(Sess_dict.keys()))

    #使用多进程并发执行(多用户并行)
    import multiprocessing
    pool = multiprocessing.Pool(min([multiprocessing.cpu_count(),3]))
    for uid in uid_list:
        print(uid)
        pool.apply_async(run_oneUser_TISTP, (uid,))
    pool.close()
    pool.join()


    '''
    #不使用多进程，纯串行执行
    for uid in uid_list:
        run_oneUser_TISTP(uid)
    '''