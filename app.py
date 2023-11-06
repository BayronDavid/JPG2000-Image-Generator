import requests
from io import BytesIO
from math import sqrt
import streamlit as st
import requests
import base64
from PIL import Image, ImageFilter, ImageEnhance
from PIL.Image import Resampling
import numpy as np
import imageio


def obtener_imagen_cuadrante(api_key, latitud, longitud, lado_km, size, scale=4, maptype="satellite"):
    lado_km_ajustado = lado_km * 1.02
    km_en_grados = lado_km_ajustado / 111.32
    coords_earth_engine = [[longitud - km_en_grados/2, latitud - km_en_grados/2], [longitud + km_en_grados/2, latitud - km_en_grados/2], [longitud + km_en_grados/2, latitud + km_en_grados/2], [longitud - km_en_grados/2, latitud + km_en_grados/2], [longitud - km_en_grados/2, latitud - km_en_grados/2]]
    path = '|'.join([f"{lat},{lon}" for lon, lat in coords_earth_engine])
    params = {"size": size, "scale": scale, "maptype": maptype, "path": path, "key": api_key}
    response = requests.get("https://maps.googleapis.com/maps/api/staticmap?", params=params)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print(f"Error en la solicitud: {response.status_code} {response.text}")
        return None  

def obtener_imagenes_segmentadas(api_key, latitud_centro, longitud_centro, lado_total_km, segmentos, size, scale=4, maptype="satellite"):
    numero_cuadrantes = int(sqrt(segmentos))
    lado_cuadrante_km = lado_total_km / numero_cuadrantes
    km_en_grados = lado_cuadrante_km / 111.32
    centros_cuadrantes = []
    for i in range(numero_cuadrantes):
        for j in range(numero_cuadrantes - 1, -1, -1):
            centros_cuadrantes.append((latitud_centro - (km_en_grados / 2) * (numero_cuadrantes - 1) + i * km_en_grados,
                                      longitud_centro - (km_en_grados / 2) * (numero_cuadrantes - 1) + j * km_en_grados))
    return [obtener_imagen_cuadrante(api_key, lat, lon, lado_cuadrante_km, size, scale, maptype) for lat, lon in centros_cuadrantes][::-1]

def recortar_imagen(imagen, borde_x, borde_y):
    return imagen.crop((borde_x, borde_y, imagen.size[0] - borde_x, imagen.size[1] - borde_y))

def unir_imagenes_recortadas(imagenes, borde_recorte_x, borde_recorte_y, segmentos):
    if segmentos == 1:
        imagen_recortada = recortar_imagen(imagenes[0], borde_recorte_x, borde_recorte_y)
        return imagen_recortada.convert('RGBA')

    numero_cuadrantes = int(sqrt(segmentos))
    ancho_recorte, alto_recorte = imagenes[0].size[0] - 2 * borde_recorte_x, imagenes[0].size[1] - 2 * borde_recorte_y
    imagen_final =  Image.new('RGBA', (ancho_recorte * numero_cuadrantes, alto_recorte * numero_cuadrantes))

    for i in range(numero_cuadrantes):
        for j in range(numero_cuadrantes):
            idx = i * numero_cuadrantes + j
            imagen_recortada = recortar_imagen(imagenes[idx], borde_recorte_x, borde_recorte_y)
            imagen_final.paste(imagen_recortada, (j * ancho_recorte, i * alto_recorte))
            
    return aplicar_filtros(imagen_final)
    # return imagen_final

def ajustar_tamaño_maximo(escala):
    if escala == 1:
        return "640x640"
    elif escala == 2:
        return "1280x1280"
    
def generar_reporte(imagen_final, lado_total_km, size, borde_recorte_x, borde_recorte_y, segmentos, res_imagen):
    """
    Esta función muestra un reporte con datos relevantes.
    """
    
    imagen_mostrar = imagen_final.resize((500, 500))
    st.session_state.imagen_final = imagen_final  # Guarda la imagen en la variable de sesión
    st.image(imagen_mostrar, caption='Imagen generada', use_column_width=False)

    # Segmento 1: Parámetros de entrada
    parametros_entrada = """
    ### Parámetros de Entrada
    - **Lado total (km):** {}
    - **Tamaño de cada segmento:** {}
    - **Borde de recorte X:** {}
    - **Borde de recorte Y:** {}
    - **Segmentos:** {}
    """.format(lado_total_km, size, borde_recorte_x, borde_recorte_y, segmentos)

    # Segmento 2: Datos de obtención de imágenes y recorte
    tamaño_antes_recorte = res_imagen.size
    tamaño_despues_recorte = (tamaño_antes_recorte[0] - 2 * borde_recorte_x, tamaño_antes_recorte[1] - 2 * borde_recorte_y)
    datos_obtencion_recorte = """
    ### Datos de la Obtención de las Imágenes y Recorte
    - **Tamaño antes del recorte:** {} (ancho x alto)
    - **Tamaño después del recorte:** {} (ancho x alto)
    """.format(tamaño_antes_recorte, tamaño_despues_recorte)

    # Segmento 3: Datos de la imagen final
    tamaño_final = imagen_final.size
    buffered = BytesIO()
    imagen_final.save(buffered, format="PNG")
    peso_imagen_kilobytes = len(buffered.getvalue()) / 1024
    datos_imagen_final = """
    ### Datos de la Imagen Final
    - **Tamaño:** {} (ancho x alto)
    - **Peso:** {:.2f} KB
    - **Modo de color:** {}
    - **Formato:** PNG
    """.format(tamaño_final, peso_imagen_kilobytes, imagen_final.mode)

    # Combina los tres segmentos y muestra el reporte bajo la imagen
    # reporte = parametros_entrada + datos_obtencion_recorte + datos_imagen_final
    # st.subheader('Reporte')
    # st.markdown(reporte)
    st.subheader('Reporte')

    with st.expander('Parámetros de Entrada'):
        st.markdown(parametros_entrada)

    with st.expander('Datos de la Obtención de las Imágenes y Recorte'):
        st.markdown(datos_obtencion_recorte)

    with st.expander('Datos de la Imagen Final'):
        st.markdown(datos_imagen_final)

def aplicar_filtros(imagen, intensidad_suavizado=2):
    # nueva_dimension = (imagen.width * 2, imagen.height * 2)
    # imagen = imagen.resize(nueva_dimension, Image.LANCZOS)

    # Aplicar filtro de nitidez
    imagen = imagen.filter(ImageFilter.SHARPEN)

    # Aplicar filtro de resaltado de luz y sombra
    # imagen = ImageEnhance.Contrast(imagen).enhance(1.5) 

    # Aplicar filtro de mejora de detalles
    imagen = imagen.filter(ImageFilter.DETAIL)

    # Aplicar filtro de suavizado con la intensidad deseada
    for _ in range(intensidad_suavizado):
        imagen = imagen.filter(ImageFilter.SMOOTH_MORE)

    return imagen

def main():
    st.title('Generador de imagnes satelitales JP2000')
    
    st.sidebar.header('Info')
    st.sidebar.markdown('**Parametros** Descripcion.')
  
    # Entradas
    coordenadas = st.text_input('Coordenadas (latitud, longitud):', value='4.9422222, -74.0127778')
    latitud_centro, longitud_centro = [float(x) for x in coordenadas.split(',')]
    lado_total_km = st.number_input('Lado (km):', value=1)
    borde_recorte_x = st.number_input('Borde de recorte X:', value=218)
    borde_recorte_y = st.number_input('Borde de recorte Y:', value=218)
    api_key = st.text_input('API Key:', value='AIzaSyAqoHZdZiLpBu024UBXHas-F51UjnwuZvA') #Bayron
    scale = st.selectbox('Escala:', options=[1, 2], index=1)
    # Ajustar automáticamente el tamaño máximo en función de la escala
    size = ajustar_tamaño_maximo(scale)
    size = st.text_input('Tamaño de cada segmento:', value=size)
    st.text(f"Tamaño máximo permitido en la escala {scale}: {size}")
    maptype = st.selectbox('Tipo de mapa:', options=['satellite', 'roadmap', 'terrain'], index=0)
    segmentos = st.selectbox('Segmentos:', options=[1, 4, 16, 36, 64, 100, 104, 116, 136, 164, 200], index=1)

    if st.button('Previsualizar imagen'):
        try:
            if segmentos == 1:
                res_imagen = obtener_imagen_cuadrante(api_key, latitud_centro, longitud_centro, lado_total_km, size=size, scale=scale, maptype=maptype)
                if res_imagen:
                    imagen_final = imagen_final = recortar_imagen(res_imagen, borde_recorte_x, borde_recorte_y)
                    generar_reporte(imagen_final, lado_total_km, size, borde_recorte_x, borde_recorte_y, segmentos, res_imagen)
                else:
                    st.warning('Error al obtener la imagen. Verifica la clave de la API o los parámetros ingresados.')
                    return
            else:
                imagenes = obtener_imagenes_segmentadas(api_key, latitud_centro, longitud_centro, lado_total_km, segmentos, size=size, scale=scale, maptype=maptype)
                if all(imagen for imagen in imagenes):
                    res_imagen = imagenes[-1]
                    imagen_final = unir_imagenes_recortadas(imagenes, borde_recorte_x, borde_recorte_y, segmentos)
                    generar_reporte(imagen_final, lado_total_km, size, borde_recorte_x, borde_recorte_y, segmentos, res_imagen)
                else:
                    st.warning('Error al obtener las imágenes. Verifica la clave de la API o los parámetros ingresados.')
                    return

                        
        except Exception as e:
            # Manejar cualquier excepción inesperada
            print(f"Error inesperado: {str(e)}")
            st.warning('Ocurrió un error inesperado. Inténtalo de nuevo.')

        st.session_state.imagen_final = imagen_final

        if 'imagen_final' in st.session_state and st.session_state.imagen_final:
            final_width, final_height = st.session_state.imagen_final.size
            filename = f"{lado_total_km}KM x{lado_total_km}KM Scale_{scale} Seg_{segmentos} {final_width}x{final_height}.jp2"
            
            buffered = BytesIO()
            
            # Convertir la imagen PIL a un arreglo de numpy
            np_image = np.array(st.session_state.imagen_final)
            
            # Guardar en formato JP2 con múltiples resoluciones
            imageio.imwrite(buffered, np_image, format='JP2', numresolutions=5)
            
            st.download_button(label="Procesar y descargar imagen", data=buffered.getvalue(), file_name=filename, mime="image/jp2")
            st.warning('Esto puede tardar dependiendo la cantidad de segmentos y la capacidad de computo. Despues de descargar la pagina se recargara y perdera los datos')

if __name__ == "__main__":
    main()