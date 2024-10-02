from classes import AlwaysDataInterface
import os
from dotenv import load_dotenv

dict_conv = {
    'str':lambda text:text,
    'int':lambda text:int(text),
    'float':lambda text:float(text),
    'bool':lambda text:int(text),
}

def extract_data(file_path:str,conv:list[str]):
    formater = []
    for type_col in conv:
        formater.append(dict_conv[type_col])

    with open(file_path,'r') as f:
        data = f.readlines()
        
    args = data.pop(0).replace('\n','').split(',')
    nb_args = len(args)
    list_values = list()
    
    for text in data:
        values = text.replace('\n','').split(',')
        for i in range(nb_args):
            values[i] = formater[i](values[i])
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
#args, values = extract_data("./airport_data/test.txt",['int','str','float','bool'])
#print(args)
#print(values)
#instance.insert_values('test',args, values)
instance.close_connection()