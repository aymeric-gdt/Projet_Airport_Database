from classes import AlwaysDataInterface
import os
from dotenv import load_dotenv
from datetime import datetime

def extract_data(file_path:str,_types:list[type]):

    with open(file_path,'r') as f:
        data = f.readlines()
        
    args = data.pop(0).replace('\n','').split(',')
    nb_args = len(args)
    list_values = list()
    
    for text in data:
        values = text.replace('\n','').split(',')
        for i in range(nb_args):
            try:
                if _types[i] is datetime:
                    values[i] = values[i].replace('Z','')
                    values[i] = values[i].split('T')
                    values[i][0] = values[i][0].split('-')
                    y,m,d = values[i][0]
                    values[i][1] = values[i][1].split(':')
                    h,mn,s = values[i][1]
                    values[i] = datetime(int(y),int(m),int(d),int(h),int(mn),int(s))
                else:
                    values[i] = _types[i](values[i])
            except Exception as e:
                values[i] = None
        list_values.append(tuple(values))
    
    return args, list_values


load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')

instance = AlwaysDataInterface(HOST, USER, PASSWORD, DATABASE)

# TABLE DES VOLS
# args, values = extract_data("./airport_data/flights.txt",[int,int,int,int,int,int,int,int,int,str,int,str,str,str,int,int,int,int,datetime])
# year,month,day,dep_time,sched_dep_time,dep_delay,arr_time,sched_arr_time,arr_delay,carrier,flight,tailnum,origin,dest,air_time,distance,hour,minute,time_hour
# planes = instance.custom_command('SELECT * FROM Plane')
# airports = instance.custom_command('SELECT * FROM Airport')

# for i in range(len(values)):
#     if values[i][11] not in [plane['tailnum'] for plane in planes]:
#         instance.insert_values('Plane',['tailnum'], [values[i][11]])
#         planes.append({'tailnum':values[i][11]})
#         print(f'avion manquant pour vol {values[i][11]}')
#     if values[i][12] not in [airport['faa'] for airport in airports]:
#         instance.insert_values('Airport',['faa'], [values[i][12]])
#         airports.append({'faa':values[i][12]})
#         print(f"aeroport d'origine manquant {values[i][12]}")
#     if values[i][13] not in [airport['faa'] for airport in airports]:
#         instance.insert_values('Airport',['faa'], [values[i][13]])
#         airports.append({'faa':values[i][13]})
#         print(f"aeroport de destination {values[i][13]}")
#     print(i)

# instance.insert_values('Flight',args, values)

# POUR LES AVIONS / LES AEROPORTS / LES COMPAGNIES AERIENNES

# args, values = extract_data("./airport_data/données.txt",[str,int,float,datetime])

# TABLE DES RAPPORTS METEO
# origin,year,month,day,hour,temp,dewp,humid,wind_dir,wind_speed,wind_gust,precip,pressure,visib,time_hour

# temp_args, temp_values = extract_data("./airport_data/weather.txt",[str,int,int,int,int,float,float,float,int,float,float,float,float,float,datetime])
# values = list()
# args = list()
# args.append('id')
# airports = instance.custom_command('SELECT * FROM Airport')

# for i in range(len(values)):
#     if values[i][0] not in [airport['faa'] for airport in airports]:
#         instance.insert_values('Airport',['faa'], [values[i][0]])
#         airports.append({'faa':values[i][0]})
#         print(f"aeroport d'origine manquant {values[i][0]}")
#     print(i)

# for i in range(len(temp_args)):
#     if temp_args[i] != 'year' and temp_args[i] != 'month' and temp_args[i] != 'day' and temp_args[i] != 'hour':
#         args.append(temp_args[i])

# for i in range(len(temp_values)):
#     value = list()
#     value.append(temp_values[i][0] + '-' + str(temp_values[i][1]) + '-' + str(temp_values[i][2]) + '-' + str(temp_values[i][3]) + '-' + str(temp_values[i][4]))
#     value.append(temp_values[i][0])
#     value.append(temp_values[i][5])
#     value.append(temp_values[i][6])
#     value.append(temp_values[i][7])
#     value.append(temp_values[i][8])
#     value.append(temp_values[i][9])
#     value.append(temp_values[i][10])
#     value.append(temp_values[i][11])
#     value.append(temp_values[i][12])
#     value.append(temp_values[i][13])   
#     value.append(temp_values[i][14])

#     values.append(value)

instance.insert_values('Weather',args, values)

# print(args)
# print(values)
#instance.insert_values('test',args, values)
#print(instance.custom_command('SELECT * FROM Airport WHERE'))
instance.close_connection()