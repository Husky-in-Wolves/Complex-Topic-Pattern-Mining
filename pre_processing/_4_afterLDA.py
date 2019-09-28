import numpy as np, os


''' Superparametric, minimum probability of a topic occurring in a message '''
htp = 0.35
in_ROOT = 'TwitterWithLabel/'
out_ROOT = 'new-data/'


def get_label_prob(z_list):
    z_dict, length = {}, len(z_list)
    for z in z_list:
        z = int(z)
        z_dict[z] = 1 if z not in z_dict.keys() else z_dict[z] + 1
    label_list = [key for key in sorted(list(z_dict.keys())) if z_dict[key] / length >= htp]
    prob_list = [z_dict[key] / length for key in label_list]
    return label_list, prob_list

def getDistribution(file_name, userID, LDA_dict, Prob_dict, data_dict, plus):
    try: tid_list = sorted(list(data_dict[userID].keys()))
    except: tid_list = sorted(list(data_dict[file_name].keys()))
    with open(ROOT + file_name) as file:
        line_list=file.readlines()
        if len(line_list) != len(tid_list):
            print("error: getDistribution tid len",len(line_list),len(tid_list),file_name,data_dict[userID], line_list[-1])
        elif len(line_list) == len(tid_list):
            for i, line in enumerate(line_list):
                z_list = line.strip("\n").strip("\t").split("\t")[1:]
                z_list = [int(z) for z in z_list]
                label_list, prob_list = get_label_prob(z_list)
                LDA_dict[userID+plus][tid_list[i]], Prob_dict[userID+plus][tid_list[i]] = label_list, prob_list



if __name__ =='__main__' :
    data_dict_2016 = np.load(in_ROOT + 'data_dict_2016.npy').item(0)
    data_dict_2018 = np.load(in_ROOT + 'data_dict_2018.npy').item(0)
    data_dict_russian = np.load(in_ROOT + "data_dict_russian.npy").item(0)
    user_lable_russian = np.load(in_ROOT + "user_lable_russian.npy").item(0)
    plus = [201600000, 201800000, 0]

    LDA_dict, Prob_dict, file_list = {}, {}, os.listdir(ROOT)

    for i, data_dict in enumerate(data_dict_list):
        for uid in sorted(list(data_dict.keys())):
            file_name = str(int(uid) + plus[i]) + ".txt"
            if file_name in file_list:
                LDA_dict[int(uid) + plus[i]], Prob_dict[int(uid) + plus[i]] = {}, {}
                getDistribution(file_name, int(uid), LDA_dict, Prob_dict, data_dict_2016, plus)
                if uid in user_vaild_lable.keys():
                    for ts in user_vaild_lable[user_id]:
                        if user_lable_russian[user_id][ts] == False or len(LDA_dict[user_id][ts]) <= 0 and len(Prob_dict[user_id][ts]) <= 0:
                            LDA_dict[int(uid) + plus[i]].pop(ts)
                            Prob_dict[int(uid) + plus[i]].pop(ts)
            else:
                print("error: there is no file: " + file_name)


    np.save(out_ROOT+"LDA_dict.npy", LDA_dict)
    np.save(out_ROOT+"Prob_dict.npy", Prob_dict)
