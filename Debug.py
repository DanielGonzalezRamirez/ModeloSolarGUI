# Bibliotecas para operaciones matematicas, arreglos y variables aleatorias
import math


# Bibliotecas para el manejo del tiempo

# Importa el archivo de la interfaz grafica y las variables de la clase definida
def calcdiadelanio(dd,mm):
    # Calcula el dia del anio (nd) a partir del numero del mes (mm) y el dia del mes (dd)
    nd = dd + 31 * (mm - 1) # Diapositiva 22 - 1. Introduccion en la energia solar
    if mm >= 3:
        nd = nd - int(0.4 * mm + 2.3)
    return nd

def calcbeta(nd):
    # Calcula el angulo beta (beta) a partir del dia del anio (nd)
    beta_deg = (nd - 1) * (360/365) # Diapositiva 24 - 1. Introduccion en la energia solar
    beta = math.radians(beta_deg) # Conversion a radianes
    return beta

def calcdeclinacion(beta):
    # Calcula la declinacion del sol (delta) a partir del angulo beta (beta)
    delta = (0.006918 - 0.399912 * math.cos(beta) + 0.070257 * math.sin(beta) - 0.006758 * math.cos(2 * beta)
            + 0.000907 * math.sin(2 * beta) - 0.002697 * math.cos(3 * beta) + 0.00148 * math.sin(3* beta))
    # Declinacion en radianes
    # Pagina 36 - Duffie & Beckman
    return delta

def calchoras(hh,mm,ss):
    # Convierte el tiempo del formato de horas:minutos:segundos (hh:mm:ss) a horas (outhoras)
    outhoras = hh + mm / 60 + ss / 3600
    return outhoras

def calctiempouniversal(TL,c1,c2):
    # Calcula el tiempo universal (TU) a partir del tiempo legal (TL), el huso horario (c1) y la correcion de
    # tiempo de verano (c2)
    TU = TL - c1 - c2 # Diapositiva 25 - 1. Introduccion en la energia solar
    return TU

def calctiemposolarmedio(TU,Long_deg):
    # Calcula el tiempo solar medio (TSM) a partir del tiempo universal (TU) y la longitud de lugar en grados (Long_deg)
    TSM = TU - (Long_deg / 15) # Diapositiva 25 - 1. Introduccion en la energia solar
    return TSM

def calcecuaciondeltiempo(beta):
    # Calcula la ecuacion del tiempo en MINUTOS(ET) a partir del angulo beta (beta)
    ET = 229.2 * (0.000075 + 0.001868 * math.cos(beta) - 0.032077 * math.sin(beta)
                  - 0.014615 * math.cos(2 * beta) - 0.04089 * math.sin(2 * beta))
    # Diapositiva 24 - 1. Introduccion en la energia solar
    return ET

def calctiemposolarverdadero(TSM,ET):
    # Calcula el tiempo solar verdadero (TSV) a partir del tiempo solar medio (TSM) y la ecuacion
    # del tiempo (ET)
    ET_horas = ET / 60
    TSV = TSM + ET_horas # Diapositiva 24 - 1. Introduccion en la energia solar
    return TSV

def calcangulohorario(TSV):
    # Calcula el angulo horario (omega) a partir del tiempo solar verdadero (TSV)
    omega_deg = (TSV - 12) * 15 # Diapositiva 24 - 1. Introduccion en la energia solar
    omega = math.radians(omega_deg) # Conversion a radianes
    return omega

def calcaltura(delta,omega,Lat):
    # Calcula la altura angular (h) a partir de la declinacion (delta), el angulo horario (omega) y la
    # latitud en radianes (Lat)
    senodeh = math.cos(delta) * math.cos(omega) * math.cos(Lat) + math.sin(delta) * math.sin(Lat)
    h = math.asin(senodeh)
    # Diapositiva 26 - 1. Introduccion en la energia solar
    return h

def calcazimuth(h,delta,omega):
    # Calcula el azimuth (a) a partir de la altura angular (h), la declinacion (delta) y el angulo horario
    # (omega)
    senodea = (math.cos(delta) * math.sin(omega)) / math.cos(h)
    a = math.asin(senodea)
    # Diapositiva 26 - 1. Introduccion en la energia solar
    # Nota: solar azimuth angle
    # Otra formula para calcular el angulo de azimuth se presenta en la P.37 de Duffie & Beckman
    return a

def calcradiacionsolarextraterrestre(Gsc,beta):
    # Calcula la radiacion solar extraterrestre (Gon) a partir de la constante solar (Gsc) y el angulo beta (beta)
    Gon = Gsc*(1.000110 + 0.034221 * math.cos(beta) + 0.001280 * math.sin(beta) + 0.000719 * math.cos(2 * beta)
               + 0.000077 * math.sin(2 * beta))
    # Pagina 31 - Duffie & Beckman
    return Gon

def calciluminacionsolarfueradelaatmosfera(Gsc,nd):
    # Calcula la iluminacion fuera de la atmosfera (I) a partit de la constante solar (Gsc) y el dia del anio (nd)
    angulo_deg = (nd - 2.72) * (360 / 365.25)
    angulo = math.radians(angulo_deg)
    I = Gsc * (1 + 0.034 * math.cos(angulo))
    # Diapositiva 30 - 1. Introduccion en la energia solar
    return I

def calcradiaciondirecta(I,i,o,h,a):
    # Calcula la radiacion solar directa (S) a partir de la altura angular (h), el angulo de inclinacion (i), el angulo
    # de orientacion (o), el angulo de azimuth (a) y iluminacion fuera de la atmosfera (I)
    S = I*(math.sin(i) * math.cos(h) * math.cos(a - o) + math.cos(i) * math.sin(h))
    # Diapositiva 30 - 1. Introduccion en la energia solar
    return S

# def calcradiaciondirecta(Gon,i,o,h,a):
#     # Calcula la radiacion solar directa (S) a partir de la altura angular (h), el angulo de inclinacion (i), el angulo
#     # de orientacion (o), el angulo de azimuth (a) y la radiacion solar extraterreste (Gon)
#     S = Gon*(math.sin(i) * math.cos(h) * math.cos(a - o) + math.cos(i) * math.sin(h))
#     # Diapositiva 30 - 1. Introduccion en la energia solar
#     return S

def calcangulodeincidencia(delta,lat,i,omega,o):
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

def calcangulocenital(lat,delta,omega):
    # Calcula el angulo cenital (thetaz) a partir de la latitud (lat), la declinacion (delta) y el angulo horario
    # (omega)
    cosdethetaz = math.cos(lat) * math.cos(delta) * math.cos(omega) + math.sin(lat) * math.sin(delta)
    thetaz = math.acos(cosdethetaz)
    # Pagina 37 - Duffie & Beckman
    return thetaz

def calcangulodeperfil(h,a,o):
    # Calcula el angulo de perfil (ap) a partir de la altura angular (h), el angulo de azimuth (a) y la orientacion (o)
    tandeap = math.tan(h)/math.cos(a - o)
    ap = math.atan(tandeap)
    # Pagina 39 - Duffie & Beckman
    return ap

def calcangulohorarioatardecer(lat,delta):
    # Calcula el angulo horario en la puesta de sol (omega_s) a partir de la latitud (lat) y de la declinacion (delta)
    cosdeomegas = - math.tan(lat) * math.tan(delta)
    omega_s = math.acos(cosdeomegas)
    # Pagina 39 - Duffie & Beckman
    return omega_s

def calcamaneceratardecer(vrot,omega_s):
    # Calcula la hora de amanecer (aman) y atardecer (atar) a partir de la velocidad de rotacion de la tierra (vrot) y
    # el angulo horario de atardecer (omega_s)
    distanciadelmediodia = omega_s / vrot
    aman = 12 - distanciadelmediodia
    atar = 12 + distanciadelmediodia
    # Pagina 39 - Duffie & Beckman
    return aman, atar

def calcrazonderadiaciondehazensuperficieinclinada(theta,thetaz):
    # Calcula la rezon entre haz radiado en una superficie inclinada con el haz radiado a una superficie horizontal (Rb)
    # a partir del angulo de incidencia (theta) y el angulo de cenital (thetaz)
    Rb = math.cos(theta)/math.cos(thetaz)
    # Pagina 46 - Duffie & Beckman
    return Rb

def calctransmitanciaatmosfeficapararadiaciondirecta(altitud,thetaz):
    # Calcula la transmitacia atmosférica para la radiacion directa (Taub) a partir de la altitud del observador en
    # kilometros(altitud) y el angulo cenital (thetaz)
    a0_ast = 0.4237 - 0.00821 * (6 - altitud)**2
    a1_ast = 0.5055 + 0.00595 * (6.5 - altitud)**2
    k_ast = 0.2711 + 0.01858 * (2.5 - altitud)**2
    # Los factores de correccion se definen para clima tropical:
    r0 = 0.95
    r1 = 0.98
    rk = 1.02

    a0 = a0_ast * r0
    a1 = a1_ast * r1
    k = k_ast * rk

    Taub = a0 + a1 * math.exp(-(k/(math.cos(thetaz))))
    # Pagina 90 - Duffie & Beckman
    return Taub

def calcradiaciondirectanormal(Gon,Taub):
    # Calcula la radiacion directa normal (Gcnb) a partir de la radiacion solar extraterrestre (Gon) y la
    # transmitancia atmosferica para radiacion directa (Taub)
    Gcnb = Gon * Taub
    # Pagina 90 - Duffie & Beckman
    return Gcnb

def calcradiaciondirectahorizontal(Gcnb,thetaz):
    # Calcula la radiacion directa horizontal (Gcb) a partir de la radiacion directa normal (Gcnb) y el angulo
    # cenital (thetaz)
    Gcb = Gcnb * math.cos(thetaz)
    # Pagina 90 - Duffie & Beckman
    return Gcb

def calcradiaciondifusahorizontal(Gon,thetaz,Taub):
    # Calcula la radiacion difusa horizontal (Gd) [denotada en las presentaciones como Dh] a partir de la radiacion
    # solar extraterrestre (Gon), el angulo cenital (thetaz) y la transmitancia atmosferica para radiacion directa
    # (Taub)
    Taud = 0.271 - 0.294 * Taub
    Go = Gon * math.cos(thetaz)
    Gd = Taud * Go
    # Pagina 91 - Duffie & Beckman
    return Gd

def calcradicaciondifusaisotropica(Gd,i):
    # Calcula la radiacion difusa isotropica (Gdiso_iy) a partir de la radiacion difusa horizontal (Gd) y la
    # inclinacion (i)
    Gdiso_iy = Gd * (1 + math.cos(i)) / 2
    # Diapositiva 33 - 1. Introduccion en la energia solar
    return Gdiso_iy

def calcrelacionderadiacionglobal(Rb,i,Gcb,Gh,alb):
    # Calcula la relacion de radicacion solar global (Rg = G(i,y)/Gh) a partir de la relacion de radiacion solar
    # directa (Rb), la inclinacion (i), la radiacion directa horizontal (Gcb), la radiacion global horizontal (Gh) y el
    # albedo (alb).
    Rg = (Rb - (1 + math.cos(i)) / 2) * (Gcb / Gh) + (1 + math.cos(i)) / 2 + alb * (1 - math.cos(i)) / 2
    # Diapositiva 34 - 1. Introduccion en la energia solar
    return Rg

def calcradiacioninclinada(Rg,Gh):
    # Calcula radiacion inclinada (G_iy) a partir de la relacion de radicacion solar global (Rg) y la radiacion global
    # horizontal (Gh)
    Giy = Rg * Gh
    # Diapositiva 34 - 1. Introduccion en la energia solar
    return Giy

def main():
    # Nota: No se han tenido en cuenta los casos especiales de medio dia ni de amanecer/atardecer
    Gsc = 1367 # Valor de la constante solar [W/m^2]
    velrotacion_deg = 15 # Velocidad de rotacion de la tierra [deg/hora]
    velrotacion = math.radians(velrotacion_deg)

    albedo = 0.3

    dia = 12
    mes = 9

    hora = 6
    min = 30
    seg = 18

    longitud_deg = 70.08167 # bogota
    #longitud_deg = -1.44  # diapositivas
    #longitud_deg = -9.19 # milan
    #longitud_deg = 89.4 # madison, wisconsin ejemplo Duffie P.34
    longitud = math.radians(longitud_deg)
    latitud_deg = 4.60944 # bogota
    #latitud_deg = 43.6  # diapositivas
    #latitud_deg = 45.46694 # milan
    #latitud_deg = 43 # madison, winsonsin ejemplo Duffie P.37
    latitud = math.radians(latitud_deg)

    inclinacion_deg = 4.60944 # ejemplo diapositivas
    #inclinacion_deg = 43  # ejemplo diapositivas
    #inclinacion_deg = 45 # ejemplo Duffie P.37
    #inclinacion_deg = 60  # ejemplo Duffie P.39
    inclinacion = math.radians(inclinacion_deg)
    orientacion_deg = 0 # ejemplo diapositivas
    #orientacion_deg = 15  # ejemplo Duffie P.37
    #orientacion_deg = 25  # ejemplo Duffie P.39
    orientacion = math.radians(orientacion_deg)

    altitud = 2.6 # bogota en kilometros

    verano = False
    if verano:
        tverano = 1
    else:
        tverano = 0

    huso = -5 # bogota
    #huso = 1 # milan
    #huso = -6 # madison, wisconsin

    diadelanio = calcdiadelanio(dia,mes)
    print('Dia del anio')
    print(diadelanio)

    beta = calcbeta(diadelanio)
    print('Beta')
    print(beta)

    TL = calchoras(hora,min,seg)
    print('TL')
    print(TL)

    TU = calctiempouniversal(TL,huso,tverano)
    print('TU')
    print(TU)

    TSM = calctiemposolarmedio(TU, longitud_deg)
    print('TSM')
    print(TSM)

    ET = calcecuaciondeltiempo(beta)
    print('ET')
    print(ET)

    TSV = calctiemposolarverdadero(TSM, ET)
    print('TSV')
    print(TSV)

    omega = calcangulohorario(TSV)
    print('Angulo horario')
    print(omega)

    delta = calcdeclinacion(beta)
    print('Declinacion')
    print(delta)

    alt_ang = calcaltura(delta,omega,latitud)
    print('Altura angular')
    print(alt_ang)

    azimuth = calcazimuth(alt_ang,delta,omega)
    print('Azimuth')
    print(azimuth)

    Gon = calcradiacionsolarextraterrestre(Gsc,beta)
    print('Radiacion solar extraterrestre (W/m^2)')
    print(Gon)

    I = calciluminacionsolarfueradelaatmosfera(Gsc,beta)
    print('Iluminacion fuera de la atmosfera (W/m^2)')
    print(I)

    #S = calcradiaciondirecta(Gon,inclinacion,orientacion,alt_ang,azimuth)
    S = calcradiaciondirecta(I, inclinacion, orientacion, alt_ang, azimuth)
    print('Radiacion directa sobre la superficie inclinada (W/m^2)')
    print(S)

    theta = calcangulodeincidencia(delta,latitud,inclinacion,omega,orientacion)
    print('Angulo de incidencia')
    print(theta)

    thetaz = calcangulocenital(latitud,delta,omega)
    print('Angulo cenital')
    print(thetaz)

    ap = calcangulodeperfil(alt_ang,azimuth,orientacion)
    print('Angulo de perfil')
    print(ap)

    omega_s = calcangulohorarioatardecer(latitud, delta)
    print('Angulo horario en puesta de sol')
    print(omega_s)

    [amanecer,atardecer] = calcamaneceratardecer(velrotacion,omega_s)
    print('Amanecer')
    print(amanecer)
    print('Atardecer')
    print(atardecer)

    Rb = calcrazonderadiaciondehazensuperficieinclinada(theta,thetaz)
    print('Razon haz sup. inclinada a plana')
    print(Rb)

    Taub = calctransmitanciaatmosfeficapararadiaciondirecta(altitud,thetaz)
    print('Transmitacia atmosferica rad. directa')
    print(Taub)

    Gcnb = calcradiaciondirectanormal(Gon,Taub)
    print('Radiacion directa normal (W/m^2)')
    print(Gcnb)

    Gcb =calcradiaciondirectahorizontal(Gcnb,thetaz)
    print('Radiacion directa horizontal (W/m^2)')
    print(Gcb)

    Gd = calcradiaciondifusahorizontal(Gon,thetaz,Taub)
    print('Radiacion difusa horizontal (W/m^2)')
    print(Gd)

    Gh_calculadamodelo = Gcb + Gd
    print('Radiacion global modelo (W/m^2)')
    print(Gh_calculadamodelo)

    Rg = calcrelacionderadiacionglobal(Rb,inclinacion,Gcb,Gh_calculadamodelo,albedo)
    print('Relacion radiacion global')
    print(Rg)

    Giy = calcradiacioninclinada(Rg,Gh_calculadamodelo)
    print('Radiacion global inclinada (W/m^2)')
    print(Giy)

if __name__ == '__main__':  # if we're running file directly and not importing it
    main()