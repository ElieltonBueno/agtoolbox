from __future__ import unicode_literals
import arcpy
from arcpy import env
from arcpy.sa import *
import sys
import os
import tempfile
import uuid

# Carrega os parâmetros do ArcGIS
Contorno = arcpy.GetParameterAsText(0)
Amostra = arcpy.GetParameterAsText(1)
CTC = arcpy.GetParameterAsText(2)
V = arcpy.GetParameterAsText(3)
V2 = arcpy.GetParameterAsText(4)
PRNT = arcpy.GetParameterAsText(5)
TamPixel = arcpy.GetParameterAsText (6)
DMin = arcpy.GetParameter (7)
DMax = arcpy.GetParameter (8)
Saida = arcpy.GetParameterAsText(9)

# Expressão para conferir se os valores de dose mínima e máxima não causarão erros
if DMin > DMax:
    arcpy.AddError("O valor de dose mínima não pode ser maior que o valor de dose máxima")

# Expressão para validar os dados da amostra
expressãoCTC = "getClass(!CTC!)"
blocoCTC = """def getClass(CTC):
    if CTC > 1000:
        return None
    if CTC <= 0:
        return None
    else:
        return CTC"""

expressãoV = "getClass(!V!)"
blocoV = """def getClass(V):
    if V > 1000:
        return None
    if V <= 0:
        return None
    else:
        return V"""

# Valida os dados da amostra
arcpy.CalculateField_management (Amostra, CTC, expressãoCTC, "PYTHON_9.3", blocoCTC)
arcpy.CalculateField_management (Amostra, V, expressãoV, "PYTHON_9.3", blocoV)

# Faz o IDW da CTC e da V%
outIDWCTC = Idw(Amostra, CTC)
outIDWV = Idw(Amostra, V)

# Faz o cálculo da Necessidade de calagem difinindo valores abaixo de 0 como o valor estipulado na dose mínima e os valores acima do máximo como o valor estipulado na dose máxima
outR = (int(V2)-outIDWV)*outIDWCTC*100/int(PRNT)/100
outRNC = Con(outR<DMin,DMin,outR)
outRasNC = Con(outRNC>DMax,DMax,outRNC)

# Cria a grade para fazer a vetorização
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
    celula = float(TamPixel)
    tamanho = str(celula)

    arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                   oppositeCoorner,
                                   "NO_LABELS", "#", "POLYGON")
    # Recorta a grade com o contorno
    arcpy.Intersect_analysis(["in_memory/grids", arquivo_projetado], saida_um, "ALL")

    # Define o sistema de coordenadas para projetar
    arcpy.DefineProjection_management(saida_um, srid)

    # Projeta novamente para Coordenadas Geográficas
    saida_dois = tempfile.gettempdir() + '\\' + str('temporaryprojection2')[16:] + '.shp'
    arcpy.Project_management(saida_um, saida_dois, arcpy.SpatialReference(4326))

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
    celula = float(TamPixel) * (100)
    tamanho = str(celula)

    arcpy.CreateFishnet_management("in_memory/grids", originCoordinate, yAxisCoordinate, tamanho, tamanho, "0", "0",
                                    oppositeCoorner,
                                    "NO_LABELS", "#", "POLYGON")
    # Recorta a grade com o contorno
    arcpy.Intersect_analysis(["in_memory/grids", Contorno], saida_um, "ALL")

    # Define o sistema de coordenadas para projetar
    arcpy.DefineProjection_management(saida_um, desc)

    # Projeta novamente para Coordenadas Geográficas
    saida_dois = tempfile.gettempdir() + '\\' + str('temporaryprojection2')[16:] + '.shp'
    arcpy.Project_management(saida_um, saida_dois, arcpy.SpatialReference(4326))

# Realiza a vetorização
outTabela = ZonalStatisticsAsTable(saida_dois, "FID", outRasNC, "tabela")
tabela_unida = arcpy.AddJoin_management(saida_dois, "FID", outTabela, "OBJECTID")
arcpy.CopyFeatures_management(tabela_unida, Saida)

# Adiciona o campo NC a grade
arcpy.AddField_management(Saida, "NC", "FLOAT")

# Copia o valor de MEAN para NC
arcpy.CalculateField_management(Saida, "NC", '!tabela_MEA!')








