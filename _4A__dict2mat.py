import time,os
import numpy as np
import _3A_UpsSTP_dataStruc as A3_STUC


TI=A3_STUC.TI
ROOT="new-data-russian/2018/"
Sess_dict=np.load(ROOT+"Sess_dict.npy").item(0)
# STUC.STP_Supp(ldaStr=tuple(gamma),tau=tau,prob_list=Supp_gamma_tau[tau],supp=average,l=gamma_len,contain=tuple([tuple(gamma)]))
def getWhole_STP(STPSUPP_dict):
    uid_list = sorted(STPSUPP_dict.keys())
    coll_stp_supp = []
    for uid in uid_list:
        if uid in STPSUPP_dict.keys():
            ldaStr_list=[(stp.ldaStr,stp.len,stp.contain) for stp in STPSUPP_dict[uid]]    #(lda,len)
            coll_stp_supp.extend(ldaStr_list)
    set_=set(coll_stp_supp)
    dict_={}
    count=0
    for key in set_:
        dict_[key]=count
        count+=1
    return dict_



def transform(uid_list, tau_stp_supp):
    # 合并所有STP，无视用户
    PHI = getWhole_STP(tau_stp_supp)
    uid_phi_MAT = np.zeros((len(uid_list), len(PHI)), np.float32)
    for i, uid in enumerate(uid_list):
        if uid in tau_stp_supp.keys():
            for stp in set(tau_stp_supp[uid]):
                key = (tuple(stp.ldaStr), stp.len, stp.contain)
                try:
                    index = PHI[key]
                except:
                    print(uid, key)
                else:
                    uid_phi_MAT[i][index] = stp.supp
    return uid_phi_MAT


def cal_global_supp(uid_list,mat_):
    supp_sum_list=np.sum(mat_,axis=0)
    supp_avg_list=[supp/len(uid_list) for supp in supp_sum_list]
    return supp_avg_list

#tanlate dict to matix
def dict2mat(tau):
    print("start mat... ", tau, time.time())

    # tau_stp_supp is a dict: tau_stp_supp[uid]=stp_list
    # 间隔序列
    tau_stp_supp = np.load(ROOT+"TISTP/STP_dict_%s.npy" % (tau)).item(0)
    uid_list = sorted(tau_stp_supp.keys())
    uid_phi_MAT=transform(uid_list, tau_stp_supp)
    supp_avg_list = cal_global_supp(uid_list, uid_phi_MAT)
    np.save(ROOT+"TISTP/STP_MAT_%s.npy" % (tau), uid_phi_MAT)
    np.save(ROOT+"TISTP/global_supp_%s.npy" % (tau), supp_avg_list)
    print("end mat... ", tau, time.time())

    # 交替序列
    path = ROOT+"CTP/"
    for dir in os.listdir(path):
        sub_path = os.path.join(path, dir)
        file_path = sub_path + "/STP_dict_%s.npy" % (tau)
        if os.path.isdir(sub_path) and os.path.exists(file_path):
            tau_stp_supp = np.load(file_path).item(0)
            uid_list = sorted(tau_stp_supp.keys())
            uid_phi_MAT = transform(uid_list, tau_stp_supp)
            supp_avg_list = cal_global_supp(uid_list, uid_phi_MAT)
            np.save(sub_path + "/STP_MAT_%s.npy" % (tau), uid_phi_MAT)
            np.save(sub_path + "/global_supp_%s.npy" % (tau), supp_avg_list)



if __name__ == '__main__':
    '''
    for tau in TI:
        dict2mat(tau)
    '''
    import multiprocessing
    pool = multiprocessing.Pool(len(TI))
    for tau in TI:
        pool.apply_async(dict2mat, args=(tau,))
    pool.close()
    pool.join()

