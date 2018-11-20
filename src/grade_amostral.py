# coding: utf-8
from __future__ import unicode_literals
import arcpy
import sys
import os
import tempfile
import uuid

# Cria o arquivo de debug
# f = open("C:\\x\\debug.txt", "w+")

# Carrega os parâmetros do ArcGIS
contorno = arcpy.GetParameterAsText(0)
densidade = arcpy.GetParameterAsText(1)
saida = arcpy.GetParameterAsText(2)

# Descobre o sistema de coordenandas da classe de feição
desc = arcpy.Describe(contorno)
SR = desc.spatialReference

# Define o arquivo projetado
arquivo_projetado = None

# Projeta a classe de feição caso estaja no sistema de coordenadas geográficas
if SR.exportToString().startswith('GEOGCS'):

    # Inicializa a extensão da classe de feição
    x_max = -999999999999999.0
    y_max = -999999999999999.0
    x_min = 999999999999999.0
    y_min = 999999999999999.0

    # Varre as feições atualizado a extensão da grade
    for feicao in arcpy.da.SearchCursor(contorno, ["OID@", "SHAPE@"]):
        for parte in feicao[1]:
            for ponto in parte:
                if ponto:
                    x_max = max(x_max, ponto.X)
                    y_max = max(y_max, ponto.Y)
                    x_min = min(x_min, ponto.X)
                    y_min = min(y_min, ponto.Y)

    # Gera o nonme de um arquivo temporário
    arquivo_projetado = tempfile.gettempdir() + '\\' + str(uuid.uuid4())[16:] + '.shp'

    # Obtém a zona UTM em que a classe de feição se encontra
    srid = 32000 + (700 if (((y_max + y_min) / 2) < 0) else 600) + int((((x_max + x_min) / 2) + 186.0) / 6)

    # Projeta a classe de feição em coordenadas planas UTM
    arcpy.Project_management(contorno, arquivo_projetado, arcpy.SpatialReference(srid))

# Deine o contorno final
contorno_final = arquivo_projetado if arquivo_projetado is not None else contorno

# Inicializa a extessão da grade
x_max = -999999999999999.0
y_max = -999999999999999.0
x_min = 999999999999999.0
y_min = 999999999999999.0

# Varre as feições atualizado a extesão da grade
for feicao in arcpy.da.SearchCursor(contorno_final, ["OID@", "SHAPE@"]):
    for parte in feicao[1]:
        for ponto in parte:
            if ponto:
                x_max = max(x_max, ponto.X)
                y_max = max(y_max, ponto.Y)
                x_min = min(x_min, ponto.X)
                y_min = min(y_min, ponto.Y)

# Cria a grade
originCoordinate = ("{} {}".format(x_min, y_min))
yAxisCoordinate = ("{} {}".format(x_min, y_max))
oppositeCoorner = ("{} {}".format(x_max, y_max))
templateExtent = ("{} {} {} {}".format(x_max, x_min, y_min, y_max))
celula = float(densidade) * (100)
tamanho = str(celula)

arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                               oppositeCoorner,
                               "NO_LABELS", "#", "POLYGON")
# Recorta a grade com o contorno
arcpy.Intersect_analysis(["in_memory/grids", contorno_final], saida, "ALL")
