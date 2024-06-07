import pandas as pd
import unidecode
import logging
from sodapy import Socrata

class DataProcessor:

    def __init__(self, df1_id, df2_id, excel_filename):
        #self.client = Socrata("www.datos.gov.co",None)
        self.client =  Socrata('www.datos.gov.co',None,username="sngh966.sg@gmail.com",password="@EY.H9pTbm$4jnJ")
        self.df1_id = df1_id
        self.df2_id = df2_id
        self.excel_filename = excel_filename

    def fetch_data(self, dataset_id):
        results = self.client.get(dataset_id,limit=2000)
        return pd.DataFrame.from_records(results)
    
    def load_excel_data(self, sheet):
        xls = pd.ExcelFile(self.excel_filename)
        return pd.read_excel(xls, sheet)
    
    def process_data(self):
        results_df = self.fetch_data(self.df1_id)
        results2_df = self.fetch_data(self.df2_id)
        self.client.close()

        df = pd.merge(results_df, results2_df[['bpin','municipio', 'departamento']], on='bpin', how='left')
        df = df.drop_duplicates()
        
        df['departamento'] = df['departamento'].str.lower()
        df['municipio'] = df['municipio'].str.lower()
        
        df['municipio'] = df['municipio'].apply(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)
        df['departamento'] = df['departamento'].apply(lambda x: unidecode.unidecode(x) if isinstance(x, str) else x)

        df1 = self.load_excel_data('coordenadas')
        df2 = self.load_excel_data('Coordenadas_departamento')

        df2['Departamento'] = df2['Departamento'].str.lower()
        df2['Departamento'] = df2['Departamento'].apply(lambda x: unidecode.unidecode(x))

        coordinates = {
            1101: ('yavarate', 'vaupes', 0.614879, -69.2081),
            1102: ('gramalote', 'norte de santander', 7.88804, -72.7975),
            1103: ('pacoa', 'vaupes', 0.05373, -71.2235),
            1104: ('barrancominas', 'guainia', 3.483, -69.8),
            1105: ('miriti - parana', 'amazonas', -0.883461, -70.9835),
            1106: ('la pedrera', 'amazonas', -1.25, -69.6),
            1107: ('la chorrera', 'amazonas', -1.45, -72.583),
            1108: ('tarapaca', 'amazonas', -2.867, -69.733),
            1109: ('puerto alegria', 'amazonas', -1.02622, -74.0486),
            1110: ('papunaua', 'vaupes', 1.91024, -70.685),
            1111: ('el encanto', 'amazonas', -1.67792, -73.2288),
            1112: ('san felipe', 'guainia', 1.91343, -67.0674),
            1113: ('mapiripana', 'guainia', 2.617, -70.533),
            1114: ('belen de bajira', 'choco', 7.3721598, -76.7145927),
            1115: ('cacahual', 'guainia', 3.51616, -67.4128),
            1116: ('puerto santander', 'amazonas', -0.625178, -72.3855),
            1117: ('puerto arica', 'amazonas', -2.133, -71.733),
            1118: ('la victoria', 'amazonas', 0.05, -71.217),
            1119: ('puerto colombia', 'guainia', 2.71947, -67.5684)
        }

        for index, (municipio, departamento, longitud, latitud) in coordinates.items():
            df1.at[index, 'Nombre Municipio'] = municipio
            df1.at[index, 'Nombre Departamento'] = departamento
            df1.at[index, 'Longitud'] = longitud
            df1.at[index, 'Latitud'] = latitud

        df1.at[1004, 'Nombre Municipio'] = 'santiago de cali'
        df1.at[779, 'Nombre Municipio'] = 'san jose de cucuta'
        df1.at[395, 'Nombre Municipio'] = 'sotara paispamba'
        df1.at[696, 'Nombre Municipio'] = 'fuente de oro'
        df1.at[170, 'Nombre Municipio'] = 'santa cruz de mompox'
        df1.at[956, 'Nombre Municipio'] = 'san jose de toluviejo'
        df1.at[727, 'Nombre Municipio'] = 'cuaspud carlosama'

        df1.at[1086, 'Nombre Departamento'] = 'archipielago de san andres'
        df1.loc[1085, 'Nombre Departamento'] = 'archipielago de san andres'

        df2.at[27, 'Departamento'] = 'archipielago de san andres'

        for index, municipio in df.municipio.items():
          try:
            if municipio == 'todo el depto':
              df.at[index, 'Longitud'] = df2[df2['Departamento'] == df.at[index, 'departamento']]['Longitud'].tolist()
              df.at[index, 'Latitud'] = df2[df2['Departamento'] == df.at[index, 'departamento']]['Latitud'].tolist()
            elif municipio == 'nacional':
                pass
            else:
              df.at[index, 'Longitud'] = df1[(df1['Nombre Municipio'] == df.at[index, 'municipio']) & (df1['Nombre Departamento'] == df.at[index, 'departamento'])]['Longitud'].tolist()
              df.at[index, 'Latitud'] = df1[(df1['Nombre Municipio'] == df.at[index, 'municipio']) & (df1['Nombre Departamento'] == df.at[index, 'departamento'])]['Latitud'].tolist()
          except ValueError as e:
            logging.info(e)
        
        df.to_csv('Clean_DNP-proyectos_datos_basicos.csv', index=False)

processor = DataProcessor("cf9k-55fw", "iuc2-3r6h", "Divipola.xlsx")
k = processor.process_data()



#'etft2hzpkc74osbghhyzs9ho5'  clave api
#'5ft4f1zx0pinax33epa6t01os819daubsvn11v5bbb4rbd6fsg' clave secreta api


client = Socrata('www.datos.gov.co',app_token='P3nSNFpLnbXCqdRTYMC9jmv8h',username="sngh966.sg@gmail.com",password="@EY.H9pTbm$4jnJ")

client = Socrata('www.datos.gov.co',app_token='P3nSNFpLnbXCqdRTYMC9jmv8h',access_token='0nBmO_Zm_BiG-olbn9LpdrAJZbdD6VodFQa7')


results = client.get("v8aw-jabd", limit=2000)
results = client.get("cf9k-55fw", limit=2000)

results = client.get_all("cf9k-55fw")

a = pd.DataFrame.from_records(results)

b = pd.read_csv('Clean_DNP-proyectos_datos_basicos.csv')