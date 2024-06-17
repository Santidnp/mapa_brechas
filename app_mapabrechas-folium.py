#import geopandas
#import pandas as pd
import streamlit as st
import matplotlib
#import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import folium
from plotly.subplots import make_subplots
#from folium.plugins import MarkerCluster, HeatMap
#import json
import pickle
from streamlit_folium import st_folium,folium_static
from streamlit_dynamic_filters import DynamicFilters
from numpy import round
from streamlit_extras.metric_cards import style_metric_cards
from pandas import read_excel,DataFrame,Series
from folium import IFrame
from Generar_conteo import *
from Inversiones_clase import *
#import webbrowser
#def make_clickable(val):
    #return f'<a href="{val}" target="_blank">{val}</a>'



def arreglar_divipola(x):
    if len(str(int(x))) == 4:
        return '0'+ str(int(x))
    
    else:
        return str(int(x))
    

def divipola_dep(x):
    if x == '11001':
        return x 
    
    else:
        return x[:-3] + "000"
    
def eliminar_espacios_extra(cadena):
    return ' '.join(cadena.split())


def convertir_a_numero(valor):
    if isinstance(valor, str):
        if '%' in valor:
           
            valor_sin_simbolo = valor.strip('%')
            valor_sin_coma = valor_sin_simbolo.replace(',', '.')
            return float(valor_sin_coma) / 100
        elif ',' in valor:
            
            valor_sin_coma = valor.replace(',', '.')
            return float(valor_sin_coma)
    elif isinstance(valor, (int, float)):
        return valor  
    else:
        return valor  


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
st.set_page_config(layout="wide",initial_sidebar_state="expanded",
                   page_icon="https://www.dnp.gov.co/img/favicon/faviconNew.ico",
                   page_title="Mapa de Brechas Territoriales")
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
    with open('geo_data_4.pickle', 'rb') as f:
        df = pickle.load(f)
    inversiones = Inversion().process_data()
    inversiones = inversiones.dropna(subset=['Latitud', 'Longitud'])
    inversiones['Valor_Billon'] = inversiones['Valor Total']/1000
    inversiones['Enlace'] =inversiones['Bpin'].apply(lambda x : 'https://mapainversiones.dnp.gov.co/Home/FichaProyectosMenuAllUsers?Bpin=' + str(x))
    serie = read_excel('Serie_tiempo.xlsx')
    i_s = read_excel('Indices_Sectores.xlsx')
    i_s['Indices'] = i_s['Indices'].apply(lambda x : eliminar_espacios_extra(x))
    i_s['Sectores'] = i_s['Sectores'].apply(lambda x : eliminar_espacios_extra(x))
    proyecto = Proyectos_conteo(inversiones).generar_conteo()
    return df,inversiones,serie,i_s,proyecto





################################################################Procesamiento###########################################################

df ,inversiones,serie,i_s,proyecto = generar_base()





default_ix = list(df.iloc[:,14:-3].columns).index('IPM')
#dynamic_filters = DynamicFilters(df, filters=['Departamento','Municipio','PDET','ZOMAC'])
dynamic_filters = DynamicFilters(df, filters=['Departamento','Municipio'])
df_1 = dynamic_filters.filter_df()
departamento_df = inversiones[inversiones['Departamento'].isin(df_1['Departamento'])]
is_filter_by_municipio = bool(len(df_1['DIVIPOLA'].unique()) == 1)
inversiones = inversiones[inversiones['DIVIPOLA'].isin(df_1['DIVIPOLA'])]
proyecto = proyecto[proyecto['DIVIPOLA'].isin(df_1['DIVIPOLA'])]
columnas_serie = ['Año'] + list(df_1['Departamento'].unique())
serie = serie[columnas_serie]
link = list(df_1['DIVIPOLA_2'])[0]
link_1 = list(df_1['DIVIPOLA_3'])[0]

missing = DataFrame(df_1.iloc[:, 14:-3].isnull().sum()).sort_values(by=[0], ascending=False)
#st.write(link_1)
#st.write(link)
#link = f'[{link}]'



########################################################################################################################################
with st.sidebar:
    st.image("dnp-logo.jpg", use_column_width=True)
    Sector = st.selectbox('Selecione sector',['Todos'] + list(i_s['Sectores'].unique()))
    #Indices = st.selectbox('Índices:', list(df.iloc[:,14:-3].columns),index=default_ix)
    if Sector == 'Todos':
        Indices = st.selectbox('Índices:', list(df.iloc[:,14:-3].columns),index=default_ix)
    else:
        Indices = st.selectbox('Índices:', i_s[i_s['Sectores']==Sector]['Indices'])

    #Municipio = st.selectbox('Municipio:',['Todos'] + list(df['Localidad'].unique()))
    #Departamento = st.selectbox('Departamento:', ['Todos'] + list(df['DPTO_CNMBR'].unique()))
    dynamic_filters.display_filters()
    boton = st.button('Ver información de proyectos')
    st.link_button("Ver información del Departamento seleccionado en Terridata", link_1)
    st.link_button("Ver información del municipo seleccionado en Terridata", link)
    

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
    
            iframe = IFrame(html, width=200, height=100)
            popup = folium.Popup(iframe, max_width=200)
            folium.Marker(
                location=[proyecto.iloc[i]['Latitud'], proyecto.iloc[i]['Longitud']],
                popup= popup,#proyecto.iloc[i]['Nombre Proyecto']
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
   

    
    

    #st.write(inversiones.sort_values(by='Valor Total', ascending=False)[['Sector','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']].head(10).to_html(escape=False), unsafe_allow_html=True)

st.plotly_chart(fig)
serie_grafica = px.line(serie, x='Año', y=serie.columns[1:], markers=True, title='Ipm Departamental')
serie_grafica.update_layout(xaxis_title='Año', yaxis_title='IPM',width=1000)
st.plotly_chart(serie_grafica)
st.markdown('## Proyectos ')

if Sector == 'Todos':
    st.data_editor(inversiones.sort_values(by='Valor Total', ascending=False)[['Sectores','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']],
                    column_config={"Enlace":st.column_config.LinkColumn()})
else:

    inversiones = inversiones[inversiones['Sectores'] == Sector]

    st.data_editor(inversiones.sort_values(by='Valor Total', ascending=False)[['Sectores','Entidad Responsable','Nombre Proyecto','Estado','Valor Total','Enlace']],
                    column_config={"Enlace":st.column_config.LinkColumn()})


#st.components.v1.iframe("https://terridata.blob.core.windows.net/fichas/Ficha_19824.pdf", height=400, scrolling=True)

########################################################GRAFICOS-DESCRIPTIVOS####################################################

grouped_data = inversiones.loc[inversiones.groupby('Bpin')['Finalización'].idxmax()]
estado_count = grouped_data['Estado'].value_counts().reset_index()
estado_count.columns = ['Estado', 'Total']

mask = ~(grouped_data.Municipio.isna())
grouped_data2 = grouped_data[mask].groupby(['Municipio', 'Departamento'])[['IPM', 'Valor Total']].agg({'Valor Total':'sum', 'IPM':'mean'})
grouped_data2 = grouped_data2.reset_index()
grouped_data2['($) Valor Total'] = '$' + (round(grouped_data2['Valor Total'].astype(float)/1000000,2)).astype(str) + 'M.'
grouped_data2['Municipio_Departamento'] = grouped_data2['Municipio'] + ', ' + grouped_data2['Departamento']
grouped_data2 = grouped_data2[grouped_data2['Valor Total'] > 0]

note = 'El gráfico presenta el valor total invertido en proyectos de carácter municipal, clasificados por departamento <br>Los cálculos no suman los proyectos de caracter Departamental, por lo que el precio total de Colombia no es el total.'
fig_heatmap = px.treemap(grouped_data2,
                 path=[px.Constant("Colombia"), 'Departamento', 'Municipio'],
                 values= 'Valor Total',
                 color = 'IPM',
                 color_continuous_scale= 'YlGn',
                 title= f'Distribución de la inversión total de proyectos por municipalidad del sector {Sector}'
                 )
fig_heatmap.update_layout(
    title = dict(
        text= 'Distribución de la inversión total de proyectos por municipalidad',
        x=0.5,
        xanchor='center'
    ),
    margin = dict(t=50, l=25, r=25, b=25))

fig_heatmap.update_traces(
    hovertemplate = '<b>%{label}</b><br><br>' +
                    'Valor Total: %{value:$,.0f}' +'<br>' +
                    'IPM: %{color:,.2f}<extra></extra>',
    textinfo ='label+text+value'
)
fig_heatmap.data[0].textinfo = 'label'

fig_heatmap.add_annotation(
    showarrow=False,
    text=note,
    font=dict(size=10), 
    xref='paper',
    x=0.5,
    yref='paper',
    y=-0.1,
    xanchor='center',
    yanchor='top'
    )
fig_container_id = 'centered-treeemap'
st.markdown(f'<div id= "(fig_container_id)">', unsafe_allow_html=True)
st.plotly_chart(fig_heatmap)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <style>
    #{fig_container_id} {{
        display: flex;
        justify-content: center;
    }}
    #{fig_container_id} .element-container {{
        display: flex;
        justify-content: center;
    }}
    #{fig_container_id} div.stPlotlyChart {{
        margin: auto;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

def bar_graph():
    if is_filter_by_municipio:

        departamento = departamento_df.groupby(['Proyecto'])[['Count', 'IPM', 'Valor Total', 'Valor_Billon']].agg({'Count':'sum', 'IPM':'mean','Valor Total':'mean', 'Valor_Billon': 'mean'}).reset_index()
        municipio = inversiones.groupby(['Proyecto'])[['Count', 'IPM', 'Valor Total', 'Valor_Billon']].agg({'Count':'sum', 'IPM':'mean','Valor Total':'sum', 'Valor_Billon': 'sum'}).reset_index()


        norm = matplotlib.colors.Normalize(municipio['Count'].min(), departamento['Count'].max())
        colors = px.colors.sequential.YlGn

        def get_color(val):
            return colors[int(norm(val) * (len(colors) -1))]

        fig_bar2 = go.Figure()

        # Barra - Municipio
        fig_bar2.add_trace(go.Bar(
            x=municipio['Proyecto'],
            y=municipio['Valor_Billon'],
            customdata = municipio[['Valor Total', 'Count']],
            marker_color = [get_color(val) for val in municipio['Count']],
            name='Municipio',
            hovertemplate='<b>%{x}</b><br>' +
                            'Total: %{customdata[1]:,.0f}<br>' +
                            'Valor Total: %{customdata[0]:,.0f}<br>'
            
        ))

        # Barra - Departamento
        fig_bar2.add_trace(go.Bar(
            x=departamento['Proyecto'],
            y=departamento['Valor_Billon'],
            marker_line=dict(width=2, color='white'),
            customdata = departamento[['Valor Total', 'Count']],
            marker_color = [get_color(val) for val in departamento['Count']],
            marker_pattern_shape=["/" for item in departamento['Proyecto']],
            name='Departamento',
            hovertemplate='<b>%{x}</b><br>' +
                            'Total: %{customdata[1]:,.0f}<br>' +
                            'Valor Promedio: %{customdata[0]:,.0f}<br>'
            
        ))

        #Barra de color
        fig_bar2.add_trace(go.Scatter(
        x=[None], y=[None],
            mode='markers',
            showlegend= False,
            marker=dict(
                colorscale='YlGn',
                cmin=min(departamento['Count'].min(), municipio['Count'].min()),
                cmax=max(departamento['Count'].max(), municipio['Count'].max()),
                colorbar=dict(
                    title = 'Total de Proyectos',
                    lenmode='fraction',
                    len=0.75,
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=0.45
                )
            ),
            hoverinfo='none'
        ))

        fig_bar2.update_layout(
            barmode='group',
            title='Distribución de cantidad proyectos por categoría',
            xaxis_tickangle=-45,
            xaxis_title= 'Proyectos',
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.45
            ),
            coloraxis1=dict(
                colorscale='YlGn',
                cmin=min(departamento['Count'].min(), municipio['Count'].min()),
                cmax=max(departamento['Count'].max(), municipio['Count'].max()),
                colorbar=dict(
                    title = 'Total de Proyectos',
                    lenmode='fraction',
                    len=0.75,
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                )
            )
        )
        return fig_bar2

    else:
        grouped_data3 = grouped_data[mask].groupby('Proyecto')[['IPM', 'Valor Total', 'Count']].agg({'Count':'sum', 'IPM':'mean','Valor Total':'sum'}).reset_index()
        grouped_data3['Valor_Billon'] = grouped_data3['Valor Total']/1000
        fig_bar = px.bar(grouped_data3, x='Proyecto', y='Count', color='Valor_Billon', custom_data= ['Valor Total'],title= 'Distribución de cantidad proyectos por categoría')

        fig_bar.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                        'Total: %{y}<br>' +
                        'Valor Total: %{customdata[0]:,.0f}<br>'
        )
        return fig_bar



fig_pie = px.pie(estado_count, values='Total', names='Estado', title ='Distribución del estado de los proyectos', color_discrete_map=  mapeo_colores)

grouped_data3 = grouped_data[mask].groupby('Proyecto')[['IPM', 'Valor Total', 'Count']].agg({'Count':'sum', 'IPM':'mean','Valor Total':'sum'}).reset_index()
grouped_data3['Valor_Billon'] = grouped_data3['Valor Total']/1000
fig_bar = bar_graph()

fig = make_subplots(rows=1, cols=2, subplot_titles=('Distribución de cantidad proyectos por categoría', 'Distribución del estado de los proyectos'), specs=[[{"type": "xy"}, {"type": "domain"}]])
for trace in fig_bar.data:
    fig.add_trace(trace, row=1,col=1)

for trace in fig_pie.data:
    fig.add_trace(trace, row=1,col=2)

fig.update_layout(height=600, 
                  width=1200, 
                  showlegend=True,
                  legend=dict(
                     x=1.1,
                     y=0.5,
                     traceorder='normal',
                     font=dict(
                         size=12
                     ),
                 ),
                 coloraxis_colorbar=dict(
                     x=0.45,
                     len=0.75,
                     title='Valor Total<br>(en millón de millones)',
                 ),
                 margin=dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig)


