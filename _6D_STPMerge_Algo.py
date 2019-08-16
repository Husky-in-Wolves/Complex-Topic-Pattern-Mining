import numpy as np
import time,multiprocessing,os,math
import _3A_UpsSTP_dataStruc as A3_STUC
import _7B_MultiSTPSupp_Algo as B7

TI=A3_STUC.TI
CORE = int(multiprocessing.cpu_count()-2)


#stp is a list
def get_sub_STP(tau_user_stp_supp,i):
    sub=[stp for stp in set(tau_user_stp_supp) if stp.len == i]
    return sub
def findBylda(list_,lda,cnttau):
    for x,l in enumerate(list_):
        if tuple(l.ldaStr)==tuple(lda) and l.tau==cnttau:
            return True,x
    return False,-1

def perm(l):
    if(len(l)<=1):
        return [l]
    r=[]
    for i in range(len(l)):
        s=l[:i]+l[i+1:]
        p=perm(s)
        for x in p:
            r.append(l[i:i+1]+x)
    return sorted(r)

def getExactSupport(uid,cand_set,tau,length,tau_user_stp_problist):
    lda_list=[]
    for cand in cand_set: lda_list+=list(cand.contain)
    lda_list=sorted(list(set(lda_list)))
    prob_list=[]
    for lda in lda_list:
        prob=tau_user_stp_problist[lda]
        prob_list.append(prob)

    multi_supp_exact_2 = B7.get_Supp(uid, tau, length, lda_list, prob_list)
    # 计算支持度
    average = sum(multi_supp_exact_2) / len(multi_supp_exact_2)
    return average,multi_supp_exact_2

def getUsed(cand_lda_list,sub_STP_supp):
    res=[]
    for idx in range(len(sub_STP_supp)):
        beta=sub_STP_supp[idx]
        if len(set(beta.contain)-set(cand_lda_list))<=0:
            res.append(beta.ldaStr)
    return res

def cutSTP(stp,start,i):
    a=[]    #a可能包含多个元素int
    b=[]    #暂时只包含一个元素
    c=[]    #暂时只包含一个元素
    d=[]    #d可能包含多个元素
    if start - 1 >= 0:
        a.extend( stp[0:start] )
    if type(stp[start]) is list or type(stp[start]) is tuple:
        b=list(stp[start])
    else:
        b.append(stp[start])
    if type(stp[start + 1]) is list or type(stp[start + 1]) is tuple:
        c=list(stp[start + 1])
    else:
        c.append(stp[start + 1])
    if start + 2 <= i - 1:
        d.extend( stp[start + 2:i] )
    return a,b,c,d
def crateCP(alpha_a,alpha_b,alpha_c,alpha_d):
    beta_a = alpha_a
    beta_b = alpha_c
    beta_c = alpha_b
    beta_d = alpha_d
    beta=[]
    beta.extend(beta_a)
    beta.extend(beta_b)
    beta.extend(beta_c)
    beta.extend(beta_d)
    return beta

'''
按包含元素分别存储 dict[num][ldaStr]
'''
def Merge(uid,sub_STP_supp,length,cntTau,tau_user_stp_problist):
    New_STP_Supp,Phi,participate={},[],[]
    for idx in range(len(sub_STP_supp)):
        alpha=sub_STP_supp[idx]
        pattern_length = len(alpha.ldaStr)
        if pattern_length > 1:
            for start in range(0, pattern_length-1):
                '''切分字符串'''
                alpha_a, alpha_b, alpha_c, alpha_d = cutSTP(alpha.ldaStr, start, pattern_length)
                '''仅允许点事件的合并'''
                if len(alpha_b)==1 and len(alpha_c)==1:
                    '''求出元素的全排列集合'''
                    swap_set = perm(alpha_b + alpha_c)
                    '''构造复合模式该有的格式'''
                    multi_ldastr = []
                    multi_ldastr.extend(alpha_a);multi_ldastr.append(tuple(swap_set[0]));multi_ldastr.extend(alpha_d)
                    multi_ldastr = tuple(multi_ldastr)
                    '''避免重复计算'''
                    if multi_ldastr not in set(New_STP_Supp.keys()):
                        New_STP_Supp[multi_ldastr] = None
                        '''拼出候选集,'''
                        cand_set = []
                        for swap in swap_set:
                            cand = alpha_a + swap + alpha_d
                            '''find the instance of beta'''
                            flag, idy = findBylda(sub_STP_supp, cand, cntTau)
                            if flag == True and idy != -1:
                                beta = sub_STP_supp[idy]
                                cand_set.append(beta)
                            else:
                                break
                        '''如果所需元素全部存在,则视为该种复合模式存在'''
                        if len(swap_set) == len(cand_set):
                            '''计算精确支持度'''
                            # prob_mat = []
                            # for cand in cand_set:
                            #     print(np.shape(cand.prob_list))
                            #     prob_mat.append(cand.prob_list)
                            # prob_mat = np.mat(prob_mat)
                            prob_mat = np.mat([np.array(cand.prob_list) for cand in cand_set])
                            multi_supp_appro = np.array(prob_mat.max(axis=0)).tolist()[0]

                            if sum([1 for i in multi_supp_appro if i > 0]) > 1:
                                    supp, multi_supp = getExactSupport(uid, cand_set, cntTau, length,
                                                                       tau_user_stp_problist)
                            else:
                                    multi_supp = multi_supp_appro
                                    supp = sum(multi_supp) / len(multi_supp)

                            '''构造复合模式的基本信息'''
                            cand_lda_list = []
                            for cand in cand_set: cand_lda_list += list(cand.contain)
                            new_stp = A3_STUC.STP_Supp(ldaStr=multi_ldastr, tau=cntTau, prob_list=multi_supp,
                                                       supp=supp,
                                                       l=length, contain=tuple(cand_lda_list))
                            '''新模式的信息做下次合并'''
                            New_STP_Supp[multi_ldastr] = new_stp


                        else:
                            '''不存在完整组合的模式，暂时符号代替，特点是len（contain）==1'''
                            x={alpha.ldaStr:alpha.contain}
                            new_stp = A3_STUC.STP_Supp(ldaStr=multi_ldastr, tau=cntTau, prob_list=alpha.prob_list,
                                                       supp=alpha.supp, l=length, contain=tuple(list(x.items())))
                        '''新模式符合条件，保存在最终高级结果里'''
                        if len([1 for i in new_stp.prob_list if i > 0]) > 1: #2:
                            Phi.append(new_stp)
    '''保存参与合并的低级模式'''
    for idx in range(len(sub_STP_supp)):
        alpha=sub_STP_supp[idx]
        if len([1 for i in alpha.prob_list if i > 0]) >= 1:
            participate.append(alpha)
    '''返回结果'''
    New_STP_Supp_list = [item for item in New_STP_Supp.values() if item != None]
    """PHI只要满足support下限； New_STP_Supp只需要满足参与者完整； participate"""
    return Phi,New_STP_Supp_list,participate


def run_one_STPMerge(uid_list_,tau_stp_supp,cntTau):
    multi_stp_dict,Participate = {},{}
    for i,uid in enumerate(set(uid_list_)):
        if i%300==0:
            print(i,cntTau)
        tau_user_stp_supp = set(tau_stp_supp[uid])  # tau_user_stp_supp is a list
        tau_user_stp_problist=dict({item.ldaStr:item.prob_list for item in tau_user_stp_supp})
        # 按长度进行合并
        if len(tau_user_stp_supp)>0:
            maxLen = max([stp.len for stp in tau_user_stp_supp])
            if maxLen >= 3:
                for l in range(3, maxLen + 1):
                    new_STP = get_sub_STP(tau_user_stp_supp, l)
                    count=0
                    """new_STP是发现interleaving的input数据"""
                    while len(new_STP)>0 and count<1:
                        count+=1
                        '''计算'''
                        sub_STP=new_STP.copy()
                        """PHI只要满足support下限,保存着该轮结果； New_STP_Supp只需要满足参与者完整保存着下轮数据"""
                        phi,new_STP,participate = Merge(uid, sub_STP, l, cntTau, tau_user_stp_problist)
                        '''保存'''
                        if len(phi)>0:
                            '''新生成的高级模式'''
                            num = int(math.pow(2, count))
                            if num not in multi_stp_dict.keys():
                                multi_stp_dict[num] = {}
                            if uid not in multi_stp_dict[num].keys():
                                multi_stp_dict[num][uid] = []
                            multi_stp_dict[num][uid].extend(phi)
                            '''参与合并的低级模式'''
                            if num not in Participate.keys():
                                Participate[num] = {}
                            if uid not in Participate[num].keys():
                                Participate[num][uid] = []
                            Participate[num][uid].extend(participate)
    return multi_stp_dict,Participate


def run_STPMerge_banches(tau_stp_supp,cntTau):
    print("start the ", cntTau, time.time())
    uid_list = sorted(list(tau_stp_supp.keys()))
    multi_stp_dict,Participate=run_one_STPMerge(uid_list,tau_stp_supp,cntTau)
    '''保存'''
    num_list = set(multi_stp_dict.keys())
    for num in num_list:
        # 创建目录
        path1 = "new-data/CTP/" + str(num)
        if not os.path.exists(path1):
            os.makedirs(path1)
        print(path1,os.path.exists(path1))
        np.save(path1+"/STP_dict_%s.npy" % (cntTau), multi_stp_dict[num])
    for num in Participate:
        # 创建目录
        path2 = "new-data/CTP/" + str(num)+"_"
        if not os.path.exists(path2):
            os.makedirs(path2)
        print(path2,os.path.exists(path2))
        np.save(path2+"/STP_dict_%s.npy" % (cntTau), Participate[num])
    print("end the ", cntTau, time.time())



if __name__ == '__main__' :
    '''
    for tau in TI:
        # tau_stp_supp = np.load("new-data/TISTP_TI/STP_dict_%s.npy" % (tau)).item(0)
        tau_stp_supp = np.load("new-data/TISTP_TI/STP_dict_%s.npy" % (tau)).item(0)
        run_STPMerge_banches(tau_stp_supp,tau,)
'''
    import multiprocessing
    pool = multiprocessing.Pool(min(len(TI),5))

    for tau in TI:
        tau_stp_supp = np.load("new-data/TISTP_TI/STP_dict_%s.npy" % (tau)).item(0)
        pool.apply_async(run_STPMerge_banches, args=(tau_stp_supp,tau,))
        #time.sleep(3)
    pool.close()
    pool.join()
    print("finish!!!!____", time.time())
