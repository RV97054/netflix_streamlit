import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="netflix")

st.title("Netflix app")

#Crear una referencia hacia la colección movies de Firestore.
dbNames = db.collection("movies")

#Lectura de documento de firestone
#Crear una referencia hacia la colección movies de Firebase y convertirla en una lista
movies_ref = list(db.collection(u'movies').stream())

#Convertir la lista en un diccionario de Python.
movies_dict = list(map(lambda x: x.to_dict(), movies_ref))

#Crear un dataframe de pandas a partir del diccionario.
movies_dataframe = pd.DataFrame(movies_dict)

#Visualizar el dataframe con st.dataframe
#Display the content of the dataset if checkbox is true
agree = st.sidebar.checkbox("Mostrar todos los filmes")
if agree:
   st.header("Todos los filmes")
   st.dataframe(movies_dataframe)

#Crear una función que reciba como parámetro el nombre a buscar, filtre y
#regrese un único documento

def loadByName(name):
   #Convierte a minuscula el valor proporcionado
   name_lower = name.lower()

   # Inicializar una lista para almacenar los documentos que cumplen con el filtro
   matching_documents = []

   # Utilizar una expresión regular para buscar cualquier coincidencia de la cadena en el campo "name"
   regex = re.compile(f".*{re.escape(name_lower)}.*", re.IGNORECASE)

   movies_ref = dbNames.where(u'name', u'!=', name_lower).stream()

   # Iterar sobre los resultados de la consulta
   for doc in movies_ref:
       data = doc.to_dict()
       if regex.search(data.get('name', '').lower()):
            matching_documents.append(data)

   #return matching_documents
   df = pd.DataFrame(matching_documents)
   return df

#Crear una función para buscar por director
def loadByDirector(director):
   # Inicializar una lista para almacenar los documentos que cumplen con el filtro
   matching_documents = []
   movies_ref = dbNames.where(u'director',u'==', director).stream()

   # Iterar sobre los resultados de la consulta
   for doc in movies_ref:
      data = doc.to_dict()
      matching_documents.append(data)

   #convertir la lista de documentos a un dataFrame de pandas
   df = pd.DataFrame(matching_documents)
   return df

#Crear el control de texto para capturar el nombre a buscar
nameSearch = st.sidebar.text_input("Titulo del filme:")
nameSearch_lower = nameSearch.lower()

#Crear el control de botón para implementar la búsqueda
btnFiltrar = st.sidebar.button("Buscar filmes")

#Si el botón es presionado llamar a la función de búsqueda
if btnFiltrar:
   df = loadByName(nameSearch_lower)
   #Si el documento es encontrado visualizarlo
   if df.empty:
      st.write("Filme no existe")
   else:
      st.write("DataFrame resultante")
      st.write(df)

st.sidebar.header("Nuevo filme")

#Crear controles de entrada para cada uno de los campos.
company = st.sidebar.text_input("Company")
director = st.sidebar.text_input("Director")
genre = st.sidebar.text_input("Genre")
name = st.sidebar.text_input("Name")

#Crear un control de botón.
submit = st.sidebar.button("Crear nuevo filme")

#Once the name has submitted, upload it to the database
if company and director and genre and name and submit:
   doc_ref = db.collection("movies").document(name)

   #Si fue presionado y además se llenaron los campos de entrada, crear una
   #referencia al documento nuevo y usando el método set() insertar el
   #nuevo registro.
   doc_ref.set({
     "company": company,
     "director": director,
     "genre": genre,
     "name": name
   })
   st.sidebar.write("Registro insertado correctamente")

#Crear SELECTBOX
# Obtener valores únicos del campo 'director' de la base de datos
unique_director_values = set()

# Iterar sobre los documentos para obtener los valores únicos
for doc in dbNames.stream():
    unique_director_values.add(doc.get('director'))

# Convertir la lista de valores únicos a una lista para usar en el selectbox
director_options = list(unique_director_values)

# Seleccionar un valor por defecto
selected_director = st.sidebar.selectbox("Seleccionar Director", director_options, index=0)

#Se agrega el boton para realizar la busqueda
btnFilterbyDirector = st.sidebar.button('Filtrar director')

#Cuando el usuario hace clic en el botón "FiltrarDirector"
if btnFilterbyDirector:
   df = loadByDirector(selected_director)
   #Si el documento es encontrado visualizarlo
   if df.empty:
      st.write("Filme no existe")
   else:
      st.write("DataFrame resultante")
      st.write(df)
