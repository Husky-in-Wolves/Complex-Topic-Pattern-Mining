import os, re, numpy as np
import parameterChoice._3A_UpsSTP_dataStruc as A3
from parameterChoice.B_1_gridSearch import get_special, getURUserList, getUserList, get_metric, getURCTP
import parameterChoice.pointGraph as PG


ROOT = "new-data/russian/2016/"
TI = A3.TI


def str2list(pattern_old="(((13, 12, 1), ((13, 12, 1),)),)"):
    patterns = pattern_old.split("), (")        # split the list of participants (string)
    list_ = [tuple([int(d) for d in re.findall(r"\d+",pat)]) for pat in patterns ] # split the list of participants (list)
    return set(list_)


def crossFilter(STP, ITP):
    new_STP, new_ITP = set(STP), set(ITP)   # lines 1-2
    ''' extract the (user-pattern pairs) of all sequential patterns '''
    seq_pattern = [(pattern[0], tuple([int(d) for d in re.findall(r"\d+", pattern[1])])) for pattern in STP]    # line 3
    '''pat[0]=user, pat[1]=pattern, pat[2]=length, pat[3]=participants, pat[-3]=global support, pat[-1]=relative rarity'''
    for i, interleaving in enumerate(ITP):
        ''' extract the names of all participants (user-pattern pairs) of a interleaving pattern '''
        participant_set = [(interleaving[0], list_) for list_ in str2list(interleaving[3])]         # line 4
        match= set(seq_pattern) & set(participant_set)                                              # line 5
        Gamma = list(filter(lambda x: (x[0], tuple([int(d) for d in re.findall(r"\d+", x[1])])) in Gamma, STP)) # line 6
        ''' if participants do not all exist, the sequential patterns is invaild '''
        if len(match) == len(participant_set) and len(participant_set) > 1:                         # line 7
            new_ITP[i][-1] = max([pat[-1] for pat in Gamma])
            new_STP = new_STP - set(Gamma)                                                          # line 8
        elif match != set([]) and (len(Gamma) < len(participant_set) or len(participant_set) <= 1): # line 9
            new_ITP = new_ITP - set([interleaving])
    return new_STP, new_ITP


def mergePatterns(input_dir_1, input_dir_2, files, hss):
    NUMBER, STP, ITP, RES = 0, [], [], {}
    for i, tau in enumerate(TI):
        for file in files:
            path_in, path_out = os.path.join(input_dir_1, file), os.path.join(input_dir_2, file)
            supp_avg_list = np.load(path_in + "/global_supp_%s.npy" % (tau))
            PHI_set = np.load(path_out + "/PHI_%s.npy" % (tau))
            ''' find the user-aware rare ones '''
            special_users, no_special_users = get_special([pattern[0] for pattern in PHI_set])
            predict_pattern_list, predict_user, predict_num, hrr = getURUserList(PHI_set, supp_avg_list, len(special_users), hss_percent=hss ,hss_num=2500)
            ''' Classified preservation '''
            if file == "0":
                STP.extend(predict_pattern_list)
            else:
                ITP.extend(predict_pattern_list)
            NUMBER = max([NUMBER, len(special_users)])
        ''' merge the sequential and interleaving pattern '''
        STP, ITP = crossFilter(STP, ITP)
        correct_users, no_correct_users, no_noise_users, noise_users, hrr = getUserList(list(STP ) +list(ITP), [], NUMBER, hss_percent=1.0, hss_num=5000)
        correct_num = len(correct_users); no_correct_num = len(no_correct_users); no_noise_num = len(no_noise_users); noise_num = len(noise_users)
        accuracy, precision, recall, f = get_metric(correct_num, no_correct_num, no_noise_num, noise_num)
        print(tau, hss, hrr, "--", NUMBER, "--", correct_num, no_correct_num, no_noise_num, noise_num)
        RES[tau] = [precision, recall, f]
    return RES



if __name__ == "__main__":
    input_dir_1 = os.path.join(ROOT, "CTP")
    input_dir_2 = os.path.join(ROOT, "URCTP")
    hss = 0.2

    files = ["SEQ", "ILV"]
    res = mergePatterns(input_dir_1, input_dir_2, files, hss)
    print(res)

    ''' draw the plot graph of discovery quality '''
    file_list = ["STP", "SEQ", "ILV"]
    res_dict = {str(file): getURCTP(input_dir_1, input_dir_2, file, hss) for file in file_list}
    res_dict["CTP"] = mergePatterns(input_dir_1, input_dir_2, files, hss)
    PG.plot_scatter(X = TI, L = [res_dict[key] for key in ["CTP", "SEQ", "ILV"]], P = res_dict["STP"], labels = ["URCTP", "URSEQ", "URILV", "URSTP"], xlabel = "time-intervals", ylabel = "F1-values", title = "the quality of discovrery")
