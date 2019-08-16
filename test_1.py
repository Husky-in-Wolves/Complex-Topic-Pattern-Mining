import numpy as np, os

ROOT="new-data-russian/"
Sess_dict=np.load(ROOT+"Sess_dict.npy").item(0) #Sess_dict[user id][sess id]=time_list
LDA_dict=np.load(ROOT+"LDA_dict.npy").item(0)   #LDA_dict[user id][time]=[LDA id,...] list
Prob_dict=np.load(ROOT+"Prob_dict.npy").item(0) #Prob_dict[user id][time]=[prob,...] list

end_2016=1451487600
end_2017=1483110000
end_2018=1577718000
DICT={2016:[], 2017:[], 2018:[]}
user_list=[u for u in LDA_dict.keys() if int(u)<30000]
for uid in user_list:
    time_list=sorted(list(LDA_dict[uid].keys()))
    min_time=min(time_list); max_time=max(time_list)
    if max_time<=end_2016+10**6 :
        DICT[2016].append(uid)
    elif max_time<=end_2017+10**6:
        DICT[2017].append(uid)
    elif max_time<=end_2018+10**6:
        DICT[2018].append(uid)
print(len(DICT[2016]), DICT[2016])
print(len(DICT[2017]), DICT[2017])
print(len(DICT[2018]), DICT[2018])

user_list=[u for u in LDA_dict.keys() if int(u)>30000]
for uid in user_list:
    time_list=sorted(list(LDA_dict[uid].keys()))
    min_time=min(time_list); max_time=max(time_list)
    if max_time<=1534070000:
        DICT[2016].append(uid)
    if max_time<=1534100000 and  max_time>=1533300000:
        DICT[2017].append(uid)
    if max_time<=1535000000 and  max_time>=1534050000:
        DICT[2018].append(uid)
print(len(user_list))
print(len(DICT[2016]), DICT[2016])
print(len(DICT[2017]), DICT[2017])
print(len(DICT[2018]), DICT[2018])

Sess_D={2016:{},2017:{},2018:{}}
LDA_D={2016:{},2017:{},2018:{}}
Prob_D={2016:{},2017:{},2018:{}}
user_list = Sess_dict.keys()
for uid in user_list:
        if int(uid) in DICT[2016]:
            Sess_D[2016][uid]=Sess_dict[uid]; LDA_D[2016][uid]=LDA_dict[uid]; Prob_D[2016][uid]=Prob_dict[uid];
        if int(uid) in DICT[2017]:
            Sess_D[2017][uid] = Sess_dict[uid];LDA_D[2017][uid] = LDA_dict[uid];Prob_D[2017][uid] = Prob_dict[uid];
        if int(uid) in DICT[2018]:
            Sess_D[2018][uid] = Sess_dict[uid];LDA_D[2018][uid] = LDA_dict[uid];Prob_D[2018][uid] = Prob_dict[uid];
np.save(ROOT + str(2016) + "/Sess_dict.npy" , Sess_D[2016])
np.save(ROOT + str(2016) + "/LDA_dict.npy" , LDA_D[2016])
np.save(ROOT + str(2016) + "/Prob_dict.npy", Prob_D[2016])

np.save(ROOT + str(2017) + "/Sess_dict.npy" , Sess_D[2017])
np.save(ROOT + str(2017) + "/LDA_dict.npy" , LDA_D[2017])
np.save(ROOT + str(2017) + "/Prob_dict.npy", Prob_D[2017])

np.save(ROOT + str(2018) + "/Sess_dict.npy" , Sess_D[2018])
np.save(ROOT + str(2018) + "/LDA_dict.npy" , LDA_D[2018])
np.save(ROOT + str(2018) + "/Prob_dict.npy", Prob_D[2018])


#
#
# # CTP_dict={2016:{}, 2017:{}, 2018:{}}
# for tau in [3600*24]:#[3600*1, 3600*3, 3600*6]:
#     CTP_dict = {2016: {}, 2017: {}, 2018: {}}
#     # TISTP_dict_list = np.load(ROOT + "TISTP/STP_dict_%s.npy" % (tau)).item(0)
#     # TISTP_dict_list = np.load(ROOT + "CTP/2/STP_dict_%s.npy" % (tau)).item(0)
#     TISTP_dict_list = np.load(ROOT + "STP/STP_dict_%s.npy" % (tau)).item(0)
#
#     user_list = TISTP_dict_list.keys()
#     print(user_list)
#     for uid in user_list:
#         if int(uid) in DICT[2016]:
#             CTP_dict[2016][uid]=TISTP_dict_list[uid]
#         if int(uid) in DICT[2017]:
#             CTP_dict[2017][uid]=TISTP_dict_list[uid]
#         if int(uid) in DICT[2018]:
#             CTP_dict[2018][uid]=TISTP_dict_list[uid]
#     print(len(CTP_dict[2016]), len(CTP_dict[2017]), len(CTP_dict[2018]))
#     # np.save(ROOT+ str(2016) + "/TISTP/STP_dict_%s.npy" % (tau), CTP_dict[2016])
#     # np.save(ROOT+ str(2017) + "/TISTP/STP_dict_%s.npy" % (tau), CTP_dict[2017])
#     # np.save(ROOT+ str(2018) + "/TISTP/STP_dict_%s.npy" % (tau), CTP_dict[2018])
#     # np.save(ROOT+ str(2016) + "/CTP/2/STP_dict_%s.npy" % (tau), CTP_dict[2016])
#     # np.save(ROOT+ str(2017) + "/CTP/2/STP_dict_%s.npy" % (tau), CTP_dict[2017])
#     # np.save(ROOT+ str(2018) + "/CTP/2/STP_dict_%s.npy" % (tau), CTP_dict[2018])
#     np.save(ROOT + str(2016) + "/STP/STP_dict_%s.npy" % (tau), CTP_dict[2016])
#     np.save(ROOT + str(2017) + "/STP/STP_dict_%s.npy" % (tau), CTP_dict[2017])
#     np.save(ROOT + str(2018) + "/STP/STP_dict_%s.npy" % (tau), CTP_dict[2018])

# for uid in user_list:
#     stp_list = np.load(os.path.join(ROOT,"") + "STPSUPP_dict_%s.npy" % (uid))
#
# for key in [2016, 2017, 2018]:
#     stp_list = np.load(dir_ + "STPSUPP_dict_%s.npy" % (uid))