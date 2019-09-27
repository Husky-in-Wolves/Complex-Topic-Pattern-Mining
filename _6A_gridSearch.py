import numpy as np
import parameterChoice._3A_UpsSTP_dataStruc as A3
import parameterChoice.pointGraph as PG
import os,math



ROOT = "new-data/russian/2016/"
TI = A3.TI


def get_special(user_set):
    special_users = [item for item in user_set if int(item) <= 30000]
    no_special_users = [item for item in user_set if int(item) > 30000]
    return special_users, no_special_users


def getURUserList(PHI_set, supp_avg_list, special_num, hss_percent, hss_num):
    if hss_percent < 1.0 and supp_avg_list != []:
        hss_threshold = sorted(supp_avg_list)[min(math.ceil(len(supp_avg_list) * hss_percent) - 1, hss_num)]
        hss_pattern_list = [list(pattern) for pattern in PHI_set if float(pattern[-3]) <= hss_threshold]
    else:
        hss_pattern_list = sorted(PHI_set, key=lambda item: float(item[-3]), reverse=False)[:min(hss_num, len(PHI_set))]
    ''' select the user-pattern pairs with minimum global support values '''
    hss_num = len([pattern for pattern in hss_pattern_list])
    sort_pattern_list = sorted(hss_pattern_list, key=lambda item: item[-1], reverse=True)
    ''' select the user-pattern pairs with top-K relative rarity '''
    hrr = 300; predict_num = 0; predict_pattern_list, predict_user = [], []
    while predict_num < special_num and hrr <= hss_num:
        predict_pattern_list = sort_pattern_list[0:hrr]
        predict_user = set([pattern[0] for pattern in predict_pattern_list])
        predict_num = len(predict_user)
        hrr += 10
    return predict_pattern_list, predict_user, predict_num, hrr


def getUserList(PHI_set, supp_avg_list, special_num, hss_percent, hss_num,):
    predict_pattern_list, predict_user, predict_num, hrr = getURUserList(PHI_set,supp_avg_list,special_num,hss_percent=hss_percent,hss_num=hss_num)
    no_predict_user = set([list(pattern)[0] for pattern in PHI_set]) - set(predict_user)
    correct_users, no_correct_users = get_special(predict_user)
    no_noise_users, noise_users = get_special(no_predict_user)
    return correct_users, no_correct_users, no_noise_users, noise_users, hrr


''' calculate the recognition effect  '''
def get_metric(correct_num, no_correct_num, no_noise_num, noise_num):
    try:
        accuracy = (correct_num+noise_num)/(correct_num+no_correct_num+no_noise_num+noise_num)
        precision = correct_num / (correct_num + no_correct_num)
        recall = correct_num / (correct_num + no_noise_num)
        f1= 2 * precision * recall /(precision + recall)
    except:
        accuracy,precision, recall, f1 = 0,0,0,0
    return accuracy,precision, recall, f1


def avg_tau(input_dir_1, input_dir_2, file):
    hss_list = np.arange(0.1, 0.3, 0.05)
    X, Y = [], []
    P, R, F = np.zeros((len(TI), len(hss_list))), np.zeros((len(TI), len(hss_list))), np.zeros((len(TI), len(hss_list)))
    for i, tau in enumerate(TI):
        path_in, path_out = os.path.join(input_dir_1, file), os.path.join(input_dir_2, file)
        supp_avg_list = np.load(path_in + "/global_supp_%s.npy" % (tau))
        PHI_set = np.load(path_out + "/PHI_%s.npy" % (tau))
        # PHI_plus += list(PHI_set); supp_avg_plus += list(supp_avg_list)
        PHI_user = [pattern[0] for pattern in PHI_set]
        special_users, no_special_users = get_special(PHI_user)
        special_num = len(special_users)
        for j, hss in enumerate(hss_list):
            correct_users, no_correct_users, no_noise_users, noise_users, hrr = getUserList(PHI_set, supp_avg_list, special_num, hss,hss_num=2500)
            correct_num = len(correct_users);no_correct_num = len(no_correct_users);no_noise_num = len(no_noise_users);noise_num = len(noise_users)
            accuracy, precision, recall, f1 = get_metric(correct_num, no_correct_num, no_noise_num, noise_num)
            print(tau, hss, special_num, correct_num, no_correct_num, no_noise_num, noise_num, accuracy, precision, recall, f1)
            F[i][j] = 1 / (f1+0.00000001)
            X.append(hss); Y.append(hrr)
    f = len(TI) / np.sum(F, axis=0)
    X=[round(x,2) for x in X]
    PG.point_2D_1Layer(X[:len(hss_list)],f,xlabel="the threshold(%) for global support")    #def point_2D_1Layer(X,Y,xlabel,ylable,title="2D",labels=""):


def getURCTP(input_dir_1, input_dir_2, file, hss):
    path_in, path_out = os.path.join(input_dir_1, file), os.path.join(input_dir_2, file)
    Res = {}
    for i, tau in enumerate(TI):
        supp_avg_list = np.load(path_in + "/global_supp_%s.npy" % (tau))
        PHI_set = np.load(path_out + "/PHI_%s.npy" % (tau))
        ''' find the user-aware rare ones '''
        special_users, no_special_users = get_special([pattern[0] for pattern in PHI_set])
        special_num = len(special_users); no_special_num = len(no_special_users)
        correct_users, no_correct_users, no_noise_users, noise_users, hrr = getUserList(PHI_set, supp_avg_list, special_num, hss, 3500)
        correct_num = len(correct_users); no_correct_num = len(no_correct_users); no_noise_num = len(no_noise_users); noise_num = len(noise_users)
        ''' calculate the quality of discovery '''
        accuracy, precision, recall, f1 = get_metric(correct_num, no_correct_num, no_noise_num, noise_num)
        Res[tau] = [precision, recall, f1]
        print(tau, hss, hrr, "--", special_num, no_special_num, "--", correct_num, no_correct_num, no_noise_num,noise_num)
    return Res




if __name__ == "__main__":
    input_dir_1 = os.path.join(ROOT, "CTP")
    input_dir_2 = os.path.join(ROOT, "URCTP")
    file_list = ["SEQ", "ILV", "STP"]
    hss = 0.2
    res_list = [getURCTP(input_dir_1, input_dir_2, file, hss) for file in file_list]
    print(res_list)





'''
    [0.85785536159601]
    [0.85785536159601, 0.9013333333333333, 0.8870967741935484, 0.9405684754521965, 0.9322916666666666, 0.9206349206349206, 0.9198966408268734]
    [0.9104477611940299, 0.9326683291770573, 0.9226932668329176, 0.8977556109725685, 0.8827930174563591, 0.8656716417910448, 0.8628428927680798]
    [0.9206349206349206, 0.9506493506493507, 0.9238578680203046, 0.9095477386934674, 0.8721804511278195, 0.835, 0.827930174563591]
    
    Y0=[0.902]
    Y1=[0.91,0.915,0.92,0.92,0.91,0.91]
    Y2=[0.94,0.955,0.958,0.97,0.955,0.93]
    F4=[0.965,0.975,0.965,0.947,0.93,0.924]
'''
