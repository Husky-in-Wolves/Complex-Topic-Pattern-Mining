import myClass as STUC
import os, math, itertools, numpy as np
import multiprocessing


ROOT = "new-data/russian/2016/"
Sess_dict=np.load(ROOT+"Sess_dict.npy").item(0) #Sess_dict[user id][sess id]=time_list
LDA_dict=np.load(ROOT+"LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load(ROOT+"Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list



''' get the prossible interleaving patterns, assuming the max pattern length is 4 '''
def getInterleaving(stp, length):
    a, b, c, d = [int(stp[0])] if length >= 1 else [], [int(stp[1])] if length >= 2 else [], [int(stp[2])] if length >= 3 else [], [int(stp[3])] if length >= 4 else []
    Gamma = {}
    if len(a) == 1 and len(b) == 1:
        gamma = [];interleaving = tuple(sorted(a + b));gamma.append(interleaving);gamma.extend(c);gamma.extend(d)
        Gamma[tuple(gamma)] = [a+b+c+d, b+a+c+d]
    if len(b) == 1 and len(c) == 1:
        gamma = [];gamma.extend(a);interleaving = tuple(sorted(b + c));gamma.append(interleaving);gamma.extend(d)
        Gamma[tuple(gamma)] = [a+b+c+d, a+c+b+d]
    if len(c) == 1 and len(d) == 1:
        gamma = a + b;interleaving = tuple(sorted(c + d));gamma.append(interleaving)
        Gamma[tuple(gamma)] = [a+b+c+d, a+b+d+c]
    if len(a) == 1 and len(b) == 1 and len(c) == 1 and len(d) == 1:
        gamma = [];interleaving_1 = tuple(sorted(a + b));gamma.append(interleaving_1);interleaving_2 = tuple(sorted(c + d));gamma.append(interleaving_2)
        Gamma[tuple(gamma)] = [a+b+c+d, b+a+c+d, a+b+c+d, a+b+d+c]
    return Gamma

    
''' find the pattern from list_ '''
def findBylda(list_, lda, cntTau):
    for x,l in enumerate(list_):
        if tuple(l.ldaStr) == tuple(lda) and l.tau == cntTau:
            return True,x
    return False,-1


''' find all the documents as instances of z record as <j,{zi:pj},tj>, which represent truple(pos,probs,time) '''
def findInstanceList_setEnhance(LDA_list,Prob_list,S_i,Z_set):
    InstanceList=[]
    for pos, time_ in enumerate(sorted(S_i)):
        Z = set(Z_set) & set(LDA_list[time_])
        if len(Z) > 0:
            probs = {z:Prob_list[time_][LDA_list[time_].index(z)] for z in Z}
            InstanceList.append([pos,probs,time_])
    return sorted(InstanceList, key=lambda item: item[0])


''' calculate the accuate support of interleaving patterns '''
def calAccurateProb(uid, cntTau, S_i, participant_dict, starting_dict,):
    ''' boundary condition of the equation'''
    participant_dict = {key: participant_dict[key] for key in participant_dict.keys() if len(participant_dict[key]) > 0}
    starting_dict = {key: starting_dict[key] for key in participant_dict.keys()}
    if len(participant_dict) == len(starting_dict) and len(participant_dict) <= 0:
        return 1.0
    elif list(filter(lambda start: start > S_i[-1], starting_dict.values())) != [] or \
        list(filter(lambda cand: len(cand) > len(S_i), participant_dict.values())) != []:
        return 0.0
    '''item in InstanceList, item = [pos, {z1:p1, z2:p2, ...}, time]'''
    Z = set([participant[-1] for participant in participant_dict])
    InstanceList = findInstanceList_setEnhance(LDA_dict[uid], Prob_dict[uid], S_i, Z)
    '''recursively calculating the occurrence probability of this session'''
    p_j2, P= 0.0, 0.0
    for j, mes in enumerate(InstanceList):
        mes_pos, mes_time, S_i_sub, Z, P = mes[0], mes[-1], S_i[:InstanceList[-1][0]], list(mes[1].keys()), 0
        for topic in Z:
            ''' find patterns that can be matched with message MES: 
                1. the last topic is Z and MES is an instance'''
            participant_dict_new = [participant_dict[key][0:-1] for key in participant_dict if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key]]
            starting_dict_new = [max(0, mes_time - cntTau) for key in participant_dict if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key]]
            ''' 2. the last topic is Z and MES cannot be instance
                3. the last topic is not Z '''
            participant_dict_new += [participant_dict[key] for key in participant_dict if int(participant_dict[key][-1]) != int(topic) or (int(participant_dict[key][-1]) == int(topic) and mes_time < starting_dict[key])]
            starting_dict_new += [starting_dict[key] for key in participant_dict if int(participant_dict[key][-1]) != int(topic) or (int(participant_dict[key][-1]) == int(topic) and mes_time < starting_dict[key])]
            ''' calculation '''
            P += mes[1][topic] * calAccurateProb(uid, cntTau, S_i_sub, participant_dict_new, starting_dict_new,)
        P += (1 - sum(mes[1].values())) * p_j2
        p_j2 = P
    return P



def TIILV(uid, tp_list, cntTau, pattern_length, S_key, min_Count):
    new_ilv_list, S_len = {}, len(S_key)
    for i, alpha in enumerate(tp_list):
        Gamma_dict = getInterleaving(alpha.ldaStr, pattern_length)
        for gamma in list(Gamma_dict.keys()):
            ''' avoid duplicate computation '''
            if gamma not in set(new_ilv_list.keys()):
                new_ilv_list[gamma], candidate_list, participant_list = None, Gamma_dict[gamma], []
                for candidate in candidate_list:
                    flag, index = findBylda(tp_list, candidate, cntTau)
                    if flag == True and index != -1: participant_list.append(tp_list[index])
                if len(candidate_list) > 0:
                    ''' get the approximate value of support, and the pattern must occur in enough sessions '''
                    probMat_approximate = np.mat([np.array(candidate.prob_list) for candidate in candidate_list])
                    probList_approximate = np.array(probMat_approximate.max(axis=0)).tolist()[0]
                    if len(list(filter(lambda item: item > 0.0, probList_approximate))) >= min_Count:
                        new_stp = None
                        '''if all the participants (seq) exist, the interleaving pattern is considered to exist'''
                        if len(candidate_list) == len(participant_list) or (
                                len(candidate_list) > len(participant_list) and len(participant_list) > 1):
                            '''there are more than one participants of gamma, it need accurate calculation of support '''
                            participant_dict, starting_dict = {i: participant for i, participant in participant_list}, {
                            i: 0 for i, participant in participant_list}
                            probList_accurate = [0.0 if probList_approximate[i] <= 0.0 else calAccurateProb(uid, cntTau, Sess_dict[uid][key], participant_dict, starting_dict)
                                                 for i, key in sorted(list(Sess_dict[uid].keys()))]
                            support_accurate = math.pow(sum(probList_accurate) / S_len, 1 / pattern_length)
                            new_stp = STUC.STP_Supp(ldaStr=tuple(gamma), tau=cntTau, prob_list=probList_accurate,
                                                    supp=support_accurate, l=pattern_length, contain=tuple(participant_list))
                        elif len(candidate_list) > len(participant_list) and len(participant_list) == 1:
                            '''there is only one participant of gamma, no need to mining once again'''
                            support_approximate = math.pow(sum(probList_approximate) / S_len, 1 / pattern_length)
                            new_stp = STUC.STP_Supp(ldaStr=tuple(gamma), tau=cntTau, prob_list=probList_approximate,
                                                    supp=support_approximate, l=pattern_length, contain=tuple(participant_list))
                        ''' save file '''
                        new_ilv_list[tuple(gamma)] = new_stp
    '''return the result'''
    new_ilv_list = list(filter(lambda item: item != None, new_ilv_list.values()))
    return new_ilv_list





def run_oneUser(input_dir, output_dir, userID, min_Count=2):
    ILV_TP_list = []
    SEQ_TP_list = np.load(input_dir + "/TP_dict_%s.npy" % (userID))
    '''classifying by time-interval'''
    for i, tau in enumerate(STUC.TI):
        tau_pattern_list = list(filter(lambda item: item.tau == tau, SEQ_TP_list))
        '''classifying by pattern length'''
        for length in range(3, max(set([item.l for item in tau_pattern_list])) + 1):
            len_tau_pattern_list=list(filter(lambda  item: item.l == length, tau_pattern_list))
            if len(len_tau_pattern_list) > 0:
                ''' mining interleaving pattern '''
                new_ilv_list = TIILV(uid=userID, tp_list=len_tau_pattern_list, cntTau=tau, pattern_length=length, S_key=list(Sess_dict[userID].keys()), min_Count=min_Count)
                ILV_TP_list.extend(new_ilv_list)
    ''' save the mining result '''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    np.save(output_dir + "/TP_dict_%s.npy" % (userID), ILV_TP_list)


if __name__ =='__main__':
    input_dir = os.path.join(ROOT, "User/TISEQ_1")
    output_dir = os.path.join(ROOT, "User/TIILV")
    file_list = os.listdir(input_dir)
    uid_list = list(map(int, [name[:-4].split("_")[-1] for name in file_list]))

    pool = multiprocessing.Pool(min([multiprocessing.cpu_count(),3]))
    for uid in uid_list:
        pool.apply_async(run_oneUser, (input_dir, output_dir, uid,))
    pool.close()
    pool.join()

    '''
    for uid in uid_list:
        run_oneUser(uid)
    '''