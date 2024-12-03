from django.http import JsonResponse
import pandas as pd
from sqlalchemy import create_engine, text
import yaml
from django.db import connection

ruta_archivo_config = 'etl_app/etl/configs/config.yaml'

def get_tipo_datos():
    try:
        with open(f'{ruta_archivo_config}', 'r') as archivo_config:
            config = yaml.safe_load(archivo_config)
        db = config['db']
        db_url = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'
        engine = create_engine(db_url)

        query = 'SELECT id, nombre FROM TipoDato ORDER BY nombre ASC'
        df_tipo_datos = pd.read_sql(query, engine)

        lista_tipo_datos = []
        for i, fila in df_tipo_datos.iterrows():
            lista_tipo_datos.append({'id': fila['id'], 'nombre': fila['nombre']})

        return lista_tipo_datos
    
    except FileNotFoundError:
        print("Archivo de configuración no encontrado")
    except yaml.YAMLError:
        print("Error al analizar el archivo de configuración")
    except KeyError:
        print("Faltan claves en la configuración de la base de datos")

def get_ficheros_pendientes(id_tipo_dato):
    try:
        with open(f'{ruta_archivo_config}', 'r') as archivo_config:
            config = yaml.safe_load(archivo_config)
        db = config['db']
        db_url = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'
        engine = create_engine(db_url)

        query = f'SELECT id, nombreFichero FROM Fichero WHERE estado = "pendiente"AND idTipoDato = {id_tipo_dato}'
        df_pendientes = pd.read_sql(query, engine)

        lista_pendientes = []
        for i, fila in df_pendientes.iterrows():
            lista_pendientes.append({'id': fila['id'], 'fichero': fila['nombreFichero']})

        return lista_pendientes
    
    except FileNotFoundError:
        print("Archivo de configuración no encontrado")
    except yaml.YAMLError:
        print("Error al analizar el archivo de configuración")
    except KeyError:
        print("Faltan claves en la configuración de la base de datos")
        

def cargar_fichero(fichero_path):
    try:
        with open(f'{ruta_archivo_config}', 'r') as archivo_config:
            config = yaml.safe_load(archivo_config)
        db = config['db']
        db_url = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'
        engine = create_engine(db_url)
        
        # Si es csv será del tipo inscripciones
        if fichero_path.endswith('.csv'):
            df_data = pd.read_csv(fichero_path)
        # Si es xlsx será del tipo accidentes
        elif fichero_path.endswith('.xlsx'):
            df_data = pd.read_excel(fichero_path)
            
            # Convertir NaN a None para que se inserte como NULL
            df_data = df_data.where(pd.notna(df_data), None)

            # Convertir todas las columnas a tipo string
            df_data = df_data.astype(str)
            
            df_data.rename(
                columns={
                    "num_expediente": "numExpediente",
                    "fecha": "fecha",
                    "hora": "hora",
                    "localizacion": "localizacion",
                    "numero": "numero",
                    "cod_distrito": "codigoDistrito",
                    "distrito": "distrito",
                    "tipo_accidente": "tipoAccidente",
                    "estado_meteorológico": "estadoMeteorologico",
                    "tipo_vehiculo": "tipoVehiculo",
                    "tipo_persona": "tipoPersona",
                    "rango_edad": "rangoEdad",
                    "sexo": "sexo",
                    "cod_lesividad": "codigoLesividad",
                    "lesividad": "lesividad",
                    "coordenada_x_utm": "coordenadaXUTM",
                    "coordenada_y_utm": "coordenadaYUTM",
                    "positiva_alcohol": "positivaAlcohol",
                    "positiva_droga": "positivaDroga",
                },
                inplace=True,
            )
            
            print(df_data.head())

            
            df_data.to_sql('Accidente', engine, if_exists='append', index=False)
            print("Datos insertados correctamente en la tabla Accidente")
            
            return {'status': 'success', 'message': 'Datos insertados correctamente en la tabla Accidente'}
            
        else:
            raise ValueError("Formato de archivo no soportado. Usa .csv o .xlsx")
        
    except FileNotFoundError:
        return {'status': 'error', 'message': 'Archivo de configuración no encontrado'}
    except yaml.YAMLError:
        return {'status': 'error', 'message': 'Error al analizar el archivo de configuración'}
    except KeyError:
        return {'status': 'error', 'message': 'Faltan claves en la configuración de la base de datos'}
    except Exception as e:
        return {'status': 'error', 'message': f"Error al procesar el archivo: {e}"}
 
def update_fichero(id_usuario, fichero_path, id_fichero):
    try:
        with open(f'{ruta_archivo_config}', 'r') as archivo_config:
            config = yaml.safe_load(archivo_config)
        db = config['db']
        db_url = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'
        engine = create_engine(db_url)
        
        sql = """
        UPDATE Fichero
        SET idUsuario = :id_usuario, fechaSubida = CURRENT_TIMESTAMP, ruta = :fichero_path, estado = 'procesado'
        WHERE id = :id_fichero
        """
        
        # Ejecutar la actualización
        with engine.connect() as connection:
            result = connection.execute(
                text(sql),
                {"id_usuario": id_usuario, "fichero_path": fichero_path, "id_fichero": id_fichero}
            )
            connection.commit()
            print(f"{result.rowcount} fila(s) actualizada(s).")
        
    except FileNotFoundError:
        print("Archivo de configuración no encontrado")
    except yaml.YAMLError:
        print("Error al analizar el archivo de configuración")
    except KeyError:
        print("Faltan claves en la configuración de la base de datos")    
    except Exception as e:
        print(f"Error al modificar los datos del fichero: {e}")
        
        
def insertar_tipo_dato(nombre, siglas):
    try:
        with open(f'{ruta_archivo_config}', 'r') as archivo_config:
            config = yaml.safe_load(archivo_config)
        db = config['db']
        db_url = f'mysql+pymysql://{db["user"]}:{db["password"]}@{db["host"]}/{db["database"]}'
        engine = create_engine(db_url)
        
        query = f'SELECT * FROM TipoDato WHERE nombre = "{nombre}"'
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            # Si no existe, insertar el nuevo registro
            insert_query = """
            INSERT INTO TipoDato (nombre, siglas)
            VALUES (:nombre, :siglas)
            """
            with engine.connect() as connection:
                connection.execute(
                    text(insert_query), 
                    {"nombre": nombre, "siglas": siglas}
                )
                connection.commit()
            return "Tipo de dato insertado correctamente."
        else:
            return f"El tipo de dato '{nombre}' ya existe en la base de datos."
        
    except FileNotFoundError:
        print("Archivo de configuración no encontrado")
    except yaml.YAMLError:
        print("Error al analizar el archivo de configuración")
    except KeyError:
        print("Faltan claves en la configuración de la base de datos")    
    except Exception as e:
        print(f"Error al insertar el tipo de dato: {e}")