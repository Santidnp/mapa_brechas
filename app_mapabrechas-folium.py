#import geopandas
#import pandas as pd
import streamlit as st
#import matplotlib.pyplot as plt
import plotly.express as px
import folium
#from folium.plugins import MarkerCluster, HeatMap
#import json
import pickle
from streamlit_folium import st_folium,folium_static
from streamlit_dynamic_filters import DynamicFilters
from numpy import round
from streamlit_extras.metric_cards import style_metric_cards
from pandas import read_excel
from folium import IFrame
#def make_clickable(val):
    #return f'<a href="{val}" target="_blank">{val}</a>'
mapeo_colores = {
    'Formulación': 'blue',       # Azul 
    'Viable': 'orange',            # Naranja 
    'En Ejecución': 'green',      # Verde amarrillo
    'Aprobado': 'red',          # Rojo
    'Terminado': 'purple',         # Morado verde
    'Desaprobado': 'brown',       # Marrón
    'No Aprobado': 'pink',       # Rosa
    'No Viable': 'yellow'          # Lima
}
st.set_page_config(layout="wide",initial_sidebar_state="expanded",page_icon="https://www.dnp.gov.co/img/favicon/faviconNew.ico")
st.markdown("""
<nav style="background-color: #f8f9fa; padding: 50px;"display: flex; justify-content: center; align-items: center;">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQeQaLUYVjPPowO5IXM7mZh6LT5yitFBoyZRKaBkxQAQw&s" alt="Left Image" style="float: left; height: 50px;">
    <img src="https://www.dnp.gov.co/img/logoNuevo.jpg" alt="Right Image" style="float: right; height: 50px;">
</nav>
""", unsafe_allow_html=True)

st.markdown("<h1 style= 'text-align: center; red;'> Mapas de calor: Brechas Territoriales </h1>", unsafe_allow_html=True)

#mapa, barras = st.columns([0.6,0.4])

@st.cache_data
def generar_base():
    with open('geo_data_3.pickle', 'rb') as f:
        df = pickle.load(f)
    df.geometry =df.geometry.simplify(tolerance=0.03)
    #print(df.columns)
    #df = df.rename({'MPIO_CDPMP':'DIVIPOLA'})
    #df['DIVIPOLA'] = df['MPIO_CDPMP'].apply(int)
    df['MPIO_CNMBR'] = df['MPIO_CNMBR'].apply(lambda x : x.capitalize())

    df['DPTO_CNMBR'] = df['DPTO_CNMBR'].apply(lambda x : x.capitalize())
    df['Municipio'] = df['MPIO_CNMBR'] + '-' +df['DPTO_CNMBR']
    df.rename(columns = {'DPTO_CNMBR':'Departamento'},inplace = True)
    inversiones = read_excel('Inversiones.xlsx')
    inversiones = inversiones.dropna(subset=['Latitud', 'Longitud'])
    inversiones['Enlace'] =inversiones['Bpin'].apply(lambda x : 'https://mapainversiones.dnp.gov.co/Home/FichaProyectosMenuAllUsers?Bpin=' + x)
    #inversiones['Enlace'] = inversiones['Enlace'].apply(make_clickable)
    proyecto = read_excel('Proyectos_conteo_1.xlsx').dropna(subset=['Latitud', 'Longitud'])
    
    
    return df,inversiones,proyecto

df ,inversiones,proyecto = generar_base()
default_ix = list(df.iloc[:,14:-3].columns).index('IPM')
dynamic_filters = DynamicFilters(df, filters=['Departamento','Municipio','PDET','ZOMAC'])


with st.sidebar:
    st.image("dnp-logo.jpg", use_column_width=True)
    Indices = st.selectbox('Índices:', list(df.iloc[:,14:-3].columns),index=default_ix)
    #Municipio = st.selectbox('Municipio:',['Todos'] + list(df['Localidad'].unique()))
    #Departamento = st.selectbox('Departamento:', ['Todos'] + list(df['DPTO_CNMBR'].unique()))
    dynamic_filters.display_filters()
    boton = st.button('Ver información de proyectos')


#def filtro(base):
    
    #if Departamento == 'Todos' and Municipio == 'Todos':
        #return base 
    #elif Departamento != 'Todos':
        #base = df[df['DPTO_CNMBR']==Departamento]
        #return base
    #elif Municipio != 'Todos':
        #base = df[df['Localidad']==Municipio]
        #return base




#Añadir los polígonos de los municipios al mapa
#folium.GeoJson(geo_data).add_to(map_colombia)

    # Mostrar el mapa en Streamlit
#map_colombia

#@st.cache_data
#def cargar_mapa():
    #mapa_colombia = folium.Map(location=[4.5709, -74.2973], zoom_start=5.2)
    # Código para crear el mapa...
    #return mapa_colombia

df_1 = dynamic_filters.filter_df()
inversiones = inversiones[inversiones['DIVIPOLA'].isin(df_1['DIVIPOLA'])]
proyecto = proyecto[proyecto['DIVIPOLA'].isin(df_1['DIVIPOLA'])]
#mapa.metric("",'',df_1['Municipio'])
#st.write(df_1[['Departamento','MPIO_CNMBR','Analfabetismo_x','PDET','ZOMAC']])
#st.write(df_1[['Departamento','MPIO_CNMBR','Analfabetismo_x','PDET','ZOMAC']].loc[:,'Analfabetismo_x'])
#st.write(len(df_1[['Departamento','MPIO_CNMBR','Analfabetismo_x','PDET','ZOMAC']]))

Ipm_variables = ['Analfabetismo_x',	
'Bajo logro educativo',	
'Barreras a servicios para cuidado de la primera infancia',	
'Barreras de acceso a servicios de salud',
'Desempleo de larga duración',	
'Hacinamiento crítico',	
'Inadecuada eliminación de excretas',	
'Inasistencia escolar',	
'Material inadecuado de paredes exteriores',	
'Material inadecuado de pisos',	
'Rezago escolar',	
'Sin acceso a fuente de agua mejorada',	
'Sin aseguramiento en salud',	
'Trabajo infantil',	
'Trabajo informal']

mapa, barras = st.columns([0.6,0.4])




#st.divider()
#mapa.metric("Toneladas necesarias",'',2)
with mapa:
    #ipm_indice = st.selectbox('Componentes Ipm',Ipm_variables)
    #if len(df_1[['Departamento','MPIO_CNMBR','Analfabetismo_x','PDET','ZOMAC']]) !=1:
        #mapa.metric("Promedio Departamental",round(df_1[ipm_indice].mean(),2))
        #style_metric_cards()
    #else:
        #mapa.metric("Ínidice Municipal",round(df_1[ipm_indice].mean(),2))
        #style_metric_cards()
    
    
    #st.subheader(Indices)
    #st.markdown(f"<h3 style='color: black;'>{Indices}</h10>", unsafe_allow_html=True)
    #st.subheader('')
    #st.subheader('')
    mapa_colombia = folium.Map(location=[4.5709, -74.2973], zoom_start=5.2)
    mapa_calor = folium.Choropleth(
        geo_data= df_1, #gdp
        name='geometry',
        data= df_1, #
        columns=['DIVIPOLA',Indices],
        key_on= 'feature.properties.DIVIPOLA',
        fill_color= 'YlGn',
        fill_opacity= 0.75,
        line_opacity= 0.5,
        #line_color='black',
        legend_name= Indices,
        
        
    ).add_to(mapa_colombia)


    folium.GeoJson(
        df_1,  # GeoDataFrame
        name='geometry',
        style_function=lambda feature: {
            'color': 'black',  # Color de las líneas de separación
            'weight': 0.1,        # Grosor de las líneas de separación
        },
        tooltip=folium.GeoJsonTooltip(fields=['MPIO_CNMBR', Indices], aliases=['Municipio', 'Valor Índice: '])
    ).add_to(mapa_colombia)

    df_2 = df_1.sort_values(by=Indices, ascending=False)

    #st.markdown("<h3 style='color: black;'>MARI</h10>", unsafe_allow_html=True)


    
    #folium.GeoJsonTooltip(fields=['DIVIPOLA', 'Índice de Productividad, Competitividad y Complementariedad Económica'], aliases=['DIVIPOLA', 'Índice']).add_to(mapa_colombia)
    #st_folium(mapa_colombia, width=725)
    #mapa_colombia.add_child(folium.plugins.MiniMap(position='bottomleft'))
    #folium_static(mapa_colombia, width=600, height=400)
    if boton:
        #inversiones = inversiones[inversiones['DIVIPOLA'].isin(df_1['DIVIPOLA'])]
        for i in range(0,len(proyecto)):
            conteo_estados_html = proyecto.iloc[i]['conteo_estados'].replace(',', '<br>')
            html = f"""
                    <div style="font-size: 12px; width: 5px;">
                     {conteo_estados_html}
                    </div>
                    """
    # Crear un IFrame con el contenido HTML
            iframe = IFrame(html, width=200, height=100)
            popup = folium.Popup(iframe, max_width=200)
            folium.Marker(
                location=[proyecto.iloc[i]['Latitud'], proyecto.iloc[i]['Longitud']],
                popup= popup , #proyecto.iloc[i]['conteo_estados'],
                #icon=folium.Icon(color=mapeo_colores[inversiones.iloc[i]['Estado']])
                icon=folium.Icon(color=proyecto.iloc[i]['color'])
                ).add_to(mapa_colombia)

# Añadir la leyenda al mapa
        
        folium_static(mapa_colombia, width=600, height=400)
        #st.table(inversiones.sort_values(by='Valor Total', ascending=False)[['Sector','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']].head(10))

    else:
        folium_static(mapa_colombia, width=600, height=400)


    

            
        
    #folium_static(mapa_colombia, width=725, height=500)
#folium.LayerControl().add_to_map()
#map_colombia.save('mapa_folium.html')
with barras:
    #ipm_indice_2 = st.selectbox('Componentes Ipm',Ipm_variables,key="unique_key_here")
    #if len(df_1[['Departamento','MPIO_CNMBR','Analfabetismo_x','PDET','ZOMAC']]) !=1:
        #st.metric("Promedio Departamental",round(df_1[ipm_indice_2].mean(),2))
    #else:
        #st.metric("Ínidice Municipal",round(df_1[ipm_indice_2].mean(),2))

    fig = px.bar(df_2.head(10), y='MPIO_CNMBR', x=Indices)
    fig.update_yaxes(title_text="")
    fig.update_layout(width=600, height=400)
    st.plotly_chart(fig)

    
    

    #st.write(inversiones.sort_values(by='Valor Total', ascending=False)[['Sector','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']].head(10).to_html(escape=False), unsafe_allow_html=True)

st.data_editor(inversiones.sort_values(by='Valor Total', ascending=False)[['Sector','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']].head(10),
                   column_config={"Enlace":st.column_config.LinkColumn()})