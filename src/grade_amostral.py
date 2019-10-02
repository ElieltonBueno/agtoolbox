# coding: utf-8
from __future__ import unicode_literals
import arcpy
import sys
import os
import tempfile
import uuid

# Carrega os parâmetros do ArcGIS
Contorno = arcpy.GetParameterAsText(0)
Densidade = arcpy.GetParameter(1)
Saida = arcpy.GetParameterAsText(2)
Converter = arcpy.GetParameterAsText(3)

# Converte novamente para Coordenadas Geográficas
if Converter == "true":
    

    # Descobre o sistema de coordenandas da classe de feição
    desc = arcpy.Describe(Contorno).spatialReference


    # Define o arquivo projetado
    arquivo_projetado = None

    # Define o arquivo projetado final
    saida_um = tempfile.gettempdir() + '\\' + str('temporaryprojection')[16:] + '.shp'

    # Projeta a classe de feição caso estaja no sistema de coordenadas geográficas
    if desc.exportToString().startswith('GEOGCS'):

        # Inicializa a extensão da classe de feição
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Varre as feições atualizado a extensão da grade
        for feicao in arcpy.da.SearchCursor(Contorno, ["OID@", "SHAPE@"]):
            for parte in feicao[1]:
                for ponto in parte:
                    if ponto:
                        x_max = max(x_max, ponto.X)
                        y_max = max(y_max, ponto.Y)
                        x_min = min(x_min, ponto.X)
                        y_min = min(y_min, ponto.Y)

        # Gera o nome de um arquivo temporário
        arquivo_projetado = tempfile.gettempdir() + '\\' + str(uuid.uuid4())[16:] + '.shp'

        # Obtém a zona UTM em que a classe de feição se encontra
        srid = 32000 + (700 if (((y_max + y_min) / 2) < 0) else 600) + int((((x_max + x_min) / 2) + 186.0) / 6)

        # Projeta a classe de feição em coordenadas planas UTM
        arcpy.Project_management(Contorno, arquivo_projetado, arcpy.SpatialReference(srid))



        # Inicializa a extenssão da grade
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Varre as feições atualizado a extesão da grade
        for feicao in arcpy.da.SearchCursor(arquivo_projetado, ["OID@", "SHAPE@"]):
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
        celula = float(Densidade) * (100)
        tamanho = str(celula)

        arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                       oppositeCoorner,
                                       "NO_LABELS", "#", "POLYGON")
        # Recorta a grade com o contorno
        arcpy.Intersect_analysis(["in_memory/grids", arquivo_projetado], saida_um, "ALL")

        # Define o sistema de coordenadas para projetar
        arcpy.DefineProjection_management(saida_um, srid)

        # Projeta novamente para Coordenadas Geográficas
        arcpy.Project_management(saida_um, Saida, arcpy.SpatialReference(4326))

            

    # Caso o arquivo seja em coordenadas planas
    else:    

        # Inicializa a extenssão da grade
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Descobre o sistema de coordenandas da classe de feição
        desc = arcpy.Describe(Contorno).spatialReference
    
        # Varre as feições atualizado a extesão da grade
        for feicao in arcpy.da.SearchCursor(Contorno, ["OID@", "SHAPE@"]):
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
        celula = float(Densidade) * (100)
        tamanho = str(celula)

        arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                        oppositeCoorner,
                                        "NO_LABELS", "#", "POLYGON")
        # Recorta a grade com o contorno
        arcpy.Intersect_analysis(["in_memory/grids", Contorno], saida_um, "ALL")

        # Define o sistema de coordenadas para projetar
        arcpy.DefineProjection_management(saida_um, desc)

        # Projeta novamente para Coordenadas Geográficas
        arcpy.Project_management(saida_um, Saida, arcpy.SpatialReference(4326))

# Deixar em coordenadas planas    
else:
    # Descobre o sistema de coordenandas da classe de feição
    desc = arcpy.Describe(Contorno).spatialReference

    # Define o arquivo projetado
    arquivo_projetado = None

    # Projeta a classe de feição caso estaja no sistema de coordenadas geográficas
    if desc.exportToString().startswith('GEOGCS'):

        # Inicializa a extensão da classe de feição
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Varre as feições atualizado a extensão da grade
        for feicao in arcpy.da.SearchCursor(Contorno, ["OID@", "SHAPE@"]):
            for parte in feicao[1]:
                for ponto in parte:
                    if ponto:
                        x_max = max(x_max, ponto.X)
                        y_max = max(y_max, ponto.Y)
                        x_min = min(x_min, ponto.X)
                        y_min = min(y_min, ponto.Y)

        # Gera o nome de um arquivo temporário
        arquivo_projetado = tempfile.gettempdir() + '\\' + str(uuid.uuid4())[16:] + '.shp'

        # Obtém a zona UTM em que a classe de feição se encontra
        srid = 32000 + (700 if (((y_max + y_min) / 2) < 0) else 600) + int((((x_max + x_min) / 2) + 186.0) / 6)

        # Projeta a classe de feição em coordenadas planas UTM
        arcpy.Project_management(Contorno, arquivo_projetado, arcpy.SpatialReference(srid))



        # Inicializa a extenssão da grade
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Varre as feições atualizado a extesão da grade
        for feicao in arcpy.da.SearchCursor(arquivo_projetado, ["OID@", "SHAPE@"]):
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
        celula = float(Densidade) * (100)
        tamanho = str(celula)

        arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                       oppositeCoorner,
                                       "NO_LABELS", "#", "POLYGON")
        # Recorta a grade com o contorno
        arcpy.Intersect_analysis(["in_memory/grids", arquivo_projetado], Saida, "ALL")

            

    # Caso o arquivo seja em coordenadas planas
    else:    

        # Inicializa a extenssão da grade
        x_max = -999999999999999.0
        y_max = -999999999999999.0
        x_min = 999999999999999.0
        y_min = 999999999999999.0

        # Varre as feições atualizado a extesão da grade
        for feicao in arcpy.da.SearchCursor(Contorno, ["OID@", "SHAPE@"]):
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
        celula = float(Densidade) * (100)
        tamanho = str(celula)

        arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                        oppositeCoorner,
                                        "NO_LABELS", "#", "POLYGON")
        # Recorta a grade com o contorno
        arcpy.Intersect_analysis(["in_memory/grids", Contorno], Saida, "ALL")

       


