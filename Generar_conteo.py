
def asignar_color(row):
    max_col = row.idxmax()
    
    if max_col == 'En Ejecución':
        return 'orange'
    elif max_col == 'Terminado':
        return 'green'
    elif max_col == 'Otros':
        return 'red'
    else:
        return 'black'



class Proyectos_conteo:

    def __init__(self,inversiones):

        self.inversiones = inversiones


    def generar_conteo(self):
        counts = self.inversiones.groupby(['DIVIPOLA', 'Estado']).size().unstack(fill_value=0)
        #counts['Otros'] = counts['Desaprobado'] + counts['Formulación'] + counts['No Aprobado'] + counts['Aprobado'] + counts['Viable'] + counts['No Viable']
        counts['Otros'] = counts['Desaprobado'] +  counts['No Aprobado'] + counts['Aprobado'] + counts['Viable'] 
        counts = counts.reset_index()
        counts = counts[['DIVIPOLA','En Ejecución','Terminado','Otros']]
        counts['color'] = counts.loc[:,['En Ejecución','Terminado','Otros']].apply(asignar_color, axis=1)
        counts['conteo_estados'] = counts.apply(lambda row: f"Terminado: {row.get('Terminado', 0)},Otros: {row.get('Otros', 0)}, En Ejecución: {row.get('En Ejecución', 0)}", axis=1)
        df_1 = self.inversiones.drop_duplicates(subset=['Municipio']).merge(counts, on='DIVIPOLA')
        df_1 = df_1[['Municipio','DIVIPOLA','Nombre Proyecto','Longitud','Latitud','color','conteo_estados','En Ejecución','Terminado',"Otros"]]
        return df_1