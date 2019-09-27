import math, multiprocessing, time, os, numpy as np
import myClass as STUC
import _4_file2dict2mat as A4



ROOT = "new-data/russian/2016/"
Sess_dict = np.load(ROOT + "Sess_dict.npy").item(0)
TI = STUC.TI



def phi2str(PHI_hss_set):
    RES=[]
    for phi in PHI_hss_set:
        string=[str(phi[0]),str(phi[1][0]),str(phi[1][1]),str(phi[1][-1]),phi[-1][0],phi[-1][1],phi[-1][-2],phi[-1][-1]]
        RES.append(string)
    return RES

def cal_AR_RR(uid_list, supp_mat, supp_dict, supp_avg_list, PHI_all, new_PHI):
    ''' calculate the AR (matrix) '''
    c, l = np.shape(supp_mat)
    AR_mat = supp_mat - np.repeat(np.array([supp_avg_list]), c, axis=0)
    whole_set = set(PHI_all.keys())  #
    for i,uid in enumerate(uid_list):
        CTP = [(tuple(stp.ldaStr), stp.len, stp.contain) for stp in supp_dict[uid]] if uid in supp_dict.keys() else []
        sub_set = whole_set - set(CTP)
        AR_mat[i, :][[PHI_all[key] for key in sub_set]] = 0.0
    ''' calculate the RR (matrix) '''
    avgAR = np.average(AR_mat, axis=1)          # average for the number of all patterns
    RR_mat = AR_mat - np.repeat(np.array([avgAR]).reshape((c, 1)), l, axis=1)
    # AR_mat = np.maximum(AR_mat, 0.0)          # average for the number of patterns for each users
    # sumAR = np.sum(AR_mat, axis=1)
    # CTP_len_list = [len(CTP_list[i]) if len(CTP_list[i]) > 0 else 1 for i, uid in enumerate(uid_list)]
    # avgAR = np.divide(np.array(sumAR), np.array(CTP_len_list))
    ''' Each pattern is converted from a structure to an tuple, containing basic information and values of properties '''
    PHI_set = []
    for i, uid in enumerate(uid_list):
        CTP = [(tuple(stp.ldaStr),stp.len,stp.contain) for stp in supp_dict[uid]] if uid in supp_dict.keys() else []
        index_list = [PHI_all[phi] for phi in set(CTP)]
        for pos in set(index_list):
            para = [round(supp_mat[i][pos],10), round(supp_avg_list[pos],10), round(AR_mat[i][pos],10), round(RR_mat[i][pos],10)]
            x = tuple([uid, new_PHI[pos], tuple(para)])
            PHI_set.append(x)
    return PHI_set


def transform(supp_mat,tau_stp_supp,supp_avg_list):
    uid_list = sorted(tau_stp_supp.keys())
    PHI_all = A4.getWhole_STP(tau_stp_supp)             # PHI[(lda,len)]=index
    new_PHI_all = {v: k for k, v in PHI_all.items()}    # PHI[index]=(lda,len)
    PHI_set = cal_AR_RR(uid_list, supp_mat, tau_stp_supp, supp_avg_list, PHI_all, new_PHI_all)
    return PHI_set, new_PHI_all,


def run_one_tau(in_path, out_path, tau):
    print("start the ", tau, time.time())
    for file in os.listdir(in_path):
        sub_path, save_path = os.path.join(in_path, file), os.path.join(out_path, file)
        file_path_1 = sub_path + "/TP_MAT_%s.npy" % (tau)
        file_path_2 = sub_path + "/TP_dict_%s.npy" % (tau)
        file_path_3 = sub_path + "/global_supp_%s.npy" % (tau)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if os.path.isdir(sub_path) and os.path.exists(file_path_1) and os.path.exists(file_path_2):
            supp_mat, tau_stp_supp, supp_avg_list = np.load(file_path_1), np.load(file_path_2).item(0), np.load(file_path_3)
            PHI_set, new_PHI_all = transform(supp_mat, tau_stp_supp, supp_avg_list)
            PHI_ = phi2str(PHI_set)
            np.save(save_path + "/PHI_%s.npy" % (tau), PHI_)
            np.save(save_path + "/PHI_all_%s.npy" % (tau), new_PHI_all)
    print("end. from ", in_path, "to", out_path, "at", tau, time.time())






if __name__ == '__main__':
    input_dir = os.path.join(ROOT, "CTP")
    output_dir = os.path.join(ROOT, "URCTP")
    pool = multiprocessing.Pool(min(len(TI),4))
    for tau in TI:
        pool.apply_async(run_one_tau, args=(input_dir, output_dir, tau,))
    pool.close()
    pool.join()
    '''
    for tau in TI:
        run_one_tau(tau)
    '''