from classes import AlwaysDataInterface
import os
from dotenv import load_dotenv

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
                values[i] = _types[i](values[i])
            except:
                values[i] = None
        list_values.append(tuple(values))
    
    return args, list_values


load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')

instance = AlwaysDataInterface(HOST, USER, PASSWORD, DATABASE)
table_test = instance.get_table("test")
print(table_test)
args, values = extract_data("./airport_data/planes.txt",[str,int,str,str,str,int,int,str,str])
instance.insert_values('planes')
print(args)
print(values)
#instance.insert_values('test',args, values)
instance.close_connection()