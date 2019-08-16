import numpy as np
import _3A_UpsSTP_dataStruc as A3_STUC
import os



def get_subset(set1,set2):
    #string = [str(uid), str(stp[0]), stp[1], str(stp[-1]), para[0], para[1], para[2], para[-1]]
    name_1=set([item[1] for item in set1])
    name_2=set([item[1] for item in set2])
    sub_name=name_2-name_1
    sub_set=[item for item in set2 if item[1] in sub_name]
    return sub_set



TI=A3_STUC.TI
in_path="new-data/URSTP/"
out_path="new-data/URSTP_final/"
for tau in TI:
    SET={}
    for dire in os.listdir(in_path):
        print(dire)
        load_path = os.path.join(in_path, dire)
        if os.path.exists(load_path + "/URSTP_%s.npy" % (tau)):
            URSTP_set=np.load(load_path + "/URSTP_%s.npy" % (tau))
            SET[dire]=URSTP_set

    list_=sorted(SET.keys())
    for i,dire in enumerate(list_):
        save_path=os.path.join(out_path, dire)
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if i > 0:
            sub_set=get_subset(SET[list_[i-1]],SET[dire])
            np.save(save_path + "/URSTP_%s.npy" % (tau), sub_set)
        else:
            np.save(save_path + "/URSTP_%s.npy" % (tau), SET[dire])

