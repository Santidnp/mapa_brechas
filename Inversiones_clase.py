import pandas as pd
from leila.datos_gov import DatosGov
from concurrent.futures import ThreadPoolExecutor
import unidecode
from pandas import read_excel,Series
import pickle
with open('geo_data_3.pickle', 'rb') as f:
        df1 = pickle.load(f)



# Función para cargar la base de datos desde la API
def cargar_base(api_id, nombre_base_script):
    data = DatosGov().cargar_base(api_id=api_id)
    datos = data.to_dataframe()
    return nombre_base_script, datos

diccionario_sectores = {
    'Ambiente Y Desarrollo Sostenible': 'Ambiente y Desarrollo Sostenible',
    'Comercio, Industria Y Turismo': 'Comercio, Industria y Turismo',
    'Cultura': 'Otro',  
    'Gobierno Territorial': 'Otro',  
    'Inclusión Social Y Reconciliación': 'Inclusión Social y Reconciliación (Prosperidad Social)',
    'Hacienda': 'Hacienda y Crédito Público',
    'Justicia Y Del Derecho': 'Justicia',
    'Interior': 'Interior',
    'Relaciones Exteriores': 'Otro',  
    'Presidencia De La República': 'Otro',  
    'Trabajo': 'Trabajo',
    'Transporte': 'Transporte',
    'Vivienda, Ciudad Y Territorio': 'Vivienda',
    'Minas Y Energía': 'Minas y Energía',
    'Organismos De Control': 'Otro',  
    'Registraduría': 'Otro', 
    'Planeación': 'Planeación Nacional',
    'Salud Y Protección Social': 'Salud',
    'Rama Judicial': 'Justicia',  
    'Información Estadística': 'Otro',  # No tiene correspondencia exacta
    'Tecnologías De La Información Y Las Comunicaciones': 'TIC',
    'Ciencia, Tecnología E Innovación': 'TIC',  # No tiene correspondencia exacta
    'Deporte Y Recreación': 'Otro',  # No tiene correspondencia exacta
    'Educación': 'Educación Nacional',
    'Empleo Público': 'Igualdad',  # No tiene correspondencia exacta
    'Fiscalía': 'Otro',  # No tiene correspondencia exacta
    'Sistema Integral De Verdad, Justicia, Reparación Y No Repetición': 'Otro',  # No tiene correspondencia exacta
    'Agricultura Y Desarrollo Rural': 'Agricultura y Desarrollo Rural',
    'Congreso De La República': 'Otro',  # No tiene correspondencia exacta
    'Igualdad Y Equidad': 'Igualdad'
}



class Inversion:

    def __init__(self):
        inventario_proyectos = pd.read_excel("Tablas_Proyec.xlsx")
        inventario_proyectos=inventario_proyectos.loc[inventario_proyectos['seleccion'] == 'x']


        with ThreadPoolExecutor() as executor:
            futures = []
        
        # Iterar sobre las filas del DataFrame inventario_proyectos
            for index, row in inventario_proyectos.iterrows():
                numero_api = row['numero_api']
                nombre_base_script = row['nombre_base_script']
                futures.append(executor.submit(cargar_base, numero_api, nombre_base_script))
        
        # Iterar sobre los objetos futuros para obtener los resultados
            for future in futures:
                nombre_base_script, datos = future.result()
                # Crear un nuevo DataFrame con el nombre especificado en la columna 'nombre_base_script'
                globals()[nombre_base_script] = datos.copy() 
                


            self.results_df = globals()['PROY_proyectos_datos_basicos']
            
            self.results2_df = globals()['PROY_EjecucionProyectoDivipola']

            self.divipola = read_excel('Divipola 1.xlsx')
            


    

    def process_data(self):

        df = pd.merge(self.results_df, self.results2_df[['bpin','codigomunicipio','municipio']], on='bpin', how='left')
        df = df.drop_duplicates()
        dictionary_longi = Series(self.divipola.Longitud.values, index=self.divipola.Divipola_mun).to_dict()
        dictionary_lati = Series(self.divipola.Latitud.values, index=self.divipola.Divipola_mun).to_dict()

        df['Longitud'] = df['codigomunicipio'].map(dictionary_longi)
        df['Latitud'] = df['codigomunicipio'].map(dictionary_lati)
        df.dropna(inplace=True)
        df = df.rename(columns={'nombreproyecto':'Nombre Proyecto','codigomunicipio':'DIVIPOLA','estadoproyecto':'Estado','municipio':'Municipio','valortotalproyecto': 'Valor Total','bpin':'Bpin'})

        for index in df.index:
             df.at[index, 'Proyecto'] = df['Nombre Proyecto'].loc[index].split()[0]
 
        mapping = {'Contribucin': 'Contribución', 'Estudio': 'Estudios', 'Implementacion': 'Implementación', 
                'Identificacin': 'Identificación', 'Construccin': 'Construcción', 'Formulacin': 'Formulación',
                'Elaboracin': 'Elaboración', 'Ampliacin': 'Ampliación', 'Diseo':'Diseño', 'Reposicin': 'Reposición'}
        df['Proyecto'] = df.replace({'Proyecto': mapping})['Proyecto']
 
        mapping = {'Construcción': ['Construcción', 'Mantenimiento', 'Reparación', 'Reposición', 'Remodelación', 'Rehabilitación',
                                    'Renovación', 'Restauración', 'Reconstrucción', 'Habilitación', 'Sistematización', 'Erradicación',
                                    'Mejoramiento', 'Conservación', 'Recuperación', 'Adecuación'],
                'Suministro': ['Suministro', 'Adquisición', 'Distribución', 'Dotación'],
                'Desarrollo': ['Desarrollo', 'Implementación', 'Generación', 'Aportes', 'Ampliación', 'Extensión', 'Modernización', 'Forestación', 'Aplicación'],
                'Estudios': ['Estudios', 'Caracterización', 'Asesoria', 'Diagnostico', 'Elaboración', 'Formulación', 'Análisis',
                            'Revisión', 'Levantamiento', 'Exploración', 'Normalización', 'Identificación', 'Aprovechamiento',
                            'Diseño'],
                'Apoyo': ['Apoyo', 'Fortalecimiento', 'Asistencia', 'Contribución', 'Capacitación', 'Control', 'Prevención',
                            'Inversión', 'Inversiones'],
                'Administración': ['Administración', 'Programación', 'Control', 'Titulación', 'Saneamiento', 'Incorporación',
                                    'Descontaminación', 'Integración', 'Consolidación'],
                'Otros': ['Optimización', 'Servicio', 'Prestación', 'Instalación', 'Compromiso', 'Subsidio', 'Protección',
                            'Traslado', 'Restitución', 'Conformación', 'Implantación', 'Prevención', 'Sustitución', 'Actualización',
                            'Incremento']}
 
        def category_assignment(string):
            for category, key_word in mapping.items():
                if string in key_word:
                    return category
 
        df['Proyecto'] = df['Proyecto'].apply(category_assignment)
        df = df.merge(df1[['DIVIPOLA','IPM','DPTO_CNMBR']],on='DIVIPOLA',how = 'left')


        df = df.rename(columns={'DPTO_CNMBR':'Departamento','sector':'Sector','entidadresponsable':'Entidad Responsable'})
        df['Finalización'] = df['horizonte'].str.extract(r'-(\d{4})')
        df['Count'] = 1
        df['Sectores'] = df['Sector'].map(diccionario_sectores)
        df['Sectores'] = df['Sectores'].str.strip()


        
       

        return df
