from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget
from PyQt5.QtGui import QPixmap

import sys  # LIBRERIA DEL SISTEMA (PARA TRABAJAR CON COMANDOS DEL OS)

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import math
import thingspeak
import threading
import numpy as np


# Importa el archivo de la interfaz grafica y las variables de la clase definida
import mainwindow
from variables import variables as var


def createWigetPlot(self):
    self.dpi = 70  # PUNTOS POR PULGADA
    # SE DEFINE LA FIGURA CON EL TAMAÑO Y EL COLOR DE FONDO:
    self.fig = Figure((5.0, 3.0), dpi=self.dpi, facecolor=(0.94, 0.94, 0.94), edgecolor=(0, 0, 0))
    self.axes = self.fig.add_subplot(111)
    # SE ASOCIA STATIC CANVAS A LA FIGURA CREADA
    self.static_canvas = FigureCanvas(self.fig)
    self.static_canvas.setParent(self)
    # A LA FIGURA SE LE DEFINE CON MARGENES PEQUEÑAS:
    self.fig.tight_layout()
    # AL LAYOUT DE LA INTERFAZ GRAFICA SE LE AGREGA EL WIDGET DE LA FIGURA EN CANVAS:
    self.layout_plot.addWidget(self.static_canvas)
    self.layout_plot.setStretchFactor(self.static_canvas, 1)
    self.setLayout(self.layout_plot)

    # SE DEFINEN LOS VALORES Y DIMENSIONES DE LAS FIGURAS EN EL CANVAS:
    var._static_ax = self.static_canvas.figure.gca()
    var._static_ax.set_xticks(np.arange(0,24,1))
    var._static_ax.set_yticks(np.arange(0,1400,100))
    var._static_ax.set_xlim(0, 24)
    var._static_ax.set_ylim(0, 1400)
    var._static_ax.set_xlabel('Hora del dia [Hr]')
    var._static_ax.set_ylabel('Radiacion [W/m^2]')

    # SE ANADE LA GRILLA A LA FIGURA Y SE DEFINE LA RELACION DE ASPECTO ENTRE LOS EJES:
    var._static_ax.grid()
    #var._static_ax.set_aspect('equal')

def drawPoint(self,time, Gh, Giy, Ghmodel, Giymodel):
    # Grafica en tiempo real la radiacion solar
    first = False
    if var.currentTime == []:
        first = True
    var.currentTime.extend([time])  # Concatena en x con las anteriores
    var.currentGhmeas.extend([Gh])  # Concatena en y con las anteriores
    var.currentGiymeas.extend([Giy])  # Concatena en y con las anteriores
    var.currentGhmodel.extend([Ghmodel]) # Concatena en y con las anteriores
    var.currentGiymodel.extend([Giymodel])  # Concatena en y con las anteriores
    line1, = var._static_ax.plot(var.currentTime, var.currentGhmeas, color='red', lw=1,label='Gh piranometro')
    line1.figure.canvas.draw()  # DIBUJA LA LINEA DEFINIDA
    line2, = var._static_ax.plot(var.currentTime, var.currentGiymeas, color='blue', lw=1,label='Giy piranometro')
    line2.figure.canvas.draw()  # DIBUJA LA LINEA DEFINIDA
    line3, = var._static_ax.plot(var.currentTime, var.currentGhmodel, color='green', lw=1, label='Gh modelo')
    line3.figure.canvas.draw()  # DIBUJA LA LINEA DEFINIDA
    line4, = var._static_ax.plot(var.currentTime, var.currentGiymodel, color='magenta', lw=1, label='Giy modelo')
    line4.figure.canvas.draw()  # DIBUJA LA LINEA DEFINIDA
    if first:
        var._static_ax.legend()

class ExampleApp(QtWidgets.QMainWindow, mainwindow.Ui_mainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()

        ############################### NOTA ###############################
        # Los angulos que se trabajan en este codigo estan todos en radianes
        # exceptuando los angulos de las variables con el sufijo _deg
        ###################################################################

        self.setupUi(self)  # Carga la interfaz grafica y la asocia con la clase ExampleApp
        self.retranslateUi(self) # Configura los valores de las lineas

        self.layout_plot.setEnabled(0)
        createWigetPlot(self)

        self.bloquearsalidatiemporeal()

        # Asocia el comportamiento de los botones para cargar y generar los archivos
        self.pushButton_Calcular.clicked.connect(self.correr)
        self.check_02TiempoReal.stateChanged.connect(self.tiemporeal)

    def calcdiadelanio(self,dd, mm):
        # Calcula el dia del anio (nd) a partir del numero del mes (mm) y el dia del mes (dd)
        nd = dd + 31 * (mm - 1)  # Diapositiva 22 - 1. Introduccion en la energia solar
        if mm >= 3:
            nd = nd - int(0.4 * mm + 2.3)
        return nd

    def calcbeta(self,nd):
        # Calcula el angulo beta (beta) a partir del dia del anio (nd)
        beta_deg = (nd - 1) * (360 / 365)  # Diapositiva 24 - 1. Introduccion en la energia solar
        beta = math.radians(beta_deg)  # Conversion a radianes
        return beta

    def calcdeclinacion(self,beta):
        # Calcula la declinacion del sol (delta) a partir del angulo beta (beta)
        delta = (0.006918 - 0.399912 * math.cos(beta) + 0.070257 * math.sin(beta) - 0.006758 * math.cos(2 * beta)
                 + 0.000907 * math.sin(2 * beta) - 0.002697 * math.cos(3 * beta) + 0.00148 * math.sin(3 * beta))
        # Declinacion en radianes
        # Pagina 36 - Duffie & Beckman
        return delta

    def calchoras(self,hh, mm, ss):
        # Convierte el tiempo del formato de horas:minutos:segundos (hh:mm:ss) a horas (outhoras)
        outhoras = hh + mm / 60 + ss / 3600
        return outhoras

    def calctiempouniversal(self,TL, c1, c2):
        # Calcula el tiempo universal (TU) a partir del tiempo legal (TL), el huso horario (c1) y la correcion de
        # tiempo de verano (c2)
        TU = TL - c1 - c2  # Diapositiva 25 - 1. Introduccion en la energia solar
        return TU

    def calctiemposolarmedio(self,TU, Long_deg):
        # Calcula el tiempo solar medio (TSM) a partir del tiempo universal (TU) y la longitud de lugar en grados (Long_deg)
        TSM = TU - (Long_deg / 15)  # Diapositiva 25 - 1. Introduccion en la energia solar
        return TSM

    def calcecuaciondeltiempo(self,beta):
        # Calcula la ecuacion del tiempo en MINUTOS(ET) a partir del angulo beta (beta)
        ET = 229.2 * (0.000075 + 0.001868 * math.cos(beta) - 0.032077 * math.sin(beta)
                      - 0.014615 * math.cos(2 * beta) - 0.04089 * math.sin(2 * beta))
        # Diapositiva 24 - 1. Introduccion en la energia solar
        return ET

    def calctiemposolarverdadero(self,TSM, ET):
        # Calcula el tiempo solar verdadero (TSV) a partir del tiempo solar medio (TSM) y la ecuacion
        # del tiempo (ET)
        ET_horas = ET / 60
        TSV = TSM + ET_horas  # Diapositiva 24 - 1. Introduccion en la energia solar
        return TSV

    def calcangulohorario(self,TSV):
        # Calcula el angulo horario (omega) a partir del tiempo solar verdadero (TSV)
        omega_deg = (TSV - 12) * 15  # Diapositiva 24 - 1. Introduccion en la energia solar
        omega = math.radians(omega_deg)  # Conversion a radianes
        return omega

    def calcaltura(self,delta, omega, Lat):
        # Calcula la altura angular (h) a partir de la declinacion (delta), el angulo horario (omega) y la
        # latitud en radianes (Lat)
        senodeh = math.cos(delta) * math.cos(omega) * math.cos(Lat) + math.sin(delta) * math.sin(Lat)
        h = math.asin(senodeh)
        # Diapositiva 26 - 1. Introduccion en la energia solar
        return h

    def calcazimuth(self,h, delta, omega):
        # Calcula el azimuth (a) a partir de la altura angular (h), la declinacion (delta) y el angulo horario
        # (omega)
        senodea = (math.cos(delta) * math.sin(omega)) / math.cos(h)
        a = math.asin(senodea)
        # Diapositiva 26 - 1. Introduccion en la energia solar
        # Nota: solar azimuth angle
        # Otra formula para calcular el angulo de azimuth se presenta en la P.37 de Duffie & Beckman
        return a

    def calcradiacionsolarextraterrestre(self,Gsc, beta):
        # Calcula la radiacion solar extraterrestre (Gon) a partir de la constante solar (Gsc) y el angulo beta (beta)
        Gon = Gsc * (
            1.000110 + 0.034221 * math.cos(beta) + 0.001280 * math.sin(beta) + 0.000719 * math.cos(2 * beta)
            + 0.000077 * math.sin(2 * beta))
        # Pagina 31 - Duffie & Beckman
        return Gon

    def calciluminacionsolarfueradelaatmosfera(self,Gsc, nd):
        # Calcula la iluminacion fuera de la atmosfera (I) a partit de la constante solar (Gsc) y el dia del anio (nd)
        angulo_deg = (nd - 2.72) * (360 / 365.25)
        angulo = math.radians(angulo_deg)
        I = Gsc * (1 + 0.034 * math.cos(angulo))
        # Diapositiva 30 - 1. Introduccion en la energia solar
        return I

    def calcradiaciondirecta(self,I, i, o, h, a):
        # Calcula la radiacion solar directa (S) a partir de la altura angular (h), el angulo de inclinacion (i), el angulo
        # de orientacion (o), el angulo de azimuth (a) y iluminacion fuera de la atmosfera (I)
        S = I * (math.sin(i) * math.cos(h) * math.cos(a - o) + math.cos(i) * math.sin(h))
        # Diapositiva 30 - 1. Introduccion en la energia solar
        return S

    def calcangulodeincidencia(self,delta, lat, i, omega, o):
        # Calcula el angulo de incidencia (theta) a partir de la declinacion (delta), la latitud (lat), el angulo de
        # inclinacion (i), el angulo horario (omega) y el angulo de orientacion (o)
        cosdetheta = math.sin(delta) * math.sin(lat) * math.cos(i) \
                     - math.sin(delta) * math.cos(lat) * math.sin(i) * math.cos(o) \
                     + math.cos(delta) * math.cos(lat) * math.cos(i) * math.cos(omega) \
                     + math.cos(delta) * math.sin(lat) * math.sin(i) * math.cos(o) * math.cos(omega) \
                     + math.cos(delta) * math.sin(i) * math.sin(o) * math.sin(omega)
        theta = math.acos(cosdetheta)
        # Pagina 36 - Duffie & Beckman
        # Nota: surface azimuth angle = angulo de orientacion
        return theta

    def calcangulocenital(self,lat, delta, omega):
        # Calcula el angulo cenital (thetaz) a partir de la latitud (lat), la declinacion (delta) y el angulo horario
        # (omega)
        cosdethetaz = math.cos(lat) * math.cos(delta) * math.cos(omega) + math.sin(lat) * math.sin(delta)
        thetaz = math.acos(cosdethetaz)
        # Pagina 37 - Duffie & Beckman
        return thetaz

    def calcangulodeperfil(self,h, a, o):
        # Calcula el angulo de perfil (ap) a partir de la altura angular (h), el angulo de azimuth (a) y la orientacion (o)
        tandeap = math.tan(h) / math.cos(a - o)
        ap = math.atan(tandeap)
        # Pagina 39 - Duffie & Beckman
        return ap

    def calcangulohorarioatardecer(self,lat, delta):
        # Calcula el angulo horario en la puesta de sol (omega_s) a partir de la latitud (lat) y de la declinacion (delta)
        cosdeomegas = - math.tan(lat) * math.tan(delta)
        omega_s = math.acos(cosdeomegas)
        # Pagina 39 - Duffie & Beckman
        return omega_s

    def calcamaneceratardecer(self,vrot, omega_s):
        # Calcula la hora de amanecer (aman) y atardecer (atar) a partir de la velocidad de rotacion de la tierra (vrot) y
        # el angulo horario de atardecer (omega_s)
        distanciadelmediodia = omega_s / vrot
        aman = 12 - distanciadelmediodia
        atar = 12 + distanciadelmediodia
        # Pagina 39 - Duffie & Beckman
        return aman, atar

    def calcrazonderadiaciondehazensuperficieinclinada(self,theta, thetaz):
        # Calcula la rezon entre haz radiado en una superficie inclinada con el haz radiado a una superficie horizontal (Rb)
        # a partir del angulo de incidencia (theta) y el angulo de cenital (thetaz)
        Rb = math.cos(theta) / math.cos(thetaz)
        # Pagina 46 - Duffie & Beckman
        return Rb

    # def calcradiaciondirectahorizontal(self,Rb,Siy):
    #     Sh = Rb * Siy
    #     return Sh

    def calctransmitanciaatmosfeficapararadiaciondirecta(self,altitud, thetaz):
        # Calcula la transmitacia atmosférica para la radiacion directa (Taub) a partir de la altitud del observador en
        # kilometros(altitud) y el angulo cenital (thetaz)
        a0_ast = 0.4237 - 0.00821 * (6 - altitud) ** 2
        a1_ast = 0.5055 + 0.00595 * (6.5 - altitud) ** 2
        k_ast = 0.2711 + 0.01858 * (2.5 - altitud) ** 2
        # Los factores de correccion se definen para clima tropical:
        r0 = 0.95
        r1 = 0.98
        rk = 1.02

        a0 = a0_ast * r0
        a1 = a1_ast * r1
        k = k_ast * rk

        Taub = a0 + a1 * math.exp(-(k / (math.cos(thetaz))))
        # Pagina 90 - Duffie & Beckman
        return Taub

    def calcradiaciondirectanormal(self,Gon, Taub):
        # Calcula la radiacion directa normal (Gcnb) a partir de la radiacion solar extraterrestre (Gon) y la
        # transmitancia atmosferica para radiacion directa (Taub)
        Gcnb = Gon * Taub
        # Pagina 90 - Duffie & Beckman
        return Gcnb

    def calcradiaciondirectahorizontal(self,Gcnb, thetaz):
        # Calcula la radiacion directa horizontal (Gcb) a partir de la radiacion directa normal (Gcnb) y el angulo
        # cenital (thetaz)
        Gcb = Gcnb * math.cos(thetaz)
        # Pagina 90 - Duffie & Beckman
        return Gcb

    def calcradiaciondifusahorizontal(self,Gon, thetaz, Taub):
        # Calcula la radiacion difusa horizontal (Gd) [denotada en las presentaciones como Dh] a partir de la radiacion
        # solar extraterrestre (Gon), el angulo cenital (thetaz) y la transmitancia atmosferica para radiacion directa
        # (Taub)
        Taud = 0.271 - 0.294 * Taub
        Go = Gon * math.cos(thetaz)
        Gd = Taud * Go
        # Pagina 91 - Duffie & Beckman
        return Gd

    def calcradicaciondifusaisotropica(self,Gd, i):
        # Calcula la radiacion difusa isotropica (Gdiso_iy) a partir de la radiacion difusa horizontal (Gd) y la
        # inclinacion (i)
        Gdiso_iy = Gd * (1 + math.cos(i)) / 2
        # Diapositiva 33 - 1. Introduccion en la energia solar
        return Gdiso_iy

    def calcrelacionderadiacionglobal(self,Rb, i, Gcb, Gh, alb):
        # Calcula la relacion de radicacion solar global (Rg = G(i,y)/Gh) a partir de la relacion de radiacion solar
        # directa (Rb), la inclinacion (i), la radiacion directa horizontal (Gcb), la radiacion global horizontal (Gh) y el
        # albedo (alb).
        Rg = (Rb - (1 + math.cos(i)) / 2) * (Gcb / Gh) + (1 + math.cos(i)) / 2 + alb * (1 - math.cos(i)) / 2
        # Diapositiva 34 - 1. Introduccion en la energia solar
        return Rg

    def calcradiacioninclinada(self,Rg, Gh):
        # Calcula radiacion inclinada (G_iy) a partir de la relacion de radicacion solar global (Rg) y la radiacion global
        # horizontal (Gh)
        Giy = Rg * Gh
        # Diapositiva 34 - 1. Introduccion en la energia solar
        return Giy

    def leervalores(self):
        # Lee los valores ingresados en la interfaz grafica
        var.Latitud_deg = float(self.line_01Latitud.text())
        var.Latitud = math.radians(var.Latitud_deg)
        var.Longitud_deg = float(self.line_02Longitud.text())
        var.Longitud = math.radians(var.Longitud_deg)
        var.HusoHorario = float(self.line_03HusoHorario.text())
        var.Inclinacion_deg = float(self.line_04Inclinacion.text())
        var.Inclinacion = math.radians(var.Inclinacion_deg)
        var.Orientacion_deg = float(self.line_05Orientacion.text())
        var.Orientacion = math.radians(var.Orientacion_deg)
        var.Albedo = float(self.line_07Albedo.text())
        var.Altitud = float(self.line_13Altitud.text())
        var.IsVerano = self.check_01Verano.isChecked()
        var.IsRealTime = self.check_02TiempoReal.isChecked()
        if not var.IsRealTime:
            var.Gh = float(self.line_06Gh.text())
            var.HoraESThr = float(self.line_08HoraESTH.text())
            var.HoraESTmin = float(self.line_09HoraESTM.text())
            var.HoraESTsec = float(self.line_10HoraESTS.text())
            var.FechaDia = float(self.line_11FechaDia.text())
            var.FechaMes = float(self.line_12FechaMes.text())

    def escribirrespuesta(self):
        # Eescribe la respuesta en la interfaz grafica
        self.line_16G.setText(str(var.G))
        self.line_17Dh.setText(str(var.Dh))
        self.line_18HoraRealH.setText(str(var.HoraRealhr))
        self.line_19HoraRealM.setText(str(var.HoraRealmin))
        self.line_20HoraRealS.setText(str(var.HoraRealsec))

    def tiemporeal(self):
        var.IsRealTime = self.check_02TiempoReal.isChecked()
        if var.IsRealTime:
            self.bloquearparametrosestaticos()
            self.leertiemporeal()
        else:
            self.bloquearsalidatiemporeal()
            self.leertiemporeal()

    def leertiemporeal(self):
        self.leervalores()
        llamado = threading.Timer(15.0, self.leertiemporeal)
        if var.IsRealTime:
            llamado.start()
        else:
            llamado.cancel()
        readChannelID = 844755
        readAPIKey = 'EC3Y2KLILZ2I5X0W'
        channel = thingspeak.Channel(id=readChannelID, api_key=readAPIKey)

        mensaje = channel.get_field_last(field="field1")
        head, sep, resto = mensaje.partition(":\"")
        fecha, sep, resto = resto.partition("T")
        tiempo, sep, resto = resto.partition("Z")
        trash, sep, resto = resto.partition("field1\":\"")
        radiacion, sep, resto = resto.partition("\"}")

        anio, sep, resto = fecha.partition("-")
        mes, sep, dia = resto.partition("-")

        hora, sep, resto = tiempo.partition(":")
        minuto, sep, segundo = resto.partition(":")

        var.Gh = float(radiacion)
        var.FechaMes = float(mes)
        var.FechaDia = float(dia)
        if var.IsVerano:
            var.HoraESThr = float(hora) + var.HusoHorario + 1
        else:
            var.HoraESThr = float(hora) + var.HusoHorario

        if var.HoraESThr < 0:
            var.HoraESThr = var.HoraESThr + 24
        var.HoraESTmin = float(minuto)
        var.HoraESTsec = float(segundo)
        var.HoraLeida = var.HoraESThr + var.HoraESTmin/60 + var.HoraESTsec/3600

        self.correr()

        self.line_21GhTiempoReal.setText(str(var.Gh))
        self.line_22GTiempoReal.setText(str(var.G))
        self.line_23DhTiempoReal.setText(str(var.Dh))
        self.line_24HoraTiempoReal.setText(str(var.HoraESThr))
        self.line_25MinuTiempoReal.setText(str(var.HoraESTmin))
        self.line_26SeguTiempoReal.setText(str(var.HoraESTsec))

        drawPoint(self,var.HoraLeida,var.Gh,var.G,var.Ghmodelo, var.Giymodelo)

    def bloquearparametrosestaticos(self):
        self.line_06Gh.setDisabled(True)
        self.line_08HoraESTH.setDisabled(True)
        self.line_09HoraESTM.setDisabled(True)
        self.line_10HoraESTS.setDisabled(True)
        self.line_11FechaDia.setDisabled(True)
        self.line_12FechaMes.setDisabled(True)

        self.line_16G.setDisabled(True)
        self.line_17Dh.setDisabled(True)
        self.line_18HoraRealH.setDisabled(True)
        self.line_19HoraRealM.setDisabled(True)
        self.line_20HoraRealS.setDisabled(True)

        self.pushButton_Calcular.setDisabled(True)

        self.line_21GhTiempoReal.setEnabled(True)
        self.line_22GTiempoReal.setEnabled(True)
        self.line_23DhTiempoReal.setEnabled(True)
        self.line_24HoraTiempoReal.setEnabled(True)
        self.line_25MinuTiempoReal.setEnabled(True)
        self.line_26SeguTiempoReal.setEnabled(True)

        self.check_02TiempoReal.setDisabled(True)

    def bloquearsalidatiemporeal(self):
        self.line_06Gh.setEnabled(True)
        self.line_08HoraESTH.setEnabled(True)
        self.line_09HoraESTM.setEnabled(True)
        self.line_10HoraESTS.setEnabled(True)

        self.line_16G.setEnabled(True)
        self.line_17Dh.setEnabled(True)
        self.line_18HoraRealH.setEnabled(True)
        self.line_19HoraRealM.setEnabled(True)
        self.line_20HoraRealS.setEnabled(True)

        self.pushButton_Calcular.setEnabled(True)

        self.line_21GhTiempoReal.setDisabled(True)
        self.line_22GTiempoReal.setDisabled(True)
        self.line_23DhTiempoReal.setDisabled(True)
        self.line_24HoraTiempoReal.setDisabled(True)
        self.line_25MinuTiempoReal.setDisabled(True)
        self.line_26SeguTiempoReal.setDisabled(True)



    def correr(self):
        self.leervalores()
        # Calcula todos los valores para generar la respuesta
        Gsc = 1367  # Valor de la constante solar [W/m^2]
        velrotacion_deg = 15  # Velocidad de rotacion de la tierra [deg/hora]
        velrotacion = math.radians(velrotacion_deg)

        diadelanio = self.calcdiadelanio(var.FechaDia, var.FechaMes)
        # print('Dia del anio')
        # print(diadelanio)

        beta = self.calcbeta(diadelanio)
        # print('Beta')
        # print(beta)

        TL = self.calchoras(var.HoraESThr, var.HoraESTmin, var.HoraESTsec)
        # print('TL')
        # print(TL)

        TU = self.calctiempouniversal(TL, var.HusoHorario, var.IsVerano)
        # print('TU')
        # print(TU)

        TSM = self.calctiemposolarmedio(TU, var.Longitud_deg)
        # print('TSM')
        # print(TSM)

        ET = self.calcecuaciondeltiempo(beta)
        # print('ET')
        # print(ET)

        TSV = self.calctiemposolarverdadero(TSM, ET)
        # print('TSV')
        # print(TSV)

        decimaleshora = TSV % 1
        var.HoraRealhr = int(TSV - decimaleshora)
        minutos = decimaleshora * 60
        decimalesminutos = minutos % 1
        var.HoraRealmin = int(minutos - decimalesminutos)
        segundos = decimalesminutos * 60
        decimalessegundos = segundos % 1
        var.HoraRealsec = int(segundos - decimalessegundos)

        omega = self.calcangulohorario(TSV)
        # print('Angulo horario')
        # print(omega)

        delta = self.calcdeclinacion(beta)
        # print('Declinacion')
        # print(delta)

        alt_ang = self.calcaltura(delta, omega, var.Latitud)
        # print('Altura angular')
        # print(alt_ang)

        azimuth = self.calcazimuth(alt_ang, delta, omega)
        # print('Azimuth')
        # print(azimuth)

        Gon = self.calcradiacionsolarextraterrestre(Gsc, beta)
        # print('Radiacion solar extraterrestre (W/m^2)')
        # print(Gon)

        I = self.calciluminacionsolarfueradelaatmosfera(Gsc, beta)
        # print('Iluminacion fuera de la atmosfera (W/m^2)')
        # print(I)

        # S = calcradiaciondirecta(Gon,inclinacion,orientacion,alt_ang,azimuth)
        Siy = self.calcradiaciondirecta(I, var.Inclinacion, var.Orientacion, alt_ang, azimuth)
        # print('Radiacion directa sobre la superficie inclinada (W/m^2)')
        # print(Siy)

        theta = self.calcangulodeincidencia(delta, var.Latitud, var.Inclinacion, omega, var.Orientacion)
        # print('Angulo de incidencia')
        # print(theta)

        thetaz = self.calcangulocenital(var.Latitud, delta, omega)
        # print('Angulo cenital')
        # print(thetaz)

        ap = self.calcangulodeperfil(alt_ang, azimuth, var.Orientacion)
        # print('Angulo de perfil')
        # print(ap)

        omega_s = self.calcangulohorarioatardecer(var.Latitud, delta)
        # print('Angulo horario en puesta de sol')
        # print(omega_s)

        [amanecer, atardecer] = self.calcamaneceratardecer(velrotacion, omega_s)
        # print('Amanecer')
        # print(amanecer)
        # print('Atardecer')
        # print(atardecer)

        Rb = self.calcrazonderadiaciondehazensuperficieinclinada(theta, thetaz)
        # print('Razon haz sup. inclinada a plana')
        # print(Rb)

        # Sh = self.calcradiaciondirectahorizontal(Rb, Siy)
        # print('Radiacion directa horizontal')
        # print(Sh)

        Taub = self.calctransmitanciaatmosfeficapararadiaciondirecta(var.Altitud, thetaz)
        # print('Transmitacia atmosferica rad. directa')
        # print(Taub)

        Gcnb = self.calcradiaciondirectanormal(Gon, Taub)
        # print('Radiacion directa normal (W/m^2)')
        # print(Gcnb)

        Gcb = self.calcradiaciondirectahorizontal(Gcnb, thetaz)
        # print('Radiacion directa horizontal (W/m^2)')
        # print(Gcb)

        Gd = self.calcradiaciondifusahorizontal(Gon, thetaz, Taub)
        # print('Radiacion difusa horizontal (W/m^2)')
        # print(Gd)

        var.Dh = Gd
        #var.Dh = 0

        var.Ghmodelo = Gcb + Gd
        # print('Radiacion global modelo (W/m^2)')
        # print(Gh_calculadamodelo)

        Rgpiranometro = self.calcrelacionderadiacionglobal(Rb, var.Inclinacion, Gcb, var.Gh, var.Albedo)
        Rgmodelo = self.calcrelacionderadiacionglobal(Rb, var.Inclinacion, Gcb, var.Gh, var.Albedo)
        # print('Relacion radiacion global')
        # print(Rg)

        Giy = self.calcradiacioninclinada(Rgpiranometro, var.Gh)
        Giymodelo = self.calcradiacioninclinada(Rgmodelo, var.Ghmodelo)
        # print('Radiacion global inclinada (W/m^2)')
        # print(Giy)

        var.G = Giy
        var.Giymodelo = Giymodelo

        self.escribirrespuesta()

def main():
    var.currentTime = []
    var.currentGhmeas = []
    var.currentGiymeas = []
    var.currentGhmodel = []
    var.currentGiymodel = []

    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()