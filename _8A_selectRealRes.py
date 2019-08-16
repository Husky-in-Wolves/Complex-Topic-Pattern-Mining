import numpy

def list2str(valid,PHI_hss_set):
    RES=[]
    for (uid,stp, para) in valid:
        if stp[0] in PHI_hss_set:
            string=[str(uid),str(stp[0]),stp[1],str(stp[-1]),para[0],para[1],para[2],para[-1]]
            RES.append(string)
    return RES


'''PHI_set is list ,PHI_set.append((new_PHI[pos],[supp_mat[i][pos], supp_list[pos], AR_mat[i][pos], RR_mat[i][pos]]))
new_PHI[pos]=[ldaStr,ldalen,contain]; contain=(alpha.ldaStr,alpha.contain)'''
def selected(num,PHI_set,PHI_hss_set):
    unValid=[(uid,stp,para) for (uid,stp,para) in PHI_set if len(stp[-1])<num and len(stp[-1])==1]
    valid=set(PHI_set)-set(unValid)

    print("len: ",len(PHI_set),len(valid),len(unValid))

    dict_={}
    for (uid,stp,para) in unValid:
        contain=stp[-1];length=stp[1];ldaStr=stp[0]
        if uid not in dict_.keys():
            dict_[uid]={}
        if (length,contain) not in dict_[uid].keys():
            dict_[uid][(length,contain)]=[]
        dict_[uid][(length,contain)].append((ldaStr,para))

    '''需要用PHI_hss_set筛选'''
    valid=set([(uid,stp,para) for (uid,stp,para) in valid if stp[0] in PHI_hss_set])
    '''恢复有效模式'''
    for uid in dict_.keys():
        for (length,contain) in dict_[uid].keys():
            list_ = dict_[uid][(length,contain)]
            '''该简单模式并无可以合并的模式，所有复杂模式都是假的'''
            if len(list_) == int(length - num + 1):
                max_para = [-1]*4
                for (ldaStr,para) in list_:
                    if para[-1] > max_para[-1] and ldaStr in PHI_hss_set:
                        max_para = para
                if max_para != [-1]*4:
                    new_contain=contain[0][-1]; new_lda=contain[0][0]
                    new_stp=(new_lda,length,new_contain)
                    print("TRUE: ", new_stp)
                    valid.add((uid,new_stp, max_para))
    '''输出'''
    RES = []
    for (uid, stp, para) in valid:
        #uid,
        string = [str(uid), str(stp[0]), stp[1], str(stp[-1]), para[0], para[1], para[2], para[-1]]
        RES.append(string)

    return RES












