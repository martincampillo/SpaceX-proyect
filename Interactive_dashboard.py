# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique()

site_options = [{'label': site, 'value': site} for site in launch_sites]

site_options.insert(0, {'label': 'All Sites', 'value': 'ALL'})

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=site_options,  # Usamos la variable que acabamos de crear
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                    ),
                                # LA LÍNEA ERRÓNEA HA SIDO ELIMINADA DE AQUÍ
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,  # Usar la variable
                                    max=max_payload,  # Usar la variable
                                    step=1000,
                                    # Crear marcas (marks) automáticas para los rangos clave
                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)},
                                    value=[min_payload, max_payload] # El valor inicial es el rango completo
                                    ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(entered_site):
    if entered_site == 'ALL':
        # 1. Agrupar por sitio y sumar los éxitos (columna 'class')
        all_sites_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            data_frame=all_sites_data,
            names='Launch Site',   # Las porciones son los sitios
            values='class',        # El tamaño es el total de éxitos
            title='Total de Lanzamientos Exitosos por Sitio'
        )
        return fig
    else:
        # 1. Filtrar el DataFrame para ese sitio
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # 2. Contar los 1s (Éxito) y 0s (Fracaso)
        outcome_counts = site_data['class'].value_counts()
        
        # 3. Crear un DataFrame para Plotly
        outcome_df = outcome_counts.reset_index()
        outcome_df.columns = ['Outcome', 'Count']
        # Mapeamos 1 y 0 a etiquetas legibles
        outcome_df['Outcome'] = outcome_df['Outcome'].map({1: 'Éxito (1)', 0: 'Fracaso (0)'})

        fig = px.pie(
            data_frame=outcome_df,
            names='Outcome',   # Las porciones son 'Éxito' y 'Fracaso'
            values='Count',    # El tamaño es el conteo
            title=f'Tasa de Éxito vs. Fracaso para {entered_site}'
        )
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]  # ¡Inputs en una lista!
)
def update_scatter_chart(entered_site, payload_range): # ¡Dos argumentos!
    
    # 1. Filtrar por rango de Payload
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # 2. Filtrar por sitio (si no es 'ALL')
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Correlación Payload vs. Éxito para {entered_site}'
    else:
        title = 'Correlación Payload vs. Éxito para Todos los Sitios'

    # 3. Crear el gráfico de dispersión
    fig = px.scatter(
        data_frame=filtered_df,
        x='Payload Mass (kg)',
        y='class',  # 'class' (0 o 1) mostrará el resultado
        # 'color' es opcional, pero muy recomendado. 
        # 'Booster Version Category' está en el CSV de este curso de Coursera.
        color='Booster Version Category', 
        title=title
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True) # Añadido debug=True para facilitar la depuración
