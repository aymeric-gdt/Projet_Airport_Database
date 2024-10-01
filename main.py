from classe import APIAlwaysData

def extract_data(file_path:str):
    with open(file_path,'r') as f:
        data = f.readlines()
    args = data.pop(0).replace('\n','').split(',')
    values = list()
    for text in data:
        values.append(text.replace('\n','').split(','))


host = 'mysql-zaahn.alwaysdata.net'  # Remplace par ton hôte
user = 'zaahn_aymeric'        # Remplace par ton nom d'utilisateur
password = 'fdb7H=a0%D_,wZaU'   # Remplace par ton mot de passe
database = 'zaahn_airport' # Remplace par le nom de ta base de données

instance = APIAlwaysData(host, user, password, database)
table_test = instance.get_table("test")
print(table_test)
#instance.insert_values("test",[''])
extract_data("./test.txt")
instance.close_connection()