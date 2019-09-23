import numpy as np, os


''' Superparametric, minimum probability of a topic occurring in a message '''
htp = 0.35
ROOT = '../TwitterWithLabel/2/'
dir_ = '../new-data/'
LDA_dict, Prob_dict = {}, {}


def get_label_prob(z_list):
    z_dict, length = {}, len(z_list)
    for z in z_list:
        z = int(z)
        z_dict[z] = 1 if z not in z_dict.keys() else z_dict[z] + 1
    label_list = [key for key in sorted(list(z_dict.keys())) if z_dict[key] / length >= htp]
    prob_list = [z_dict[key] / length for key in label_list]
    return label_list,prob_list


def getDistribution(file_name,userID,LDA_dict,Prob_dict,data_dict,plus=0):
    try:
        tid_list = sorted(list(data_dict[userID].keys()))
    except:
        tid_list = sorted(list(data_dict[file_name].keys()))

    with open(ROOT+file_name) as file:
        line_list=file.readlines()
        if len(line_list) != len(tid_list):
            print("error: getDistribution tid len",len(line_list),len(tid_list),file_name,data_dict[userID], line_list[-1])
        elif len(line_list) == len(tid_list):
            userID += plus
            for i, line in enumerate(line_list):
                z_list = line.strip("\n").strip("\t").split("\t")[1:]
                z_list = [int(z) for z in z_list]
                label_list, prob_list = get_label_prob(z_list)
                LDA_dict[userID][tid_list[i]] = label_list
                Prob_dict[userID][tid_list[i]] = prob_list




if __name__ =='__main__' :
    file_list = os.listdir(ROOT)
    data_dict = np.load(dir_+'data_dict_2016.npy').item(0)
    name_dict = np.load(dir_+'name_dict_2016.npy').item(0)

    # LDA生成的文件比原始少12个
    #print(len(file_list),len(list(name_dict.keys())),len(list(sess_dict.keys())))
    # 不包含重名文件
    #print(len(list(name_dict.values())),len(set(list(name_dict.keys()))))

    '''
    LDA_dict is a second-level dictionary: key_1 = user ID, key_2 = timestamp, value = a list of topic categories
    prob_dict is a second-level dictionary: key_1 = user ID, key_2 = timestamp, value = a list of probability
    '''
    for user_key in sorted(list(name_dict.keys())):
        LDA_dict[user_key], Prob_dict[user_key] = {}, {}
        file_name = name_dict[user_key] + ".txt"
        if file_name in file_list:
            getDistribution(file_name,user_key,LDA_dict,Prob_dict,data_dict)
        else:
            print("error: there is no file: "+file_name)

    np.save(dir_+"LDA_dict.npy", LDA_dict)
    np.save(dir_+"Prob_dict.npy", Prob_dict)

