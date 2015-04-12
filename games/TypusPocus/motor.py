# -*- coding: utf-8 -*-

from __future__ import division
import random, time
import cosas
import phrases

DEBUG=0

PALABRAS = "Nuestro objetivo es nuclear a los usuarios de Python, de manera de centralizar la comunicacion a nivel nacional. Pretendemos llegar a usuarios y empresas, promover el uso de Python, intercambiar informacion, compartir experiencias y en general, ser el marco de referencia local en el uso y difusion de esta tecnologia.".split()

class Estados:
    (VIRGEN, OK_DEUNA, OK_CORRG, MAL) = range(4)

class Eventos:
    (VIRGEN, OK_DEUNA, OK_CORRG, MAL, PALOK, PALMAL, INACT5, INACT10) = range(8)
    descrip = {PALOK:   "Se escribio una palabra completamente correcta",
               PALMAL:  "Se escribio una palabra completamente mal",
               INACT5:  "Hace 5 segundos que no se escribe nada",
               INACT10: "Hace 10 segundos que no se escribe nada",
              }
    

class MainMotor(object):
    '''Clase que maneja el motor del juego.

    Se lo arranca con el start().
    Cuando el usr presiona una tecla, hitLetra(), cuando hace backspace, hitBackspace()
    '''

    voluntario = None
    voluntario_error = None
    step_size = 0.1
    fast = 1.5
    slow = 0.75
    good = 1.00
    bad = 0.70
    inicio_segundos = 10
    max_calor_inicial = 0.3
    max_with_error = 0.9
    precision_requerida = 0.8
    tiempo_por_caracter = 0.5
    changui = 3
    preferencia_precision = 0.5
    cantidad_palabras = 20
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
        # Elegimos el objeto para voluntario en funcion de lo que dice levels.py
        # sino tenemos objeto, no me queda otra que ir al azar
        if self.voluntario is None:
            if hasattr(self, "objeto") and hasattr(cosas, self.objeto):
                self.voluntario = getattr(cosas, self.objeto)
            else:
                self.voluntario = random.choice(cosas.all)
        self.voluntario_error = self.voluntario
        while self.voluntario == self.voluntario_error:
            self.voluntario_error = random.choice(cosas.all)
        if "hechizo" in kwargs:
            (self.hechizo, self.indpals) = self._armaHechizo(0, self.hechizo)
        else:
            (self.hechizo, self.indpals) = self._armaHechizo(self.cantidad_palabras)
        self.largohech = len(self.hechizo)
        self.cursor = 0
        self.cant_bs = 0
        self.startTime = None
        self.tiempoJuego = self._getTiempoJuego()
        # calculamos el puntaje maximo con un estado 100% ok, y luego reseteamos
        self.score = 0
        self.estado = [Estados.VIRGEN] * self.largohech
        self.calor = 0
        self.tiempoUltTecla = 0
        self.dirty = True

    def _armaHechizo(self, cant=0, spell=None):
        '''Arma el hechizo y un indice que es un dict, donde la clave es la
        posicion de la ultima letra de cada palabra y el valor es una tupla
        con los dos extremos de la palabra.
        '''
        base = 0
        palabras = []
        indice = {}
        if spell is None:
            spell = phrases.Spell(cant).getPhrase()
        for pal in spell.split(" "):
            #pal = random.choice(PALABRAS)
            largo = len(pal)
            palabras.append(pal)
            indice[base+largo-1] = (base, base+largo)
            base += largo + 1
        return (" ".join(palabras), indice)
        
    def hitLetra(self, letra):
        '''Recibe la letra que apretó el usuario y devuelve...

        - Si esa letra estuvo bien o mal
        - El estado completo de la frase
        - El puntaje total
        - El calor del público
        - Una lista de eventos
        '''
        self.dirty = True
        if self.startTime is None:
            raise ValueError("Todavia no se hizo el start de la sesion!")
        if self.cursor > self.largohech:
            return (None, self.estado, None, None, None)

#        if DEBUG: print "Estado viejo", self.estado
        if self.hechizo[self.cursor] == letra:
            if self.estado[self.cursor] in (Estados.VIRGEN, Estados.OK_DEUNA):
                res = Estados.OK_DEUNA
            else:
                res = Estados.OK_CORRG
        else:
            res = Estados.MAL
        self.estado[self.cursor] = res
#        if DEBUG: print "Estado nuevo", self.estado

        # evento? nos fijamos si completamos una palabra
        evento = None
        if self.cursor in self.indpals:
            (ini, fin) = self.indpals[self.cursor]
            if self.estado[ini:fin] == [Estados.OK_DEUNA]*(fin-ini):
                evento = Eventos.PALOK
            if self.estado[ini:fin] == [Estados.MAL]*(fin-ini):
                evento = Eventos.PALMAL
        else:
            evento = self.estado[self.cursor]

        # actualizamos las variables
        
        self.tiempoUltTecla = time.time()
        self.cursor += 1
        return (res, evento)

    def hitBackspace(self):
        '''El usuario apretó el backspace.'''
        if self.cursor > 0:
            self.cursor -= 1
        self.cant_bs = +1
        self.tiempoUltTecla = time.time()
        return


    def start(self):
        self.last_update = self.startTime = time.time()
        return

    def tick(self):
        if self.startTime is None:
            return
        
        # actualizamos el calor del publico
        if time.time() - self.last_update > 1:
            self._calcCalor()
            self.last_update = time.time()

        # evento? vemos si hace rato que no tocamos una tecla
        inactivo = time.time() - self.tiempoUltTecla
        if inactivo > 10:
            return Eventos.INACT10
        if inactivo > 5:
            return Eventos.INACT5
        return

    def getTimeLeft(self):
        '''Antes del start, devuelve el tiempo total, después devuelve
        el que falta para terminar.
        '''
        if self.startTime is None:
            return self.tiempoJuego
        falta = self.startTime + self.tiempoJuego - time.time()
        return falta

    def _getTiempoJuego(self):
        '''Devuelve el tiempo que tiene el usuario para completar el hechizo.'''
        # la hacemos fácil, un segundo por letra
        return self.largohech*self.tiempo_por_caracter + self.changui

    def tuvoExito(self):
        acertados = 0
        for st in self.estado:
            if st == Estados.OK_DEUNA or st == Estados.OK_CORRG:
                acertados += 1
        porcentaje = float(acertados)/len(self.estado)
        #if DEBUG: print acertados, "/", len(self.estado)
        return porcentaje >= self.precision_requerida

    def _calcCalor(self):
        '''calcula el calor del publico y lo pone en self.calor
        se debe ejecutar una vez por segundo
        tambien updetea el score
        Es un float, entre -1 (super enojado) y 1 (super alegre).
        0 es neutro.
        
        ver: https://opensvn.csie.org/traccgi/PyAr/wiki/FuncionCalor
        '''
        
        #calculos previos
        acertados = 0.0
        errados = 0.0
        for st in self.estado:
            if st == Estados.OK_DEUNA or st == Estados.OK_CORRG:
                acertados += 1
            elif st == Estados.MAL:
                errados += 1
        # calculamos el calor por velocidad
        tiempo_transcurrido = self._getTiempoJuego() - self.getTimeLeft()
        tiempo_estimado = (acertados+errados)*self.tiempo_por_caracter
        
        
        ratio_velocidad = tiempo_estimado/tiempo_transcurrido
        
        calor_velocidad = (ratio_velocidad-self.slow)*2.0/(self.fast-self.slow)-1
        
        if ratio_velocidad < self.slow:
            calor_velocidad = -1.0
        if ratio_velocidad > self.fast:
            calor_velocidad = 1.0
            
        # calculamos el calor por precision
        
        
        if (acertados+errados) == 0:
            ratio_precision = self.bad
        else:
            ratio_precision = acertados/(acertados+errados)
        
        calor_precision = (ratio_precision-self.bad)*2.0/(self.good-self.bad)-1
        if ratio_precision < self.bad:
            calor_precision = -1.0
        if ratio_precision > self.good:
            calor_precision = 1.0
            
        # mezlcamos ambos
        delta_calor = (
                 calor_precision*self.preferencia_precision +
                 calor_velocidad*(1-self.preferencia_precision)
                 )
        
        # filtros pre delta
        if time.time()-self.tiempoUltTecla > 2:
            delta_calor = -1
            
        # aplicamos el delta
        calor = self.calor + delta_calor*self.step_size
        
        # filtros post delta
        if time.time()-self.tiempoUltTecla > 5:
            calor = min(calor, -0.5)
            
        if calor > 1:
            calor = 1
        if calor < -1:
            calor = -1
            
        # corregimos el calor y el score
        self.calor = calor
        self.score += calor
        if self.score < 0:
            self.score = 0.0
        if DEBUG: print "calor: %.2f\t calp: %.2f\t calv: %.2f\t rpre: %.2f\t rvel: %.2f\t"%(calor, calor_precision, calor_velocidad, ratio_precision, ratio_velocidad)
        return calor

    def getRate(self):
        if self.dirty:
            acertados = 0.0
            errados = 0.0
            for st in self.estado:
                if st == Estados.OK_DEUNA or st == Estados.OK_CORRG:
                    acertados += 1
                elif st == Estados.MAL:
                    errados += 1
                    
            if (acertados+errados) == 0:
                ratio_precision = 1
            else:
                ratio_precision = acertados/(acertados+errados)
            self._rate = ratio_precision
            self.dirty = False
            
        return self._rate
