import runtime.myClass as myClass
import os, math, time, numpy as np
import itertools


RAW = "data/"
ROOT = "seq-data/"
OUT = "ilv-data/"
Sess_dict, LDA_dict, Prob_dict = {}, {}, {}
R_gamma = []

''' get the prossible interleaving patterns '''
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
def findPattern(list_, lda, cntTau):
    for x, l in enumerate(list_):
        if tuple(l.ldaStr) == tuple(lda) and l.tau == cntTau:
            return True, x
    return False, -1


''' find all the documents as instances of z record as <j,{zi:pj},tj>, which represent truple(pos,probs,time) '''
def findInstanceList_setEnhance(LDA_list, Prob_list, S_i, Z_set):
    InstanceList = []
    for pos, time_ in enumerate(sorted(S_i)):
        Z = set(Z_set) & set(LDA_list[time_])
        if len(Z) > 0:
            probs = {z: Prob_list[time_][LDA_list[time_].index(z)] for z in Z}
            InstanceList.append([pos, probs, time_])
    return sorted(InstanceList, key=lambda item: item[0])


''' calculate the accuate support of interleaving patterns '''
def calAccurateProb(uid, cntTau, S_i, participant_dict, starting_dict, ):
    ''' boundary condition of the equation'''
    participant_dict = {key: participant_dict[key] for key in participant_dict.keys() if len(participant_dict[key]) > 0}
    starting_dict = {key: starting_dict[key] for key in participant_dict.keys()}
    if len(participant_dict) <= 0 and len(starting_dict) <= 0:
        return 1.0
    if len(S_i) <= 0 or len(list(filter(lambda start: start > S_i[-1], starting_dict.values()))) > 0:
        return 0.0

    ''' item in InstanceList, item = [pos, {z1:p1, z2:p2, ...}, time] '''
    Z_set = set([participant[-1] for participant in participant_dict.values()])
    InstanceList = findInstanceList_setEnhance(LDA_dict[uid], Prob_dict[uid], S_i, Z_set)
    if len(InstanceList) <= 0:
        return 0.0

    ''' find the recorded data to avoid repeated computation '''
    pattern_start_dict = {participant_dict[key]: starting_dict[key] for key in participant_dict.keys()}
    recorded_start = list(filter(lambda item: item.pattern_start_dict == pattern_start_dict, R_gamma))
    recorded_end = list(filter(lambda item: item.time_end == InstanceList[-1][-1], recorded_start))
    if len(recorded_end) > 0:
        return recorded_end[0].prob

    ''' recursively calculating the occurrence probability of this session '''
    p_j2, P = 0.0, 0.0
    for j, mes in enumerate(InstanceList):
        recorded_end = list(filter(lambda item: item.time_end == mes[-1], recorded_start))
        if len(recorded_end) > 0:
            P = recorded_end[0].prob
        else:
            mes_pos, mes_time, S_i_sub, Z, P, Z_match = mes[0], mes[-1], S_i[:mes[0]], list(mes[1].keys()), 0, []
            for topic in Z:
                ''' find patterns that can be matched with message MES:     1. the last topic is Z and MES is an instance (yes)
                    2. the last topic is Z and MES cannot be instance (no)  3. the last topic is not Z (no) '''
                participant_dict_new = {key: participant_dict[key][0:-1] if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key] else participant_dict[key]
                                        for key in participant_dict.keys()}
                starting_dict_new = {key: max(0, mes_time - cntTau) if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key] else starting_dict[key]
                                     for key in participant_dict.keys()}
                ''' calculation '''
                p_star = calAccurateProb(uid, cntTau, S_i_sub, participant_dict_new, starting_dict_new)
                if p_star > 0.0:
                    P += mes[1][topic] * p_star
                    Z_match.append(topic)
            P += (1.0 - sum([mes[1][topic] for topic in Z_match])) * p_j2
            # R_gamma.append(myClass.Prefix_ILV(tau=cntTau, pattern_start_dict=pattern_start_dict, time_end=mes_time, prob=P))
        p_j2 = P
    return P

''' calculate the accuate support of interleaving patterns '''
def calAccurateProb_2(uid, cntTau, S_i, participant_dict, starting_dict, ):
    ''' boundary condition of the equation'''
    participant_dict = {key: participant_dict[key] for key in participant_dict.keys() if len(participant_dict[key]) > 0}
    starting_dict = {key: starting_dict[key] for key in participant_dict.keys()}
    pattern_start_dict = {participant_dict[key]: starting_dict[key] for key in participant_dict.keys()}

    if len(participant_dict) <= 0 and len(starting_dict) <= 0:
        print(S_i[-1], pattern_start_dict, "no pattern")
        return 1.0
    if len(S_i) <= 0 or len(list(filter(lambda start: start > S_i[-1], starting_dict.values()))) > 0:
        print("\t", pattern_start_dict, "no message")
        return 0.0

    ''' item in InstanceList, item = [pos, {z1:p1, z2:p2, ...}, time] '''
    Z_set = set([int(participant[-1]) for participant in participant_dict.values()])
    InstanceList = findInstanceList_setEnhance(LDA_dict[uid], Prob_dict[uid], S_i, Z_set)
    if len(InstanceList) <= 0:
        print(S_i[-1], pattern_start_dict, "no instance")
        return 0.0

    ''' find the recorded data to avoid repeated computation '''
    recorded_start = list(filter(lambda item: item.pattern_start_dict == pattern_start_dict, R_gamma))
    recorded_end = list(filter(lambda item: item.time_end == InstanceList[-1][-1], recorded_start))
    if len(recorded_end) > 0:
        print(S_i[-1], pattern_start_dict, "repeated computation", recorded_end[0].pattern_start_dict, recorded_end[0].time_end, recorded_end[0].prob)
        return recorded_end[0].prob

    ''' recursively calculating the occurrence probability of this session '''
    p_j2, P = 0.0, 0.0
    for j, mes in enumerate(InstanceList):
        recorded_end = list(filter(lambda item: item.time_end == mes[-1], recorded_start))
        if len(recorded_end) > 0:
            P = recorded_end[0].prob
            print("Recorded:\t", pattern_start_dict, "mes=", mes[-1], "P=", P)
        else:
            mes_pos, mes_time, S_i_sub, Z, P, Z_match = mes[0], mes[-1], S_i[:mes[0]], list(mes[1].keys()), 0.0, []
            for topic in Z:
                ''' find patterns that can be matched with message MES:     1. the last topic is Z and MES is an instance (yes)
                    2. the last topic is Z and MES cannot be instance (no)  3. the last topic is not Z (no) '''
                participant_dict_new = {key: participant_dict[key][0:-1] if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key] else participant_dict[key]
                                        for key in participant_dict.keys()}
                starting_dict_new = {key: max(0, mes_time - cntTau) if int(participant_dict[key][-1]) == int(topic) and mes_time >= starting_dict[key] else starting_dict[key]
                                     for key in participant_dict.keys()}
                ''' calculation '''
                p_star = calAccurateProb_2(uid, cntTau, S_i_sub, participant_dict_new, starting_dict_new)
                if p_star > 0.0:
                    P += mes[1][topic] * p_star
                    Z_match.append(topic)
                    print("Recursively:\t", pattern_start_dict, "mes=",mes_time, "topic=", topic, "p=", mes[1][topic], "p_star=",p_star,"P=", P)
            P += (1.0 - sum([mes[1][topic] for topic in Z_match])) * p_j2
            print("calculation:\t", pattern_start_dict, mes_time,Z_match,[mes[1][topic] for topic in Z_match], P, p_j2)
            R_gamma.append(myClass.Prefix_ILV(tau=cntTau, pattern_start_dict=pattern_start_dict, time_end=mes_time, prob=P))
        p_j2 = P
    return P


def getProbList(uid, cntTau, participant_list, probList_approximate,):
    Sess_list, probList_accurate = Sess_dict[uid], [0.0] * len(Sess_dict[uid].keys())
    S_key = [(i, key) for i, key in enumerate(Sess_list.keys()) if probList_approximate[i] > 0.0]
    for (i, key) in S_key:
        probList_accurate[i] += probList_approximate[i]
        for size in range(2, len(participant_list) + 1):
            SUM = 0.0
            for combination in itertools.combinations(participant_list, size):
                participant_dict = {j: item.ldaStr for j, item in enumerate(list(combination))}
                starting_dict = {j: Sess_list[key][0] for j, item in enumerate(list(combination))}
                P = calAccurateProb(uid, cntTau, Sess_list[key], participant_dict, starting_dict)
                SUM += P
            probList_accurate[i] += math.pow(-1, size-1) * SUM
            if probList_accurate[i] > 1.0:
                print((i, key), [item.ldaStr for item in participant_list], probList_approximate[i], SUM)
                SUM = 0.0
                for combination in itertools.combinations(participant_list, size):
                    participant_dict = {j: item.ldaStr for j, item in enumerate(list(combination))}
                    starting_dict = {j: Sess_list[key][0] for j, item in enumerate(list(combination))}
                    P = calAccurateProb_2(uid, cntTau, Sess_list[key], participant_dict, starting_dict)
                    SUM += P
    return probList_accurate




def TIILV(uid, tp_list, cntTau, pattern_length, min_Count):
    global R_gamma; R_gamma = []
    S_key, new_ilv_list = sorted(list(Sess_dict[uid].keys())), {}
    for i, alpha in enumerate(tp_list):
        Gamma_dict = getInterleaving(alpha.ldaStr, pattern_length)
        for gamma in list(Gamma_dict.keys()):
            # print(i,alpha,gamma,Gamma_dict[gamma])
            ''' avoid duplicate computation '''
            if gamma not in set(new_ilv_list.keys()):
                new_ilv_list[gamma], candidate_list, participant_list = None, Gamma_dict[gamma], []
                for candidate in candidate_list:
                    flag, index = findPattern(tp_list, candidate, cntTau)
                    if flag == True and index != -1: participant_list.append(tp_list[index])
                if len(candidate_list) > 0:
                    ''' get the approximate value of support, and the pattern must occur in enough sessions '''
                    probMat_approximate = np.mat([np.array(participant.prob_list) for participant in participant_list])
                    probList_approximate = np.array(probMat_approximate.sum(axis=0)).tolist()[0]

                    if len(list(filter(lambda item: item > 0.0, probList_approximate))) >= min_Count:
                        new_stp = None
                        '''if all the participants (seq) exist, the interleaving pattern is considered to exist'''
                        if len(candidate_list) == len(participant_list) or (len(candidate_list) > len(participant_list) and len(participant_list) > 1):
                            '''there are more than one participants of gamma, it need accurate calculation of support '''
                            probList_accurate = getProbList(uid, cntTau, participant_list, probList_approximate)
                            support_accurate = math.pow(sum(probList_accurate) / len(S_key), 1 / pattern_length)
                            # print("accurate:", tuple(gamma), support_accurate, probList_accurate)
                            new_stp = myClass.STP_Supp(ldaStr=tuple(gamma), tau=cntTau, prob_list=probList_accurate,
                                                    supp=support_accurate, l=pattern_length, contain=tuple(participant_list))

                        elif len(candidate_list) > len(participant_list) and len(participant_list) == 1:
                            '''there is only one participant of gamma, no need to mining once again'''
                            support_approximate = math.pow(sum(probList_approximate) / len(S_key), 1 / pattern_length)
                            # print("approximate:", tuple(gamma), support_approximate, probList_approximate)
                            new_stp = myClass.STP_Supp(ldaStr=tuple(gamma), tau=cntTau, prob_list=probList_approximate,
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
    # for i, tau in enumerate(myClass.TI):
    tau = 5
    tau_pattern_list = list(filter(lambda item: item.tau == tau, SEQ_TP_list))
    '''classifying by pattern length'''
    if len(tau_pattern_list) > 0:
        for length in range(3, max(set([item.len for item in tau_pattern_list])) + 1):
            len_tau_pattern_list = list(filter(lambda item: item.len == length, tau_pattern_list))
            if len(len_tau_pattern_list) > 0:
                new_ilv_list = TIILV(uid=userID, tp_list=len_tau_pattern_list, cntTau=tau, pattern_length=length, min_Count=min_Count)
                ILV_TP_list.extend(new_ilv_list)

    ''' save the mining result '''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    np.save(output_dir + "/TP_dict_%s.npy" % (userID), ILV_TP_list)


if __name__ == '__main__':
    print("*** The algorithm for mining topic pattern is %s" % (str(TIILV)), "***")

    ''' adjust the file path according to actual situation  '''
    file_list = os.listdir(RAW)
    for file_name in file_list:
        raw_dir = os.path.join(RAW,file_name)
        LDA_dict = np.load(raw_dir + "/LDA_dict.npy").item(0)  # LDA_dict[user id][time]=[LDA id,...] list
        Prob_dict = np.load(raw_dir + "/Prob_dict.npy").item(0)  # Prob_dict[user id][time]=[prob,...] list
        Sess_dict = np.load(raw_dir + "/Sess_dict.npy").item(0)  # Sess_dict[user id][sess id]=time_list

        root_dir = os.path.join(ROOT, file_name)
        uid_list = list(map(int, [file_name[:-4].split("_")[-1] for file_name in os.listdir(root_dir)]))

        ''' serial execution '''
        start_time = time.time()
        for uid in uid_list:
            run_oneUser(input_dir=os.path.join(ROOT, file_name), output_dir=os.path.join(OUT, file_name), userID=uid)
        end_time = time.time()
        print(file_name, (end_time - start_time) / len(uid_list))
