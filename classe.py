import pymysql

class APIAlwaysData:

    def __init__(self, host:str, user:str, password:str, database:str):
        try:
            # Connexion à la base de données
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Connexion réussie à la base de données.")

        except Exception as e:
            print("Erreur lors de la connexion :", e)
            exit()

    def __request(self,command:list, getOrInsert:bool):
        with self.connection.cursor() as cursor:
            if getOrInsert is False:
                cursor.execute(command[0])  # Remplace par ta requête
                return cursor.fetchall()
            elif getOrInsert is True:
                try :
                    cursor.executemany(command[0],command[1])
                    self.connection.commit()
                    print("Insertion de valeurs réussie.")
                except Exception as e:
                    print(f"Erreur survenue : {e}")


    def get_table(self,table_name:str):
        return self.__request([f"SELECT * FROM {table_name}"], False)

    def insert_values(self, table_name:str, args:list[str], values:list[tuple]):
        a = "%s"
        for i in range(len(args)-1):
            a += ", %s"
        command = list()
        command.append(f"INSERT INTO {table_name} ({", ".join(args)}) VALUES ({a})")
        command.append(values)
        self.__request(command, True)

    def close_connection(self):
        """Fermer la connexion établit avec la Database"""
        if self.connection:
            self.connection.close()
            print("Connexion fermée.")