import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dash_table.Format import Format, Scheme, Trim
from dash.dash_table import FormatTemplate
import numpy as np
import pypdf
import pandas as pd
import dash_auth
import ctypes
from urllib.request import urlretrieve
import camelot
from datetime import datetime, date
from urllib.error import HTTPError
#import pymsgbox
import os
import base64


USERNAME_PASSWORD_PAIRS = [ ['barrage', 'redouane1']]

def Taux(df, x1, y1):
    x=df[x1]
    y=df[y1]
    if  y.sum()==0:
        z=0
    else :
        z=x.sum() / y.sum()
    return z
df5=pd.read_excel("Barrages-Bassins.xlsx")

list_bassin=list(df5.Bassin.unique())   

with open('robot.jpg', "rb") as image_file2:
    img_data2 = base64.b64encode(image_file2.read())
    img_data2 = img_data2.decode()
    img_data2 = "{}{}".format("data:image/jpg;base64, ", img_data2)   

        
fichiers = os.listdir("Situation_Barrage")  
app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],prevent_initial_callbacks=True)
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

server = app.server
app.layout =dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('Situation des Barrages'),xs=9, sm=9, md=9, lg=9, xl=9,align='center'),
        
dbc.Col(html.Div([html.Div(html.Img(src= img_data2,width='auto',height=30),style={'display': 'inline-block'}),
               html.Div(html.P("By Redouane El Aoudi ",style={'font-size':'10px'},
               className="d-flex justify-content-end"),style={'display': 'inline-block'})]) ,xs=3, sm=3, md=3, lg=3, xl=3,align='end' )
    
    ],justify="center",style={'text-align': 'center','color':'black',
             'backgroundColor':'rgb(179,229,255)', 'box-shadow': '5px 10px #3B3C36',
    'border-radius': 4, 'border-color':'#0247FE','height':50,'font-weight': 'bold'}),
    
    html.Div(className="my-1"),
    
    dbc.Row([
   dbc.Col(
            html.Div([html.P("Téléchargement",className="my-1",style={'fon-Size':'16','color':'white','font-weight': 'bold'}),
                    dcc.Dropdown(
        id='dropdown-files',
        options=[{'label': f, 'value': f} for f in fichiers] ,
        placeholder="Télécharger la situation des barrages",
        value="",
        searchable=False,
        clearable=False,
        style={'fontSize':15,'color':'blue','font-weight': 'bold','width':'40vH'
               ,'height':'40px'}
    ),
    dcc.Download(id="download-docx")]),xs=4, sm=4, md=4, lg=6, xl=4, xxl=4,align='start'),
        
    dbc.Col(
            html.Div([html.P("Bassins Hydrologiques",className="my-1",style={'fon-Size':'16','color':'white',
                                                                             'font-weight': 'bold'}),
                   dcc.Dropdown(
        id='dropdown-files01',
        options=[{'label': f, 'value': f} for f in list_bassin] ,
        placeholder="Choisir un Bassin",
        value="",
        searchable=False,
        clearable=False,
        style={'fontSize':15,'color':'blue','font-weight': 'bold','width':'40vH'
               ,'height':'40px'})]), xs=4, sm=4, md=4, lg=4, xl=4, xxl=4,align='start'),  
        
      
    
    dbc.Col(html.Div([html.P("Choisir une date",className="my-1",style={'fontSize':16,'color':'white','font-weight': 'bold',
                                                                     'margin-bottom': '2px'  }),
    dcc.DatePickerSingle(
        id='picker',
        display_format='DD-MM-YYYY',
        date=date.today()) ,
        html.Div(id='error-message', style={'fontSize':16,'color':'white','font-weight': 'bold',
                                                                     'margin-bottom': '2px'  })
        
    #html.Div(id='date-output')
]),className="d-flex justify-content-end",xs=4, sm=4, md=4, lg=4, xl=4, xxl=4,align='start')],
  justify="center",style={'background-color': '#3B3C36', 'height':'200px'})  , 
    #  'height':40    
    
   html.Div(className="my-1"),  
   html.Hr(),
    
    
    dbc.Row([ 
         dbc.Col([
            html.Div(dcc.Loading(id="loading-1",
               type="default",
        children=[
            dash_table.DataTable(
        id='my-table',
        
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={ 'backgroundColor': 'rgb(204,230,255)', 'color': 'black' },                                                                                          
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="multi",
        row_selectable="multi",
        row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 12     
    )]))],
             xs=7, sm=7, md=7, lg=7, xl=7,align='start'),
        
        dbc.Col(dcc.Graph(id='bar-chart1' ),xs=5, sm=5, md=5, lg=5, xl=5,align="start")
        
        
    ],justify="center",className="mt-0")
       # "start", "center", "end", "between" and "around".
    
],fluid=True) 




@app.callback(
[ Output('my-table', 'columns'), Output('my-table', 'data'),
 Output('error-message', 'children')
   ],
    [Input('picker', 'date'),  Input('dropdown-files01', 'value')], 
    prevent_initial_call=True
)

def update_date_output(selected_date,selected_value):
    
    try:
        d1=selected_date[0:4]+"/"+selected_date[5:7]
        d2=selected_date[8:10]+"_"+selected_date[5:7]+"_"+selected_date[0:4]
        url = "http://81.192.10.228/wp-content/uploads/"+d1+"/"+d2+".pdf?"
        dossier = "Situation_Barrage"
        urlretrieve(url, f"{dossier}/situation_barrage.pdf")
        tableau = camelot.read_pdf("Situation_Barrage/situation_barrage.pdf", pages='1-end')
        df2= tableau[0].df
        df3= tableau[1].df
        df02=pd.concat([df2,df3],ignore_index=True)
        df02.columns = df02.iloc[0]
        df02=df02.drop(df02.index[[0]])
        df02 = df02.reset_index(drop=True)
        df02.columns.values[3]=df02.columns.values[2]+"-"
        df02.columns.values[5]=df02.columns.values[4]+"-"
        df02 =df02.rename(columns={'CAPACITE \nNORMALE \n(Mm3)': 'CAPACITE NORMALE (Mm3)',df02.columns.values[2]:df02.columns.values[2]
                                  +"-RESERVES (Mm3)-",df02.columns.values[3]:df02.columns.values[3]
                                  +"TAUX DE REMPLISSAGE (%)-",df02.columns.values[4]:df02.columns.values[4]
                                  +"-RESERVES (Mm3)-",df02.columns.values[5]:df02.columns.values[5]
                                  +"TAUX DE REMPLISSAGE (%)-"})
        df02= df02.drop(index=[0,len( df02)-1])
        df02.reset_index(inplace=True,drop = True)

        for i in  range(1,len(df02.columns)):
            df02.iloc[:,i]= df02.iloc[:,i].str.replace(',', '.')
            df02.iloc[:,i]=pd.to_numeric(df02.iloc[:,i], errors='coerce')
            
        df02.to_excel("Situation_Barrage/situation_barrage.xlsx",index=False)
        df6=pd.merge(df02,df5,on=["BARRAGES","CAPACITE NORMALE (Mm3)"],how='left')
        df6.to_excel("Situation_Barrage/Détail_barrage.xlsx",index=False)
        #pd.set_option('display.max_rows', None)
        df7=df6[df6.columns[[0,1,2,3,4,5,6]]]
        g=df7.groupby("Bassin")
        
        mt=g.get_group(selected_value)
        new_columns=[dict(name=i, id=i ,deletable=True,selectable= True,
        format=Format( precision=0,scheme=Scheme.fixed, trim=Trim.yes)  )  for i in mt.columns]

        new_data=mt.to_dict('records')
        
        
        return new_columns, new_data,""           
    except Exception as e:
        error_message = f"Les données ne sont pas disponibles pour cette date!: {str(e)}"
        return [], [], error_message



@app.callback(
    Output("download-docx", "data"),
    Input('dropdown-files', 'value'),
    prevent_initial_call=True
)
def generate_download(selected_file):
    try:
        if selected_file is not None:
            # Construct the full file path
            file_path = os.path.join("Situation_Barrage", selected_file)

            # Vérifiez si le fichier existe avant de le renvoyer
            if os.path.exists(file_path):
                return dcc.send_file(file_path)
            else:
                raise FileNotFoundError("Le fichier sélectionné n'existe pas.")
    except Exception as e:
        # Gérez d'autres exceptions ici, par exemple, affichez un message d'erreur générique
        return f"Erreur lors du téléchargement du fichier "

@callback(
    Output('bar-chart1', 'figure'),
    Input('my-table', 'derived_virtual_data'),
    Input('my-table', 'derived_virtual_selected_rows'),
    Input('my-table', 'selected_columns'))


def update_graphs(data_rows, derived_virtual_selected_rows,col):
  
    # Création du sous-tableau
    sub_df = pd.DataFrame(data_rows)
   # Création des données pour le graphique à barres
    fig=px.bar(sub_df, x='BARRAGES',y=col,barmode='group', color_discrete_sequence=px.colors.qualitative.Alphabet,
      ).update_layout(legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.2),xaxis={'categoryorder': 'total ascending'},
                    width=600, height=450)
                                                                 
    
    return fig


if __name__ == '__main__':
    app.run_server()