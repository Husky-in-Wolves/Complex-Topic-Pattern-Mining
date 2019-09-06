aHour=3600
#TI=[int(aHour*1),int(aHour*2),int(aHour*3),int(aHour*4),int(aHour*6),int(aHour*9)]
#TI=[int(aHour*0.25),int(aHour*0.5),int(aHour*1),int(aHour*2),int(aHour*3)]
TI=[aHour*1,aHour*3,aHour*6,aHour*9,aHour*12,aHour*24]
# TI=[1,2,3,4,5,6,7,8,100]


# class Prefix:
#     def __init__(self,tau,i,j,k,p):
#         self.sessID = i
#         self.tau=tau
#         self.next_pos=j
#         self.pos=k
#         self.prob=p

class Prefix_STP:
    def __init__(self,tau,pos,prob,time):
        self.tau=tau
        self.pos=pos
        self.prob=prob
        self.time=time

class Prefix_CTP:
    def __init__(self,tau,time_start,time_end,prob):
        self.tau=tau
        # self.pos_start=pos_start
        # self.pos_end=pos_end
        self.time_start=time_start
        self.time_end=time_end
        self.prob = prob

class STP_Supp:
    def __init__(self,ldaStr,tau,prob_list,supp,l,contain):
        self.ldaStr=ldaStr
        self.tau=tau
        self.prob_list=prob_list
        self.supp=supp
        self.len=l
        self.contain=contain