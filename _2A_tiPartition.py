import numpy as np

# data_dict=np.load("new-data/data_dict.npy").item(0)

root="new-data-russian/"
result={}
COUNT=0
LDA_dict=np.load(root+"LDA_dict.npy").item(0)
'''
#算法2:   tiPartition(TDSu; hts)
# 对于每个用户，先按时间间隔切割出多个session,默认的时间间隔是5小时=18000,
# 此处有一个超参数： hts=切割session的时间间隔
# session_list:记录每段session的开始位置 和 结束位置（不包含）
'''


def tiPartition(uid,hts,minlen=5):
    session_list=[]
    prev_time=min(list(LDA_dict[uid].keys()))
    start=0
    for i,time in enumerate(sorted(list(LDA_dict[uid].keys()))):
        #如果大于时间间隔，则开启一个新的session,将旧session保存
        if time-prev_time>=hts:
            end=i
            if end-start >= minlen:
                session_list.append((start,end))
            start=i
        prev_time=time
    #遍历到最后 把最后一条session加入到列表
    if i+1-start >= minlen:
        session_list.append((start, i+1))
    return session_list

def add2dict(uid,hts,minLen,minNum):
    global COUNT
    time_list = sorted(list(LDA_dict[uid].keys()))
    session_list = tiPartition(uid, hts, minlen=minLen)
    dict_ = {}
    #################如果session个数小于3，则此用户作废 从Sess中删除该用户##################
    #prob和lda中的仍是全部用户，故之后不能做用户列表
    if len(session_list) >= minNum:
        for i, x in enumerate(session_list):
            sess = time_list[x[0]:x[-1]].copy()
            dict_[i] = sess
            #结果统计
            if len(sess) not in result.keys():
                result[len(sess)]=0
            result[len(sess)] += 1
            COUNT+=1

    print(uid, dict_)
    return dict_

if __name__ =='__main__' :
    uid_list=sorted(list(LDA_dict.keys()))
    Sess_dict={}
    count=0
    # 串行执行
    for uid in uid_list:
        if len(LDA_dict[uid].keys())>0:
            count += len(LDA_dict[uid].keys())
            if uid > 30000:
                dict_ = add2dict(uid, hts=3600 * 6, minLen=6,minNum=6)
            if uid < 30000:
                dict_ = add2dict(uid, hts=3600 * 3, minLen=6,minNum=8)

            #################如果len(session_list)小于3，则此用户作废##################
            if len(dict_.keys()):
                Sess_dict[uid] = dict_

    print(count)
    np.save(root+"Sess_dict.npy", Sess_dict)
    result=sorted(result.items(), key=lambda e: e[0], reverse=False)
    print(result,COUNT)
    print(len(Sess_dict.keys()),len([u for u in Sess_dict.keys() if u<30000]))


