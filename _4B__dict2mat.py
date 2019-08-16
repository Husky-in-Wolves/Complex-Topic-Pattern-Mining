import time, os
import numpy as np
import _3A_UpsSTP_dataStruc as A3_STUC

ROOT="new-data-russian/2018/"
Sess_dict = np.load(ROOT+"Sess_dict.npy").item(0)
TI = A3_STUC.TI


# STUC.STP_Supp(ldaStr=tuple(gamma),tau=tau,prob_list=Supp_gamma_tau[tau],supp=average,l=gamma_len,contain=tuple([tuple(gamma)]))
def getWhole_STP(uid_list, STPSUPP_dict):
    coll_stp_supp = []
    for uid in uid_list:
        if uid in STPSUPP_dict.keys():
            ldaStr_list = [(stp.ldaStr, stp.len, stp.contain) for stp in STPSUPP_dict[uid]]  # (lda,len)
            coll_stp_supp.extend(ldaStr_list)
    set_ = set(coll_stp_supp)
    dict_ = {}
    count = 0
    for key in set_:
        dict_[key] = count
        count += 1
    return dict_


def transform(uid_list, tau_stp_supp, PHI):
    uid_phi_MAT = np.zeros((len(uid_list), len(PHI)), np.float32)
    for i, uid in enumerate(uid_list):
        if uid in tau_stp_supp.keys():
            # (ldaStr=tuple(gamma), tau = tau, prob_list = Supp_gamma_tau[tau], supp = average, l = gamma_len, contain = tuple([tuple(gamma)])
            for stp in set(tau_stp_supp[uid]):
                key = (tuple(stp.ldaStr), stp.len, stp.contain)
                try:
                    index = PHI[key]
                except:
                    print(uid, key)
                else:
                    uid_phi_MAT[i][index] = stp.supp
    return uid_phi_MAT

def cal_global_supp(uid_list, tau_stp_supp, PHI):
    supp_avg_list=[0]*len(PHI)
    global_sess_num=0
    for uid in uid_list:
            # (ldaStr=tuple(gamma), tau = tau, prob_list = Supp_gamma_tau[tau], supp = average, l = gamma_len, contain = tuple([tuple(gamma)])
            for stp in tau_stp_supp[uid]:
                key = (tuple(stp.ldaStr), stp.len, stp.contain)
                try:
                    index = PHI[key]
                except:
                    print(uid, key)
                else:
                    supp_avg_list[index] += sum(stp.prob_list)
                    global_sess_num += len(stp.prob_list)
    supp_avg_list=[round(s/global_sess_num,5) for s in supp_avg_list]
    return supp_avg_list




# tanlate dict to matix
def dict2mat(tau):
    print("start mat... ", tau, time.time())
    # 原始序列
    tau_stp_supp = np.load(ROOT+"STP/STP_dict_%s.npy" % (tau)).item(0)
    uid_list = sorted(tau_stp_supp.keys())
    PHI = getWhole_STP(uid_list,tau_stp_supp)
    uid_phi_MAT = transform(uid_list,tau_stp_supp,PHI)
    supp_avg_list = cal_global_supp(uid_list,tau_stp_supp,PHI)
    np.save(ROOT+"STP/STP_MAT_%s.npy" % (tau), uid_phi_MAT)
    np.save(ROOT+"STP/global_supp_%s.npy" % (tau), supp_avg_list)
    print("end mat... ", tau, time.time())


if __name__ == '__main__':
    for tau in [3600*24]:
        dict2mat(tau)


