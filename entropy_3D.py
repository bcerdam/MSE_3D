import numpy as np
from PIL import Image

import PIL.Image
import cv2
import entropy_3D
import numpy as np
import pandas as pd
import neurokit2 as nk
import seaborn as sns
import matplotlib.pyplot as plt


'''
MUY IMPORTANTE: Me base fuertemente en la formula de coarse graining para series de tiempo, por lo tanto cuenta desde 1 
hasta N/t. Por lo tanto, al ocupar esta funcion, X (La lista de imagenes), en la posicion X[0] tiene que llevar 
cualquier cosa (Yo puse un string), pero es necesario para que empieze a contar bien las imagenes.

coarse_graining_Z(X, t): Recibe lista de frames del video, devuelve lista coarse-graneada de esas imagenes. 
En el nombre tiene "Z" porque combinado con la entropia 2D, esta seria la tercera dimension. 

X = Lista de imagenes que componen video.
t = escala.
'''
def coarse_graining_Z(X, t):
    coarse_list = []
    if t == 1:
        return [x.convert("L") for x in X[1:]]
    else:
        # for j in range(1, int((len(X)-1)/t)+1):
        for j in range(1, (int(len(X)/t)+1)):
            lista_imagenes = []
            for i in range((j-1)*t+1, j*t):
                i = abs(i)
                lista_imagenes.append(X[i])
            coarse_list.append(promedio_imagenes(lista_imagenes))
    return coarse_list

'''
promedio_imagenes(lista_imagenes): Recibe imagenes del video y devuelve imagen promediada. 
lista_imagenes = lista que tiene imagenes a promediar.

Es necesario convertir las imagenes a RGB: im = Image.open(path).convert("RGB")
'''

def promedio_imagenes(lista_imagenes):
    imagenes = np.array([np.array(imagen.convert("L")) for imagen in lista_imagenes])
    array_promedio = np.array(np.mean(imagenes, axis=(0)), dtype=np.uint8)
    array_promedio = Image.fromarray(array_promedio)
    return array_promedio


'''
mp4_to_frames(mp4_path): Recibe path de .mp4, devuelve una lista que contiene sus frames.

Input:
mp4_path: str

Output:
frame_list: list
'''

def mp4_to_frames(mp4_path):
    frame_list = ['']
    video = cv2.VideoCapture(mp4_path)
    frame_bool, image = video.read()
    while frame_bool:
        frame_list.append(PIL.Image.fromarray(image))
        frame_bool, image = video.read()
    return frame_list

'''
extracts(mp4_path): recibe path de .mp4, devuelve matriz de video original, en donde cada pixel es una serie de tiempo,
representando como cambia ese pixel a lo largo del video.

Input:
mp4_path: str

Output:
serie_pixeles: list matrix
'''

def extracts(mp4_path):
    coarse_list = entropy_3D.coarse_graining_Z(mp4_to_frames(mp4_path), 1)
    # coarse_list = entropy_3D.coarse_graining_Z(mp4_path, 1) Por si no hay video, solamnete sus frames.
    w, h = coarse_list[1].size
    serie_pixeles = [[] for x in range(w * h)]
    for frame in coarse_list:
        if type(frame) == str:
            continue
        else:
            frame = np.array(frame).flatten()
            for c, pixel in enumerate(frame):
                serie_pixeles[c].append(pixel)
    return serie_pixeles


'''
entropy_3d(mp4_path, scale, og, m, r): recibe path de .mp4 y parametros, para calcular su entropia en una escala determinada.

Input:
mp4_path: str
scale: int
og: list matrix (Se consigue con extracts(mp4_path))
m (dimension, neurokit2 param): int
r (tolerance, neurokit2 param): float

Output:
serie_curvas: list matrix (cada entrada es el valor de entropia de cada serie de tiempo del pixel determinado)
'''

def entropy_3d(mp4_path, scale, og, m, r):
    coarse_list = entropy_3D.coarse_graining_Z(mp4_to_frames(mp4_path), scale)
    # coarse_list = entropy_3D.coarse_graining_Z(mp4_path, scale) Por si no hay video, solamnete sus frames.
    w, h = coarse_list[1].size
    serie_pixeles = [[] for x in range(w * h)]
    serie_curvas = [[] for x in range(w * h)]
    for frame in coarse_list:
        if type(frame) == str:
            continue
        else:
            frame = np.array(frame).flatten()
            for c, pixel in enumerate(frame):
                serie_pixeles[c].append(pixel)
    for c, ps in enumerate(serie_pixeles):
        print(f'iteracion: {scale} {c}')
        fuzzyen, info = nk.entropy_fuzzy(signal=pd.Series(ps, dtype=np.uint8), dimension=m,
                                         tolerance=r*np.std(pd.Series(og[c], dtype=np.uint8)))
        if np.isnan(fuzzyen):
            serie_curvas[c].append(0)
        else:
            serie_curvas[c].append(fuzzyen)
    return serie_curvas


'''
mse_entropy_3d(mp4_path, scales, m , r): Recibe .mp4 path, calcula su entropia a varias escalas.

Input:
mp4_path: str
scales: int
m (dimension, neurokit2 param): int
r (tolerance, neurokit2 param): float

Output:
valores_finales: list (Son los valores de la curva de entropia final que representa complejidad del video)
'''

def mse_entropy_3d(mp4_path, scales, m, r):
    og = extracts(mp4_path)
    serie_curvas_finales = []
    for scale in range(1, scales+1):
        if scale == 1:
            serie_curvas = entropy_3d(mp4_path, scale, og, m, r)
            serie_curvas_finales = serie_curvas
        else:
            serie_curvas = entropy_3d(mp4_path, scale, og, m, r)
            for c, pixel in enumerate(serie_curvas_finales):
                serie_curvas_finales[c].append(serie_curvas[c][0])
    valores_finales = []
    suma = []
    for x in range(scales):
        for serie in serie_curvas_finales:
            suma.append(serie[x])
        promedio = sum(suma) / len(serie_curvas_finales)
        valores_finales.append(promedio)
        suma = []
    return valores_finales

