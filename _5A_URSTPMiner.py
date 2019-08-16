import numpy as np
import math,multiprocessing, time,os
import _3A_UpsSTP_dataStruc as A3_STUC
import _4A__dict2mat as A4
import _8A_selectRealRes as A8


Sess_dict=np.load("new-data/Sess_dict.npy").item(0)
TI=A3_STUC.TI



'''
此处有一个超参数hss默认为0.05, 暂时先将hss换成比例为前10%,hss=0.2
'''
def cal_scsupp(uid_list,mat_,new_PHI,hss=0.05):
    supp_sum_list=np.sum(mat_,axis=0)
    supp_avg_list=[supp/len(uid_list) for supp in supp_sum_list]

    # 按照hss筛选,如果hss表示的是比例
    threshold = sorted(supp_avg_list)[int(len(supp_avg_list) * hss)]
    '''PHI_hss is dict key=ldaStr val=index'''
    PHI_hss = {new_PHI[i]: i for i, supp in enumerate(supp_avg_list) if supp < threshold}
    PHI_hss_set =set([key[0] for key in set(PHI_hss.keys())])
    print("num of pattern", len(supp_sum_list), len(PHI_hss_set))
    return supp_avg_list,PHI_hss_set


def cal_AR_RR(uid_list, supp_mat, supp_dict,supp_avg_list,PHI_all,new_PHI):
    c,l=np.shape(supp_mat)
    AR_mat=supp_mat-np.repeat(np.array([supp_avg_list]),c,axis=0)

    #计算该用户的模式个数
    stp_list=[]
    for uid in uid_list:
        if uid in supp_dict.keys():
            stp_list.append([(tuple(stp.ldaStr),stp.len,stp.contain) for stp in supp_dict[uid]])
        else:
            stp_list.append([])
    stp_len_list = []
    whole_set=set(PHI_all.keys())
    for i,uid in enumerate(uid_list):
        sub_set=whole_set-set(stp_list[i])      #差集
        AR_mat[i, :][[PHI_all[key] for key in sub_set]] = 0.0
        #计算用户i的模式个数
        length = len(stp_list[i])
        if length == 0:
            stp_len_list.append(1)
        else:
            stp_len_list.append(length)

    # 求均值
    AR_mat=np.maximum(AR_mat, 0.0)                       # 将矩阵中小于0的数全部变成0**********
    sumAR = np.sum(AR_mat, axis=1)
    avgAR=np.divide(np.array(sumAR),np.array(stp_len_list))

    #求RR
    RR_mat=AR_mat-np.repeat(np.array([avgAR]).reshape((c,1)),l,axis=1)

    #筛选，打包，输出
    PHI_set = []
    #
    for i, uid in enumerate(uid_list):
        sub_set = set(stp_list[i])  #sub_set=set(stp_list[i])&PHI_hss_set
        index_list = [PHI_all[phi] for phi in sub_set]
        for pos in set(index_list):
            '''
            RR=RR_mat[i][pos]; AR=AR_mat[i][pos]; user_suppList=supp_list[pos]; all_suppList=supp_mat[i][pos]
            new_PHI[pos]=[ldaStr,ldalen,contain]
            '''
            # supp_user,supp_all,AR,RR
            para=[round(supp_mat[i][pos],10), round(supp_avg_list[pos],10), round(AR_mat[i][pos],10), round(RR_mat[i][pos],10)]
            x=tuple([uid,new_PHI[pos],tuple(para)])
            PHI_set.append(x)
    return PHI_set

def transform(supp_mat,tau_stp_supp):
    uid_list = sorted(tau_stp_supp.keys())
    PHI_set = []
    # 计算scsupp，并筛选F
    PHI_all = A4.getWhole_STP(tau_stp_supp)  # PHI[(lda,len)]=index
    if len(PHI_all)>0:
        # 将原字典dict进行反转得新字典new_dict
        new_PHI_all = {v: k for k, v in PHI_all.items()}  # PHI[index]=(lda,len)
        supp_avg_list, PHI_hss_set = cal_scsupp(uid_list, supp_mat, new_PHI_all)
        # 计算stp AR RR
        PHI_set = cal_AR_RR(uid_list, supp_mat, tau_stp_supp, supp_avg_list, PHI_all, new_PHI_all)
        #简化PHI_hss
    return PHI_set,PHI_hss_set


def run_one_tau(tau):
    print("start the ", tau, time.time())

    """******************简单模式计算结果*************************"""
    # 简单模式计算结果
    supp_mat = np.load("new-data/TISTP_TI/TISTP_MAT_%s.npy" % (tau))
    tau_stp_supp = np.load("new-data/TISTP_TI/TISTP_dict_%s.npy" % (tau)).item(0)
    # 计算
    PHI_set, PHI_hss_set = transform(supp_mat, tau_stp_supp)
    # 保存成可输出格式
    URSTP_set = A8.list2str(PHI_set, PHI_hss_set)
    if not os.path.exists("new-data/URSTP/0/"):
        os.makedirs("new-data/URSTP/0/")
    np.save("new-data/URSTP/0/URSTP_%s.npy" % (tau), URSTP_set)


    """******************复杂模式计算结果*************************"""
    # 复杂模式计算结果
    in_path = "new-data/Exact_STP/"
    out_path = "new-data/URSTP/"
    file_list=os.listdir(in_path)
    for file in file_list:
        print(file)
        sub_path = os.path.join(in_path, file)
        save_path = os.path.join(out_path, file)
        file_path_1 = sub_path + "/multiSTP_MAT_%s.npy" % (tau)
        file_path_2 = sub_path + "/multiSTP_dict_%s.npy" % (tau)
        if os.path.isdir(sub_path) and os.path.exists(file_path_1) and os.path.exists(file_path_2):
            supp_mat = np.load(file_path_1)
            tau_stp_supp = np.load(file_path_2).item(0)
            PHI_set, PHI_hss_set = transform(supp_mat, tau_stp_supp)
            try:
                num = int(file)
            except:
                # 保存成可输出格式
                URSTP_set = A8.list2str(PHI_set, PHI_hss_set)
            else:
                # 需要删除结果集之间的重复模式
                # 需要筛出无意义的结果
                URSTP_set = A8.selected(num, PHI_set, PHI_hss_set)
            # 保存
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            np.save(save_path + "/URSTP_%s.npy" % (tau), URSTP_set)


    print("end the ", tau, time.time())


if __name__ == '__main__':
    TI.reverse()

    for tau in TI:
        run_one_tau(tau)
    '''
    import multiprocessing
    pool = multiprocessing.Pool(len(TI))

    for tau in TI:
        pool.apply_async(run_one_tau, args=(tau,))


    pool.close()
    pool.join()
    print("finish!!!!____", time.time())
    '''

