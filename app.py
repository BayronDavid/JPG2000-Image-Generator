import requests
from PIL import Image
from io import BytesIO
from math import sqrt
import base64
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64

def obtener_imagen_cuadrante(api_key, latitud, longitud, lado_km, size="2048x2048", scale=4, maptype="satellite"):
    # Aumenta el lado en kilómetros para hacer el cuadrado un poco más grande.
    lado_km_ajustado = lado_km * 1.02
    km_en_grados = lado_km_ajustado / 111.32
    coords_earth_engine = [[longitud - km_en_grados/2, latitud - km_en_grados/2], [longitud + km_en_grados/2, latitud - km_en_grados/2], [longitud + km_en_grados/2, latitud + km_en_grados/2], [longitud - km_en_grados/2, latitud + km_en_grados/2], [longitud - km_en_grados/2, latitud - km_en_grados/2]]
    path = '|'.join([f"{lat},{lon}" for lon, lat in coords_earth_engine])
    params = {"size": size, "scale": scale, "maptype": maptype, "path": path, "key": api_key}
    response = requests.get("https://maps.googleapis.com/maps/api/staticmap?", params=params)
     # Verificando si la respuesta es exitosa
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        print(f"Error en la solicitud: {response.status_code} {response.text}")
        return None  

def obtener_imagenes_segmentadas(api_key, latitud_centro, longitud_centro, lado_total_km, segmentos, size="2048x2048", scale=4, maptype="satellite"):
    numero_cuadrantes = int(sqrt(segmentos))
    lado_cuadrante_km = lado_total_km / numero_cuadrantes
    km_en_grados = lado_cuadrante_km / 111.32
    centros_cuadrantes = []
    for i in range(numero_cuadrantes):
        for j in range(numero_cuadrantes - 1, -1, -1):
            centros_cuadrantes.append((latitud_centro - (km_en_grados / 2) * (numero_cuadrantes - 1) + i * km_en_grados,
                                      longitud_centro - (km_en_grados / 2) * (numero_cuadrantes - 1) + j * km_en_grados))
    return [obtener_imagen_cuadrante(api_key, lat, lon, lado_cuadrante_km, size, scale, maptype) for lat, lon in centros_cuadrantes][::-1]

def recortar_imagen(imagen, borde):
    return imagen.crop(borde)

def unir_imagenes_recortadas(imagenes, borde_recorte, segmentos):
    if segmentos == 1:
        imagen_recortada = recortar_imagen(imagenes[0], (borde_recorte, borde_recorte, imagenes[0].size[0] - borde_recorte, imagenes[0].size[1] - borde_recorte))
        return imagen_recortada.convert('RGB')


    numero_cuadrantes = int(sqrt(segmentos))
    ancho_recorte, alto_recorte = imagenes[0].size[0] - 2 * borde_recorte, imagenes[0].size[1] - 2 * borde_recorte
    imagen_final = Image.new('RGB', (ancho_recorte * numero_cuadrantes, alto_recorte * numero_cuadrantes))

    for i in range(numero_cuadrantes):
        for j in range(numero_cuadrantes):
            idx = i * numero_cuadrantes + j
            imagen_recortada = recortar_imagen(imagenes[idx], (borde_recorte, borde_recorte, ancho_recorte + borde_recorte, alto_recorte + borde_recorte))
            imagen_final.paste(imagen_recortada, (j * ancho_recorte, i * alto_recorte))
            
    return imagen_final

# Función para crear un enlace descargable desde una imagen PIL
def create_download_link(image, title = "Descargar imagen", filename = "imagen.png"):  
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}">{title}</a>'
    return href

def main():
    st.title('Generador de Texturas Segmentadas')
    
    st.sidebar.header('Información sobre los Parámetros')
    st.sidebar.markdown('**Coordenadas (latitud, longitud):** Las coordenadas geográficas del centro del área que desea mapear. Más decimales incrementarán la precisión de la ubicación.')
    st.sidebar.markdown('**Lado (km):** Tamaño en kilómetros del lado del cuadrado que desea mapear.')
    st.sidebar.markdown('**API Key:** Clave de acceso al servicio de mapas de Google.')
    st.sidebar.markdown('**Borde de recorte:** (NO TOCAR) Número de píxeles para recortar las marcas de agua alrededor del borde de cada imagen.')
    st.sidebar.markdown('**Tamaño:** Resolución de cada segmento solicitado a google maps, NO GARANTIZA LA DEVOLUCION DE IMAGENES EN ESA CALIDAD, pero se ponde el valor maximo para obtener el mejor resultado posible')
    st.sidebar.markdown('**Escala:** Factor de escalado para la imagen. Aumentar la escala mejorará la calidad de la imagen, permitiendo más detalles. Puede ser 1, 2, 3 o 4.')
    st.sidebar.markdown('**Tipo de mapa:** Tipo de mapa generado.')
    st.sidebar.markdown('**Segmentos:** Número de segmentos en los que se divide la imagen. Puede ser 1, 4, 16, ... Más segmentos pueden proporcionar más detalles en áreas grandes. ')
    st.sidebar.markdown('\n')
    st.sidebar.markdown('Mientras mas segmentos mas se tarda la peticion y el proceso de recorte y unir las imagenes, ESPERAR A QUE SE GENERE UN ENLACE DE DESCARGA EN LA PARTE INFERIOR')

    # Entradas
    coordenadas = st.text_input('Coordenadas (latitud, longitud):', value='4.7586562291, -74.0657205711')
    latitud_centro, longitud_centro = [float(x) for x in coordenadas.split(',')]
    lado_total_km = st.number_input('Lado (km):', value=20)
    borde_recorte = st.number_input('Borde de recorte:', value=115)
    api_key = st.text_input('API Key:', value='AIzaSyAqoHZdZiLpBu024UBXHas-F51UjnwuZvA')
    size = st.text_input('Tamaño de segegmento:', value='2048x2048')
    scale = st.slider('Escala:', min_value=1, max_value=4, value=4)
    maptype = st.selectbox('Tipo de mapa:', options=['satellite', 'roadmap', 'terrain'], index=0)
    segmentos = st.selectbox('Segmentos:', options=[1, 4, 16, 36], index=1)

    if st.button('GENERAR TEXTURA'):
        try:
            if segmentos == 1:
                imagen_final = obtener_imagen_cuadrante(api_key, latitud_centro, longitud_centro, lado_total_km, size=size, scale=scale, maptype=maptype)
                # Verificar si la imagen fue obtenida exitosamente
                if imagen_final:
                    imagen_final = recortar_imagen(imagen_final, (borde_recorte, borde_recorte, imagen_final.size[0] - borde_recorte, imagen_final.size[1] - borde_recorte))
                else:
                    st.warning('Error al obtener la imagen. Verifica la clave de la API o los parámetros ingresados.')
                    return
            else:
                imagenes = obtener_imagenes_segmentadas(api_key, latitud_centro, longitud_centro, lado_total_km, segmentos, size=size, scale=scale, maptype=maptype)
                # Verificar si las imágenes fueron obtenidas exitosamente
                if all(imagen for imagen in imagenes):
                    imagen_final = unir_imagenes_recortadas(imagenes, borde_recorte, segmentos)
                else:
                    st.warning('Error al obtener las imágenes. Verifica la clave de la API o los parámetros ingresados.')
                    return

            imagen_mostrar = imagen_final.resize((500, 500))
            st.image(imagen_mostrar, caption='Imagen generada', use_column_width=False)

            # Generar enlace de descarga para la imagen
            final_width, final_height = imagen_final.size
            filename = f"Textura_{segmentos}_segmentos_{final_width}x{final_height}.png"
            download_link = create_download_link(imagen_final, filename=filename)
            st.markdown(download_link, unsafe_allow_html=True)
        except Exception as e:
            # Manejar cualquier excepción inesperada
            print(f"Error inesperado: {str(e)}")
            st.warning('Ocurrió un error inesperado. Inténtalo de nuevo.')

if __name__ == "__main__":
    main()



