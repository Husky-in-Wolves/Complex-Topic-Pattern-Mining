import numpy as np, os, multiprocessing, time
import myClass as STUC


ROOT = "new-data/russian/2016/"
TI = STUC.TI
Sess_dict = np.load(ROOT+"Sess_dict.npy").item(0)



''' the data structure of complex topic pattern
ldaStr=tuple(gamma),tau=tau,prob_list=Supp_gamma_tau[tau],supp=average,l=gamma_len,contain=tuple([tuple(gamma)])'''
def getWhole_STP(STPSUPP_dict):
    uid_list, coll_stp_supp = sorted(STPSUPP_dict.keys()), []
    set_, dict_, count = set(coll_stp_supp), {}, 0
    for uid in uid_list:
        if uid in STPSUPP_dict.keys():
            ldaStr_list=[(stp.ldaStr,stp.len,stp.contain) for stp in STPSUPP_dict[uid]]
            coll_stp_supp.extend(ldaStr_list)
    for key in set_:
        dict_[key]=count; count+=1
    return dict_


def transform(uid_list, tau_stp_supp):
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


''' Store all patterns by user id according to the value of time-interval (tau)
TISTP_dict is a dict:    key1=tau    key2=user id    value=CTP(seq) '''
def file2dict(input_dir,output_dir):
    CTP4tau_dict = {tau: {} for i, tau in enumerate(TI)}
    file_list = os.listdir(input_dir)
    idlist=list(map(str, [name[:-4].split("_")[-1] for name in file_list]))
    for uid in sorted(idlist):
        stp_list=np.load(input_dir+"/TP_dict_%s.npy" % (uid))
        print(uid, len(stp_list))
        if len(stp_list) < 5:
            continue
        else:
            for stp in stp_list:    # STP_Supp(ldaStr=gamma,tau=tau,supp=Supp_gamma_tau[tau],l=gamma_len)
                if uid not in CTP4tau_dict[stp.tau].keys():
                    CTP4tau_dict[stp.tau][uid] = []
                CTP4tau_dict[stp.tau][uid].append(stp)
    for i, tau in enumerate(TI):
        np.save(output_dir + "/TP_dict_%s.npy" % (tau), CTP4tau_dict[tau])


def dict2mat(input_dir, tau):
    if os.path.exists(input_dir + "/TP_dict_%s.npy" % (tau)):
        ''' tau_stp_supp[uid] = stp_list '''
        tau_stp_supp = np.load(input_dir + "/TP_dict_%s.npy" % (tau)).item(0)
        uid_list = sorted(tau_stp_supp.keys())
        ''' convert dict to mat '''
        uid_phi_MAT = transform(uid_list, tau_stp_supp)
        ''' calculate the global support for each pattern '''
        supp_sum_list = np.sum(uid_phi_MAT, axis=0)
        supp_avg_list = [supp / len(uid_list) for supp in supp_sum_list]
        ''' storage '''
        np.save(input_dir + "/TP_MAT_%s.npy" % (tau), uid_phi_MAT)
        np.save(input_dir + "/global_supp_%s.npy" % (tau), supp_avg_list)
    print("end converting dictionaries into matrix... ", input_dir, tau, time.time())


def run_one_tau(input_dir,output_dir):
    file2dict(input_dir,output_dir)
    for tau in TI:
        dict2mat(output_dir, tau)


if __name__ == '__main__':
    ''' the mined CTPs (sequential) (min_count=2) for each user is stored in User/TISEQ_2 '''
    ''' the mined CTPs (interleaving) (min_count=2) for each user is stored in User/TIILV '''
    ''' the mined STPs (min_count=2) for each user is stored in User/STP '''
    List_ = [(os.path.join(ROOT,"User/TISEQ_2"), os.path.join(ROOT, "CTP/SEQ")),
             (os.path.join(ROOT,"User/TIILV"), os.path.join(ROOT, "CTP/ILV")),
             (os.path.join(ROOT,"User/STP"), os.path.join(ROOT, "CTP/STP"))]

    pool = multiprocessing.Pool(len(TI))
    for (input_dir, output_dir) in List_:
        pool.apply_async(run_one_tau, args=(input_dir, output_dir))
    pool.close()
    pool.join()

