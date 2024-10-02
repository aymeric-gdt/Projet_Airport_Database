import pymysql
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
DATABASE = os.getenv('DATABASE')

class AlwaysDataInterface:

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


class MySQLDataApp:
    temp_connect = None
    temp_data = None
    def __init__(self):
        self.title = "WebApp de Visualisation des Données MySQL"
        self.description = "Connectez-vous à une base de données MySQL et visualisez les données."
        print('Inits')

    def display_title(self):
        st.title(self.title)

    def display_description(self):
        st.write(self.description)

    def connect_to_db(self, host, user, password, database):
        try:
            MySQLDataApp.temp_connect = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            st.success("Connexion réussie à la base de données !")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

    def input_db_credentials(self):
        st.sidebar.subheader("Détails de connexion à la base de données")
        host = st.sidebar.text_input("Hôte", HOST)
        user = st.sidebar.text_input("Utilisateur", USER)
        password = st.sidebar.text_input("Mot de passe", type="password", value=PASSWORD)
        database = st.sidebar.text_input("Base de données", DATABASE)

        if st.sidebar.button("Se connecter"):
            self.connect_to_db(host, user, password, database)

    def execute_query(self):
        print("test")
        print(MySQLDataApp.temp_connect)
        if MySQLDataApp.temp_connect:
            query = st.text_area("Entrez une requête SQL", "SELECT * FROM votre_table LIMIT 100;")
            if st.button("Exécuter la requête"):
                print("bouton pressé")
                try:
                    MySQLDataApp.temp_data = pd.read_sql(query, MySQLDataApp.temp_connect)
                    st.success("Requête exécutée avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de la requête : {e}")
        else:
            st.warning("Veuillez vous connecter à la base de données avant d'exécuter une requête.")

    def display_data(self):
        if MySQLDataApp.temp_data is not None and not MySQLDataApp.temp_data.empty:
            st.subheader("Aperçu des Données")
            st.write(MySQLDataApp.temp_data.head())

            st.subheader("Description Statistique")
            st.write(MySQLDataApp.temp_data.describe())
        else:
            st.warning("Aucune donnée à afficher. Exécutez une requête pour récupérer les données.")

    def plot_data(self):
        if MySQLDataApp.temp_data is not None and not MySQLDataApp.temp_data.empty:
            columns = MySQLDataApp.temp_data.columns.tolist()
            
            st.subheader("Visualisation de données")
            x_axis = st.selectbox("Sélectionnez la colonne pour l'axe X", columns)
            y_axis = st.selectbox("Sélectionnez la colonne pour l'axe Y", columns)

            if st.button("Tracer le graphique"):
                fig, ax = plt.subplots()
                ax.plot(MySQLDataApp.temp_data[x_axis], MySQLDataApp.temp_data[y_axis], marker='o')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                ax.set_title(f"Graphique de {y_axis} en fonction de {x_axis}")
                st.pyplot(fig)
        else:
            st.warning("Veuillez exécuter une requête pour visualiser les données.")

    def run(self):
        self.display_title()
        self.display_description()
        self.input_db_credentials()
        self.execute_query()
        self.display_data()
        self.plot_data()
