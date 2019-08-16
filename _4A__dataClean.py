import numpy as np
import _3A_UpsSTP_dataStruc as A3_STUC

import os

Count=0
ROOT="new-data-gun/"
# ROOT="new-data-russian/"
TI=[3600*36]#A3_STUC.TI

'''
算法三使用多线程，每个用户的STP分别保存在自己的文件内，
按照时间间隔tau，合并为多个字典 
TISTP_dict 是一维字典   key1=tau key2=userID     value=同一时间间隔下的该用户所有stp
'''
def STP_file2dict(dir_):
    global Count
    #初始化
    TISTP_dict_list=[[] for i in range(len(TI))]
    for i, tau in enumerate(TI):
        TISTP_dict_list[i] = {}

    file_list = os.listdir(dir_)
    #字符串数组变为整形数组
    #idlist=list(map(int, [name[:-4].split("_")[-1] for name in file_list]))
    idlist=list(map(str, [name[:-4].split("_")[-1] for name in file_list]))
    idlist=sorted(idlist)
    for uid in sorted(idlist):
        stp_list=np.load(dir_+"STPSUPP_dict_%s.npy" % (uid))
        if len(stp_list)<3:
            Count+=1
            continue
        else:
            print(uid, len(stp_list))# print(stp_list[0].tau)
            if len(stp_list) > 0:
                # 按照TI分别保存
                for i in range(len(TI)):
                    TISTP_dict_list[i][uid] = []
                # STUC.STP_Supp(ldaStr=gamma,tau=tau,supp=Supp_gamma_tau[tau],l=gamma_len)
                for stp in stp_list:
                    ind = TI.index(stp.tau)
                    TISTP_dict_list[ind][uid].append(stp)

    # 保存到本地
    for i, tau in enumerate(TI):
        # np.save(ROOT+"TISTP_TI/STP_dict_%s.npy" % (tau), TISTP_dict_list[i])
        # np.save(ROOT+"TISTP/STP_dict_%s.npy" % (tau), TISTP_dict_list[i])
        np.save(ROOT+"STP/STP_dict_%s.npy" % (tau), TISTP_dict_list[i])



if __name__ == '__main__':
    # STP_file2dict(dir_="new-data/User_TISTP/")
    # STP_file2dict(dir_=ROOT+"User_TISTP_/")
    STP_file2dict(dir_=ROOT+"User_STP_/")

    print(Count)





