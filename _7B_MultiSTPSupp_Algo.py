import numpy as np
import math

#来自于算法2生成的切割好的片段
Sess_dict=np.load("new-data/Sess_dict.npy").item(0) #Sess_dict[user id][sess id]=time_list
#来自于Twitter-LDA生成的话题及概率
LDA_dict=np.load("new-data/LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load("new-data/Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list

Inter={}

def getPrev(uid,x,pt,tau,time_list,target_list):
    if pt != -1:
        cur_time = time_list[x]
        LDA_list = LDA_dict[uid]
        time_id = [i for i, t in enumerate(time_list) if t >= pt - tau and t <= cur_time and len(set(LDA_list[t]) & set(target_list)) > 0]
        if len(time_id) > 0:
            return min(time_id)
    return -1

#index_list=[(i,index),...]; pattern_list=[(i,pattern)]
def URMultiSTP(x,pt,uid,tau,time_list,index_list,pattern_list):
    if len(index_list)<=0 or len(pattern_list)<=0:
        return 0.0
    if pt != -1 and time_list[x] + tau < pt:
        return 0.0
    if len([1 for item in index_list.values() if x < item]) > 0:  # if x < y or x < z :
        return 0.0
    if len([1 for item in index_list.values() if item < 0]) >= len(index_list.values()):#if y < 0 and z < 0:
        return 1.0
    elif len([1 for item in index_list.values() if item < 0])>0:    # y<0 or z<0
        new_index_list=dict([(item[0],item[-1])for item in index_list.items() if item[-1] >= 0])
        new_pattern_list=dict([(item[0],pattern_list[item[0]]) for item in new_index_list.items()])
        return URMultiSTP(x,pt,uid,tau,time_list,new_index_list,new_pattern_list)
    if x < 0:
        return 0.0
    '''初始化'''
    G_xyz = 0
    cur_time = time_list[x]
    target_list=dict([[item[0],item[-1][index_list[item[0]]]] for item in pattern_list.items()])
    '''重叠子问题'''
    prev = getPrev(uid, x, pt, tau, time_list, target_list)
    global Inter
    key = list(index_list.items());key.append(x);key.append(prev);key=tuple(key)
    if key in Inter.keys():
        return Inter[key]
    '''find all possible topics of x and recoed in E'''
    E = list(LDA_dict[uid][cur_time])
    E_p = list(Prob_dict[uid][cur_time])
    if sum(E_p) < 1.0:  # 如果存在被过滤的元素，需补齐
        E.append(-1)
        E_p.append(1.0 - sum(E_p))
    '''loop for topic:'''
    for i,e in enumerate(E):
        accord_list=[item[0] for item in target_list.items() if int(e)==int(item[-1])]
        if len(accord_list)<=0:#if e != alpha_y and e != beta_z:
            G_xyz += E_p[i]*URMultiSTP(x-1,pt,uid,tau,time_list,index_list,pattern_list)
        elif len(accord_list)<=len(target_list.items()):
            index_list_={}
            for item in index_list.items():
                if item[0] in accord_list:
                    index_list_[item[0]]=item[-1]-1
                else:
                    index_list_[item[0]]=item[-1]
            G_xyz += E_p[i]*URMultiSTP(x-1,cur_time,uid,tau,time_list,index_list_,pattern_list)
    Inter[key]=G_xyz
    return G_xyz

def getSubSets(items,l):
    result = [[]]
    for x in items:
        result.extend([subset + [x] for subset in result])
    res=[i for i in result if len(i)==l]
    return res

def get_Supp(user_id,tau,length,pattern_list,supp_list):
    RES = []
    user_id = int(user_id)
    S = Sess_dict[user_id]

    for i in range(len(S)):
        result = 0
        # print(len(supp_list),len(pattern_list))
        new_pattern_list = [pattern_list[j] for j, item in enumerate(supp_list) if item[i] > 0]

        if len(new_pattern_list) > 1:
            for l in range(len(new_pattern_list)):
                '''get all subsets of S with length i+1'''
                subset = getSubSets(new_pattern_list, l + 1)
                p = 0
                for ss in subset:
                    global Inter;Inter = {}
                    index_dict = dict([(j, len(item) - 1) for j, item in enumerate(ss)])
                    pattern_dict = dict([(j, item) for j, item in enumerate(ss)])
                    # def URMultiSTP(x,pt,uid,tau,time_list,index_list,pattern_list):
                    p += URMultiSTP(x=len(S[i]) - 1, pt=-1, uid=user_id, tau=tau, time_list=S[i],
                                    index_list=index_dict, pattern_list=pattern_dict)
                # print(result)
                result += math.pow(-1, l) * p
                '''
                if l == 0:
                    print(round(p, 9), round(sum([math.pow(item[i], length) for item in supp_list]), 9))
                '''
            '''算的不准的话'''
            if result > 1 or result < 0:
                result = max( [item[i] for item in supp_list] )
            else:
                result = math.pow(round(result, 9), 1 / length)
        else:
            result = max( [item[i] for item in supp_list] )

        RES.append(result)
    return RES
