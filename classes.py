import pymysql
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
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


    def custom_command(self, command, getOrInsert=False):
        return self.__request([command],getOrInsert)
    
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
    temp_data = {}
    def __init__(self):
        self.title = "WebApp de Visualisation des Données MySQL"
        self.description = "Connectez-vous à une base de données MySQL et visualisez les données."

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
        if MySQLDataApp.temp_connect:
            query = st.text_area("Entrez une requête SQL", "SELECT * FROM test;")
            if st.button("Exécuter la requête"):
                try:
                    MySQLDataApp.temp_data['tab1'] = pd.read_sql(query, MySQLDataApp.temp_connect)
                    st.success("Requête exécutée avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de la requête : {e}")
        else:
            st.warning("Veuillez vous connecter à la base de données avant d'exécuter une requête.")

    def display_data(self,context='tab1'):
        data = MySQLDataApp.temp_data.get(context, None)
        if data is not None and not data.empty:
            st.subheader("Aperçu des Données")
            st.write(data.head())

            st.subheader("Description Statistique")
            st.write(data.describe())
        else:
            st.warning("Aucune donnée à afficher. Exécutez une requête pour récupérer les données.")

    def plot_data(self, context='tab1'):
        data = MySQLDataApp.temp_data.get(context, None)
        if data is not None and not data.empty:
            columns = data.columns.tolist()
            
            st.subheader("Visualisation de données")
            x_axis = st.selectbox("Sélectionnez la colonne pour l'axe X", columns)
            y_axis = st.selectbox("Sélectionnez la colonne pour l'axe Y", columns)

            if st.button("Tracer le graphique"):
                fig, ax = plt.subplots()
                ax.plot(data[x_axis], data[y_axis], marker='o')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                ax.set_title(f"Graphique de {y_axis} en fonction de {x_axis}")
                st.pyplot(fig)
        else:
            st.warning("Veuillez exécuter une requête pour visualiser les données.")
    
    def hist_data(self, labels, sizes, title, details=20):
        st.subheader(title)
        # plot
        fig, ax = plt.subplots()

        ax.bar(labels, sizes, width=1, edgecolor="white", linewidth=0.7)
        ax.set(ylim=(0, sizes.max()), yticks=np.arange(1, sizes.max(),sizes.max()//details))
        
        plt.xticks(rotation=90)

        st.pyplot(fig)
    
    def pie_chart(self, labels, sizes, colors, title):

        # Titre pour le graphique
        st.subheader(title)

        # Générer le camembert avec Matplotlib
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Assurer que le camembert est bien circulaire

        # Afficher le camembert dans Streamlit
        st.pyplot(fig)
    
    def questions(self, context="q1"):
        if MySQLDataApp.temp_connect:
            st.subheader(f"Requêtes {context}")
            querys = []
            match context:
                case "q1":
                    querys.append(st.text_area("nombre d'aéroports", "SELECT COUNT(*) AS nb_airports FROM Airport;"))
                    querys.append(st.text_area("nombre d'aéroports de départ", "SELECT COUNT(DISTINCT origin) AS nb_origin_airport FROM Flight;"))
                    querys.append(st.text_area("nombre d'aéroports de destination", "SELECT COUNT(DISTINCT dest) AS nb_dest_airports FROM Flight;"))
                    querys.append(st.text_area("nombre de fuseaux horaire ne passant pas à l'heure d'été", 'SELECT COUNT(faa) FROM Airport WHERE dst = "N";'))
                    querys.append(st.text_area("nombre de fuseaux horaire différents", "SELECT COUNT(DISTINCT tzone) AS nb_unique_fuseaux FROM Airport;"))
                    querys.append(st.text_area("nombre de compagnies", "SELECT COUNT(carrier) AS nb_compagnies FROM Airline;"))
                    querys.append(st.text_area("nombre d'avions", "SELECT COUNT(tailnum) AS nb_avions FROM Plane;"))
                    querys.append(st.text_area("nombre de vols annulés", "SELECT COUNT(id) as nb_vols_annules FROM Flight WHERE air_time is null AND arr_time is NULL;"))
                case "q2":
                    querys.append(st.text_area("aéroport de départ le plus emprunté", "SELECT count(*)as departs, Airport.name FROM Flight INNER JOIN Airport ON Airport.faa = Flight.origin GROUP BY origin ORDER BY Flight.origin ASC LIMIT 1;"))
                    querys.append(st.text_area("fréquentation aéroports", "SELECT COUNT(Flight.dest) as arrivee, Airport.name FROM Flight INNER JOIN Airport ON Airport.faa = Flight.dest GROUP BY Airport.faa ORDER BY `arrivee` DESC;"))
                    querys.append(st.text_area("nombre de vols part d'avions", "SELECT COUNT(Flight.tailnum) as vols, Plane.tailnum FROM Flight INNER JOIN Plane ON Plane.tailnum = Flight.tailnum GROUP BY Plane.tailnum ORDER BY `vols` DESC;"))
                case "q3":
                    querys.append(st.text_area("nombre de destination uniques desservis par chaque Airline", "SELECT COUNT(DISTINCT Flight.dest) as Destinations, Airline.Name FROM Flight INNER JOIN Airline on Airline.carrier = Flight.carrier GROUP BY Airline.carrier;"))
                    querys.append(st.text_area("nombre de destination desservis par chaque Airlines depuis chaque aéroports de départs.","SELECT COUNT(DISTINCT Flight.dest) as Destinations, Airline.Name as Airline_name, Airport.name as Airport_name FROM Flight INNER JOIN Airline on Airline.carrier = Flight.carrier INNER JOIN Airport ON Airport.faa = Flight.origin GROUP BY Airline.carrier, Airport.name;"))
                case "q4":
                    querys.append(st.text_area("Liste des vols ayant atterri a Houston (IAH ou HOU)", 'SELECT Flight.id, Airport.name, Flight.dest, Flight.origin, Flight.tailnum FROM Airport INNER JOIN Flight ON Flight.dest = Airport.faa WHERE Flight.arr_time is not NULL AND Flight.dest = "IAH" OR Flight.dest = "HOU" ORDER BY Flight.id ASC'))
                    querys.append(st.text_area("Nombre d'airline desservant Seattle(LKE, SEA et BFI)", 'SELECT COUNT(DISTINCT Flight.carrier) as numberCarrier FROM Flight WHERE (dest="LKE" or dest="SEA" or dest="BFI");'))
                    querys.append(st.text_area("Nombre d'avions uniques desservant Seattle(LKE, SEA et BFI)", 'SELECT COUNT(DISTINCT Flight.tailnum) as uniqPlane FROM Flight WHERE (dest="LKE" or dest="SEA" or dest="BFI");'))
                    querys.append(st.text_area("Nombre de vols partant de NYC Airports (JFK, LGA et EWR) allant vers Seattle (LKE, SEA et BFI)", 'SELECT COUNT(*) AS vol_nyc_seattle FROM Flight WHERE (dest="LKE" or dest="SEA" or dest="BFI") AND (origin = "JFK" or origin = "LGA" or origin = "EWR");'))
                    #querys.append(st.text_area("", ''))
                case "q5":
                    querys.append(st.text_area("Nombre de vols par destination classé par le nom de la destination, ordre alphabétique", 'SELECT COUNT(*) as nb_vols, Destination.name as DestinationName FROM Flight INNER JOIN Airport as Destination ON Destination.faa = Flight.dest GROUP BY Flight.dest ORDER BY DestinationName;'))
                case "q6":
                    querys.append(st.text_area("Liste des Airlines avec le nombre de aéroports d'origines d'ou elles opérent", 'SELECT COUNT(DISTINCT Flight.origin) AS Origins, Airline.name, Airline.carrier FROM Airline INNER JOIN Flight ON Flight.carrier = Airline.carrier GROUP BY Airline.carrier ORDER BY Origins;'))
                    querys.append(st.text_area("Liste des origines de chaque Airline classé par Airline ", "SELECT DISTINCT Flight.origin AS Origins, Airline.name FROM Airline INNER JOIN Flight ON Flight.carrier = Airline.carrier ORDER BY Flight.Carrier;"))
                    querys.append(st.text_area("Liste des destinations de chaque Airline classé par Airline", 'SELECT DISTINCT Flight.dest , Airline.name FROM Airline INNER JOIN Flight ON Flight.carrier = Airline.carrier ORDER BY Flight.Carrier;'))
                case "q7":
                    querys.append(st.text_area("Aéroport(destination) monopolisé par une Airline", 'SELECT Airport.name as airport_name, Airline.name as airline_name FROM Flight INNER JOIN Airport ON Airport.faa = Flight.dest INNER JOIN Airline ON Airline.carrier = Flight.carrier GROUP BY Flight.dest HAVING COUNT(DISTINCT Flight.carrier) = 1;'))
                case "q8":
                    querys.append(st.text_area("Filtrage des vols par American, Delta ou United", 'SELECT * FROM `Flight` WHERE carrier = "AA" or carrier = "DL" or carrier = "UA";'))

            if st.button(f"Executer requêtes {context}"):
                try:
                    MySQLDataApp.temp_data[context] = []
                    for query in querys:
                        MySQLDataApp.temp_data[context].append(pd.read_sql(query, MySQLDataApp.temp_connect))
                    st.success("Requêtes exécutées avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de l'exécution de la requête : {e}")
                    
        else:
            st.warning("Veuillez vous connecter à la base de données avant toutes choses.")
    
    def reponses(self, context="q1"):
        data = MySQLDataApp.temp_data.get(context)
        if data is not None:
            st.subheader(f"Réponses requêtes {context}")
            match context:
                case "q1": # Affichage simple
                    for d in data:
                        st.write(d)
                case "q2": # Affichage *
                    st.write(data[0])
                    nb_vols = data[1]["arrivee"].sum()
                    
                    premiers = data[1].head(10)
                    derniers = data[1].tail(10)
                    premiers.loc[11] = [nb_vols-(premiers["arrivee"].sum()),'Autres']
                    derniers.loc[11] = [nb_vols-(derniers["arrivee"].sum()), 'Autres']
                    
                    pourcentages_premiers = []
                    pourcentages_derniers = []

                    for row in premiers.itertuples():
                        pourcentages_premiers.append((row.arrivee/nb_vols)*100)
                    for row in derniers.itertuples():
                        pourcentages_derniers.append((row.arrivee/nb_vols)*100)
                    
                    labels_premiers = premiers['name']
                    labels_derniers = derniers['name']
                    
                    colors = [
                                "#FF5733",  # Rouge vif
                                "#33FF57",  # Vert vif
                                "#3357FF",  # Bleu vif
                                "#F1C40F",  # Jaune
                                "#8E44AD",  # Violet
                                "#E74C3C",  # Rouge foncé
                                "#3498DB",  # Bleu clair
                                "#2ECC71",  # Vert clair
                                "#E67E22",  # Orange
                                "#1ABC9C",  # Turquoise
                                "#C0392B"   # Rouge sombre
                            ]
                    
                    self.pie_chart(labels_premiers,pourcentages_premiers,colors,'q2 parts des 10 aéroports les plus prisés')
                    self.pie_chart(labels_derniers,pourcentages_derniers,colors,'q2 parts des 10 aéroports les moins prisés')
                    st.text(f"{context} avions ayants le plus volé")
                    st.write(data[2].head(10))
                    st.text(f"{context} avions ayants le moins volé")
                    st.write(data[2].tail(10))
                case "q3":
                    self.hist_data(data[0]["Name"],data[0]["Destinations"],"Nombre de destination uniques desservis par chaque Airline")
                    airport_list = data[1]['Airport_name'].unique().tolist()
                    selected_airport = st.selectbox('Sélectionnez un aéroport', airport_list)
                    filtered_data = data[1][data[1]['Airport_name'] == selected_airport]
                    self.hist_data(filtered_data["Airline_name"], filtered_data["Destinations"],f"Nombre de destination desservis par chaque Airlines depuis {selected_airport} (départs)")
                case "q4":
                    for i in range(len(data)):
                        st.write(data[i])
                case "q5":
                    st.text("Nombre de vols par destination (classé par ordre alphabétique)")
                    st.write(data[0])
                case "q6":
                    self.hist_data(data[0]["name"],data[0]["Origins"], "Liste des Airlines avec le nombre de aéroports d'origines d'ou elles opérent", details=3)
                    
                    airline_list = data[1]['name'].unique().tolist()
                    selected_airline = st.selectbox('Sélectionnez une Airline', airline_list)
                    filtered_data = data[1][data[1]['name'] == selected_airline]
                    st.text(f"Liste des origines de {selected_airline}")
                    st.write(filtered_data["Origins"])
                    
                    airline_list2 = data[2]['name'].unique().tolist()
                    selected_airline2 = st.selectbox('Sélectionnez une Airline x2', airline_list2)
                    filtered_data2 = data[2][data[2]['name'] == selected_airline2]
                    st.text(f"Liste des destinations de {selected_airline2}")
                    st.write(filtered_data2["dest"])
                case "q7":
                    st.write(data[0])
                case "q8":
                    st.write(data[0])
                    
        else:
            st.warning("Aucune donnée à afficher. Exécutez une requête pour récupérer les données.")
            

    def run(self):
        self.display_title()
        self.display_description()
        self.input_db_credentials()

        # Créer des onglets
        tab1, tab2 = st.tabs(["Requête & Visualisation", "Questions"])

        with tab1:
            self.execute_query()
            self.display_data()
            self.plot_data()

        with tab2:
            nb_questions = 8
            questions = [f"q{x}" for x in range(1,nb_questions+1)]
            for q in questions:
                self.questions(q)
                self.reponses(q)