# -*- coding: utf-8 -*-
import time
import numpy as np
import pandas as pd
#cut subline from line
def str_cut(str,start,end):
    line = ''
    for i in range(start,end,1):
        line += str[i]
    return line
#change format of time value from hh:mm:ss to ss
def time_to_sec(t_name):
    n = t_name.split(':')
    if(int(n[0]) < 12):
        n[0] = str(int(n[0]) + 24)
    return int(n[0]) * 3600 + int(n[1]) * 60 + int(n[2])
#change format of time value from ss to hh:mm:ss
def sec_to_time(t_sec):
    def t_c(t):
        if(t<10):
            t = f'0{t}'
        return t
    h = t_sec // 3600
    m = (t_sec - h*3600) // 60
    s = t_sec - h*3600 - m*60
    if(h >= 24):
        h = h % 24
    h,m,s = t_c(h),t_c(m),t_c(s)
    return f'{h}:{m}:{s}'
#filepath
save_path = r'C:\Users\lrikozavr\work\LAO'
file_path_fcu = r'C:\Users\lrikozavr\work\LAO\train0718.fcu'
file = f'{file_path_fcu}'
#PC time now
t = time.localtime()
localtime = time_to_sec(time.strftime("%H:%M:%S", t))
#list of parametrs to read loop
name_line = 'ЭФЕМЕРИДЫ ПО ОБЪЕКТУ:'
satelite_number = ''
flag_data = 0
flag_time_period_start = 0
flag_time_period_end = 1
#
UTC = sec_to_time(localtime)
#
data = []
timemass = []
timeline = ''
timelinemass = []
#read file and make two massive
def join(mass):
    line = ''
    for i in range(len(mass)):
        if(i < len(mass)-1 ):
            line += str(mass[i]) + ','
        else: line += str(mass[i])
    return line
##########################################
#index_1 = 0
##########################################
for line in open(file, encoding = 'Windows-1251'):
    if(line == '\n'):
        if(flag_data):
            timelinemass.append(time_to_sec(UTC))
            timeline = join(timelinemass)
            if(len(timelinemass) > 1):
                timemass.append(np.array([satelite_number,timeline]))
            timelinemass = []
            flag_data = 0
            flag_time_period_end = 1
            flag_time_period_start = 0
            '''
            index_1 += 1
            if(index_1 == 4):
                print(timemass)
                exit()
            '''
        continue
    if(line.split('  ')[0] == name_line):
        n = line.split('  ')
        satelite_number = n[1]
        continue
    if(line.startswith('   Date')):
        flag_data = 1
        continue
    if(flag_data):
        UTC_label = str_cut(line,12,20)
        d_UTC_temp = time_to_sec(UTC_label) - time_to_sec(UTC)
        if(abs(d_UTC_temp) > 10 and flag_time_period_start):
            timelinemass.append(time_to_sec(UTC))
            flag_time_period_end = 1
            flag_time_period_start = 0
        #UTC = time_to_sec(UTC_label)
        UTC = UTC_label
        Mag = float(str_cut(line,108,111))
        Az = float(str_cut(line,78,85))
        Um = float(str_cut(line,86,92))        
        data.append(np.array([satelite_number,time_to_sec(UTC),Az,Um,Mag])) #UTC
        if(flag_time_period_end):
            timelinemass.append(time_to_sec(UTC))
            flag_time_period_end = 0
            flag_time_period_start = 1
##########################################
#f1 = open('timemass.txt','w')
#f2 = open('data.txt','w')
#print(timemass)
#print(len(timemass))
#f1.write(print(timemass))
#f2.write(print(data))
data = pd.DataFrame(np.array(data),columns=['name','time','mag','Az','Um'])
##########################################
count_satelite = len(timemass)
print(count_satelite)
##########################################
timelinemass = []
for i in range(count_satelite):
    name = timemass[i][0]
    n = timemass[i][1].split(',')
    count = int(len(n) / 2)
    for j in range(len(n)):
        if((j+2) % 2 == 0):
            timelinemass.append(np.array([name, n[j], 1, count]))
        else: timelinemass.append(np.array([name, n[j], -1, count])) # (j+2) // 2
##########################################
timelinemass = pd.DataFrame(np.array(timelinemass), columns = ['name','time','flag_1','flag_n'])
#print(timelinemass)
#exit()
#timelinemass.to_csv('sort.txt')
##########################################
# make 'flag_d', namely density overlap
def process_1(timelinemass):
    timelinemass = timelinemass.sort_values(by=['time'],ignore_index=True)
    #print(timelinemass)
    #print(int(timelinemass['flag_1'][0]))
    if(len(timelinemass) > 0):
        time_density = [int(timelinemass['flag_1'][0])]
        s=int(timelinemass['flag_1'][0])
        for i in range(len(timelinemass)):
            if(not i==0):
                s+=int(timelinemass['flag_1'][i])
                time_density.append(s)
        timelinemass['flag_d'] = time_density
    return timelinemass
    
    #return time_density
#print(time_density)
##########################################
# separate not overlap satelite time and overlap
def process_2(timelinemass):
    data_time = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    data_time_process = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    flag_data = 0
    data_satelite_name = []
    timelinemass = process_1(timelinemass)
    for i in range(1,len(timelinemass),1):
        if(flag_data):
            flag_data = 0
            continue
        temp = pd.concat([timelinemass.iloc[[i-1]],timelinemass.iloc[[i]]], ignore_index=True)
        if(abs(timelinemass['flag_d'][i-1]) == 1 and timelinemass['flag_d'][i] == 0 and timelinemass['name'][i-1] == timelinemass['name'][i]):
            data_time = pd.concat([data_time,temp], ignore_index=True)
            flag_name = 1
            if( len(data_satelite_name) > 0 ):
                for ii in range(len(data_satelite_name)):
                    if (data_satelite_name[ii][0] == timelinemass['name'][i]):
                        data_satelite_name[ii][1] += 1
                        flag_name = 0
                if(flag_name):
                    data_satelite_name.append([timelinemass['name'][i],1])
            else: data_satelite_name.append([timelinemass['name'][i],1])
            flag_data = 1
        else:
            data_time_process = pd.concat([data_time_process,temp], ignore_index=True)
            flag_data = 1
    #print(data_satelite_name)
    #exit()
    
    #data_time_process.loc[data_time_process['name'] == data_satelite_name[i][0]]

    #for i in range(len(data_satelite_name)):
    #    ['flag_n'] -= data_satelite_name[i][1]
    
    #print(data_satelite_name)
    #data_time_process_1 = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    '''    
    for i in range(len(data_time_process)):
        flag_1 = 0
        if(len(data_satelite_name) > 0):
            for name in data_satelite_name:
                if(data_time_process['name'][i] == name):
                    flag_1 = 1
        if(flag_1 == 0):
            data_time_process_1 = pd.concat([data_time_process_1,data_time_process.iloc[[i]]], ignore_index=True)
    '''    
    #print(data_time_process_1)
    
    #data_time_process = data_time_process_1
    '''
    if(len(data_satelite_name) > 0):
        data_time_1,data_time_process = process_2(data_time_process)
        process_1(data_time_process)
        data_time = pd.concat([data_time,data_time_1],ignore_index=True)
    '''
    #print(data_time)
    #print(data_time_process)
    #data_time_process.to_csv(f'{save_path}/data_time_process.csv')
    #exit()

    return data_time,data_time_process

# separate unite overlap satelite time to not overlap 
def drawbridges(data):
    mass = []
    time_1,time_2,d_time,name = 0,0,0,0
    def d_t(mass,index):
        mass[index][3] = int(mass[index][1]) - int(mass[index][2])
        
    for j in range(len(data)):
        if(int(data['flag_1'][j]) == 1):
            #print('llll')
            time_1 = data['time'][j]
            name = data['name'][j]
            for jj in range(j,len(data),1):
                if(data['name'][jj] == name and int(data['flag_1'][jj]) == -1):
                    time_2 = data['time'][jj]
                    break
            d_time = int(time_2) - int(time_1)
            mass.append([name,time_1,time_2,d_time])

    def ap_line(data_time,mass,i):
        line1 = [mass[i][0],mass[i][1],1,1,1]
        line2 = [mass[i][0],mass[i][2],-1,1,0]
        #print(pd.DataFrame(np.array([line1])))
        data_time = pd.concat([data_time,pd.DataFrame(np.array([line1]),columns=['name','time','flag_1','flag_n','flag_d'])],ignore_index=True)
        data_time = pd.concat([data_time,pd.DataFrame(np.array([line2]),columns=['name','time','flag_1','flag_n','flag_d'])],ignore_index=True)
        return data_time        

    def ladder(mass):
        d = int(mass[len(mass)-1][2]) - int(mass[0][1])
        sum = 0
        a = []
        for i in range(len(mass)):
            sum += int(mass[i][2]) - int(mass[i][1])
        for i in range(len(mass)-1):
            a.append(int(int(mass[i][1]) + (int(mass[i][2]) - int(mass[i][1]))*d / sum))
        
        for i in range(len(mass)-1):
            mass[i][2] = str(a[i] - 1)
            mass[i+1][1] = str(a[i])
        
        data_time = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
        for i in range(len(mass)):
            data_time = ap_line(data_time,mass,i)
        #print(data_time)
        #data_time = process_1(data_time)
        return data_time

    def simple_first(mass):
        data_time = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
        temp_time = 0
        for i in range(len(mass)):
            if(mass[i][0] == '0'):
                continue
            data_time = ap_line(data_time,mass,i)
            for ii in range(i,len(mass),1):
                if(mass[i][2] >= mass[ii][2]):
                    mass[ii][0] = '0'
                elif(mass[i][2] > mass[i][1]):
                    mass[ii][1] = mass[i][2]
                    d_t(mass,ii)
            '''
            if( mass[i][3] > mass[i+1][3] ):
                if(mass[i][2] > mass[i+1][2]):
                    #data_time = ap_line(data_time,mass,i)
                    temp_time = mass[i][2]
                    mass[i+1][0] = '0'
                else:
                    mass[i+1][1] = mass[i][2]
                    d_t(mass,i+1)
            else:
            '''                    
        return data_time
    #data_time = ladder(mass)
    data_time = simple_first(mass)
    
    #print(data_time)
#    for i in range(len(data)):
#        data['time'][i]
    return data_time

# separate mass of overlap satelite time to one overlap unite
def split_data(data):
    data_process = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    data_process_1 = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    for i in range(len(data)):
        data_process = pd.concat([data_process,data.iloc[[i]]], ignore_index=True)
        if(int(data['flag_d'][i]) == 0):
            #print(data_process)
            data_process = drawbridges(data_process)
            #print(data_process)
            data_process_1 = pd.concat([data_process_1,data_process], ignore_index=True)
            data_process = pd.DataFrame(columns=['name','time','flag_1','flag_n','flag_d'])
    return data_process_1


data_time,data_time_process = process_2(timelinemass)

#print(data_time_process)
data_time_process = split_data(data_time_process)
#print(data_time_process)
data_time = pd.concat([data_time,data_time_process], ignore_index=True)
#data_time = process_1(data_time)
a1,a2 = process_2(data_time)
#print(a2)
#print(a1)
'''
for i in range(len(a1)):
    flag = 0
    index = 0
    for j in range(i,len(a1),1):
        if(a1['name'][i] == a1['name'][j]):
            index = j
            flag+=1
    if(flag>2):
        print(a1['name'][i], index, i)
'''
#print(data)
#print(a1)
#print(data_time)
#print(data_time_process)

#прибрати дублікати - поки нема такої потреби

def satelite_process_1(data,data_time):
    data_new = pd.DataFrame()
    for j in range(len(data_time)):
        data_new_temp = pd.DataFrame()
        if(data_time['flag_d'][j]):
            continue
        for i in range(len(data)):
            if(data['time'][i] > data_time['time'][j-1]  and  data['time'][i] < data_time['time'][j]):
                data_new_temp = pd.concat([data_new_temp,data.iloc[[i]]],ignore_index=True)
        data_new = pd.concat([data_new,data_new_temp],ignore_index=True)
    return data_new

name = data['name'][0]
data_temp = pd.DataFrame()
data_new = pd.DataFrame()
for i in range(len(data)):
    if(data['name'][i] == name):
        data_temp = pd.concat([data_temp,data.iloc[[i]]], ignore_index=True)
    else:
        data_time_temp = pd.DataFrame()
#        index = 0
        for j in range(len(a1)): #a1 - massive
#            if(index == 2):
#                break
            if(a1['name'][j] == name):
                data_time_temp = pd.concat([data_time_temp,a1.iloc[[j]]],ignore_index=True)
#                index += 1   
        data_new = pd.concat([data_new,satelite_process_1(data_temp,data_time_temp)],ignore_index=True)
        data_temp = pd.DataFrame()        
        name = data['name'][i]

#data.to_csv(f'{save_path}/data.csv')
data_new = data_new.sort_values(by='time',ignore_index=True)
data = data_new
#print(data)

localtime = 60000

#print(data_new)
#data_new.to_csv(f'{save_path}/text.csv')    
#exit()

shoot = 30
calibr = 5
const_3 = 8

def dots_1(Az0,Az1,Um0,Um1,time0,time1):
    def Az_format(az):
        if(az >= 0 and az <= 180):
            az = abs(az - 180)
        else:
            az = abs(az - 540)
        return az
    Az0 = Az_format(Az0)
    Az1 = Az_format(Az1)
    delta_t = abs(Az1 - Az0)*0.5 + abs(Um1 - Um0)*0.5 + shoot + const_3 + calibr - (time1 - time0)
#    delta_t = abs(Az1 - Az0)*0.5 + abs(Um1 - Um0)*0.5  + 4 - (time1 - time0)
    if(delta_t <= 0):
        flag = 1
    else: flag = 0
    return flag,-delta_t        


Az0,Um0,time0 = 0,0,localtime
print(localtime)
data_new = pd.DataFrame()
for i in range(len(data)):
    Az1,Um1,time1 = float(data['Az'][i]),float(data['Um'][i]),int(data['time'][i])
    flag,delta_t = dots_1(Az0,Az1,Um0,Um1,time0,time1)
    if(flag):
        temp = pd.DataFrame(np.array([[data['name'][i],Az1,Um1,time1,delta_t]]),columns=['name','Az','Um','time','delta_t'])
        data_new = pd.concat([data_new,temp], ignore_index=True)
        Az0,Um0,time0 = Az1,Um1,time1
    
print(data_new)

data_new.to_csv(f'{save_path}/final_data.csv')

#точка перегину 180, якщо менше 180 йде до більше 180, то рахується шлях через зменшення.