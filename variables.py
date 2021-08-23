import numpy as np
class variables:
    def __init__(self):
        self.Latitud_deg = None
        self.Latitud = None
        self.Longitud_deg = None
        self.Longitud = None
        self.HusoHorario = None
        self.Inclinacion_deg = None
        self.Inclinacion = None
        self.Orientacion_deg = None
        self.Orientacion = None
        self.Gh = None
        self.Albedo = None
        self.Altitud = None
        self.IsVerano = None
        self.IsRealTime = None
        self.HoraESThr = None
        self.HoraESTmin = None
        self.HoraESTsec = None
        self.FechaDia = None
        self.FechaMes = None
        self.HoraLeida = None

        self.G = None
        self.Dh = None
        self.HoraRealhr = None
        self.HoraRealmin = None
        self.HoraRealsec = None

        self.Ghmodelo = None
        self.Giymodelo = None

        self.currentTime = None
        self.currentGhmeas = None
        self.currentGiymeas = None
        self.currentGhmodel = None
        self.currentGiymodel = None

        self._static_ax = None
        self.plotX = None
        self.plotY = None

        # self.Pmax = None
        # self.Beta = None
        # self.Tpanel = None
        # self.PotPanel = None
        # self.EfiColector = None
        # self.InclOpti_deg = None
        # self.InclOpti = None
