########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################
#######################                                                #################################
####################### AUTHOR: SALVADOR JESÚS MEGÍAS ANDREU           #################################
####################### EMAIL: salvadorjmegias@gmail.com               #################################
####################### UNIVERSITY EMAIL: salvadorjesus@correo.ugr.es  #################################
#######################                                                #################################
########################################################################################################
########################################################################################################
########################################################################################################
########################################################################################################


# Librerías o Modulos necesarios a importar
import pyvisa as visa
import numpy as np
from struct import unpack
import pylab
import time
from matplotlib import pyplot as plot


############################################################################################
##############                 CLASS AGILENT_N9020A     #####################################
##############        SPECTRUM ANALYZER CONTROLLED     #####################################
##############  BY ETHERNET CONTROL                    #####################################
############################################################################################

class Agilent_MXA_N9020A:
    
    # La medida con la que vamos a trabajar van a ser los MHz
    medida ='MHZ'

############################################################################################
############## CONSTRUCTOR #################################################################
############################################################################################
    
    # Cuando creemos un objeto de la clase, ejecutaremos el setup() conectándose automáticamente a la máquina
    # mediante conexión TCP
    
    def __init__(self):
        
        self.scope= self.setup()
        #sel.nPoints = int(self.scope.query('SWE:POIN?'))
        
############################################################################################
############## IDENTITY & SETUP ############################################################
############################################################################################
    
    # Muestra la información propia ofrecida por la máquina
    
    def identity(self):
        info= self.scope.query('*IDN?')
        info = info.split(",")
        print("Fabricante: ",info[0])
        print("Modelo: ",info[1])
        print("Número de serie: ",info[2])
        print("Firmware: ",info[3])
    
    # Establece una conexión TCP con la máquina mediante su IP devolviendo el objeto conectado para poder manejarlo
    
    def setup(self):
        # 192.168.1.200 IP AGILENT MACHINE
        rm = visa.ResourceManager('@py') # Calling PyVisaPy library
        scope = rm.open_resource('TCPIP::192.168.1.200::INSTR') # Connecting via LAN 
        return scope


    # Finaliza la conexión con la máquina
    def disconnect(self):
        self.scope.close()
    
################################################################################################################################
# AL CONTRARIO QUE LA MÁQUINA ANRITSU, AGILENT SOLO TIENE MODO SPECTRUM ANALYZER, POR LO QUE NO ES NECESARIO ACTIVAR NINGÚN MODO
# EL MODO SPECTRUM ANALYZER VIENE POR DEFECTO
################################################################################################################################

# Activa el modo Spectrum en la máquina (por si acaso)
    
    def setSpectrum(self):
        self.scope.write('INST SA')
        self.instAgilent = 'SA'
        #print("Ha seleccionado el Spectrum Analyzer")


    # Función con la que recogemos todos los datos de la máquina una vez nos conectamos a esta (para tener los datos y no tener que reescribirlos si no es necesario)
    # Dejamos la máquina finalmente en el modo en el que estaba cuando nos conectamos, no modificando así nada
    def getInitialParamsAgilent(self):
        
        self.instAgilent= str(self.scope.query('INST?'))

        # Seleccionamos el spectrum para poder recoger los datos del spectrum
        self.setSpectrum()
        self.inicialFreq= float(self.scope.query('FREQ:START?'))/1e6
        self.finalFreq= float(self.scope.query('FREQ:STOP?'))/1e6
        self.centralFreq= float(self.scope.query('FREQ:CENT?'))/1e6
        self.referenceLevel = float(self.scope.query('DISP:WIND:TRAC:Y:RLEV?'))
        self.nPoints = int(self.scope.query('SWE:POIN?'))
        self.span = float(self.scope.query('FREQ:SPAN?'))/1e6
        
        self.scope.write('INST '+ self.instAgilent)

############################################################################################
######### FUNCTIONS FOR SPECTRUM ANALYZER ##################################################
############################################################################################

    # Muestra todos los parámetros del Espectro en ese momento 
    
    def getParamsSpectrum(self):
        print("Frecuencia central: ",self.centralFreq ,"MHz") # Muestra la frecuencia central
        print("Frecuencia inicial: ",self.inicialFreq,"MHz") # Muestra la frecuencia inicial
        print("Frecuencia final: ",self.finalFreq,"MHz") # Muestra la frecuencia final
        print("Nivel de referencia: ",self.referenceLevel,"dBm") # Muestra el nivel de referencia
    
    # Modifica todos los parámetros del Spectrum Analyzer (la medida de las frecuencias está en MHz)
    
    def setParamsSpectrum(self,inicialFreq , finalFreq , referenceLevel):
        # Guarda todos los datos en variables del objeto de la clase
        self.inicialFreq = float(inicialFreq)
        self.finalFreq = float(finalFreq)
        self.referenceLevel = float(referenceLevel)
        self.centralFreq = (self.finalFreq + self.inicialFreq)/2.0
        
        self.scope.write('FREQ:START '+ str(inicialFreq) + self.medida) # Modifica la frecuencia inicial
        self.scope.write('FREQ:STOP '+ str(finalFreq) + self.medida) # Modifica la frecuencia final
        self.scope.write('FREQ:CENT '+ str(self.centralFreq)+ self.medida) # Modifica la frecuencia central
        self.scope.write('DISP:WIND:TRAC:Y:RLEV '+ str(referenceLevel)) # Modifica el nivel de referencia
        # Se define el número de puntos observables y medibles al valor que tenga la máquina en ese momento (por defecto son 10001)
        self.nPoints = int(self.scope.query('SWE:POIN?'))
    
    

    # Modifica todos los parámetros del Spectrum Analyzer mediante el uso de span (la medida de las frecuencias está en MHz)
    
    def setParamsSpectrumSpan(self, centralFreq , span , referenceLevel):
            self.setCentralFreqMHz(centralFreq) # Modifica la frecuencia central y su atributo de la clase
            self.setSpanMHz(span) # llama a la función modificando el valor de span inicialFreq y finalFreq y los atributos de la clase
            self.setReferenceLevelDBM(referenceLevel) # llama a la función modificando el valor de referencelevel y el atributo de la clase
            # Se define el número de puntos observables y medibles al valor que tenga la máquina en ese momento (por defecto son 10001)
            self.nPoints = int(self.scope.query('SWE:POIN?'))
            
    
        
    # Modifica el valor del span, inicialFreq y finalFreq y aparte los atributos de la clase correspondientes a la frecuencia inicial y final y el span
    # (Hace falta haber definido la frecuencia central)
    
    def setSpanMHz(self, span):
        self.span = float(span)
        mitad = self.span / 2.0
        self.scope.write('FREQ:SPAN '+ str(span)+ self.medida)
        
        self.inicialFreq = self.centralFreq - mitad
        self.scope.write('FREQ:START '+ str(self.inicialFreq) + self.medida)
        self.finalFreq = self.centralFreq + mitad
        self.scope.write('FREQ:STOP '+ str(self.finalFreq) + self.medida)
    
    # Muestra el Span en ese momento
    
    def getSpanMHz(self):
        print("Span: ", self.span , " MHz")
        
    # Modifica el valor de la frecuencia central y el atributo del objeto de la clase correspondiente
    
    def setCentralFreqMHz(self,centralFreq):
        self.centralFreq = float(centralFreq)
        self.scope.write('FREQ:CENT '+ str(centralFreq)+ self.medida)
    
    # Muestra la frecuencia central en ese momento
    
    def getCentralFreqMHz(self):
        print("Frecuencia central: ",self.centralFreq," MHz")
    
    # Modifica la frecuencia incial y el atributo del objeto de la clase correspondiente
    
    def setInicialFreqMHz(self,inicialFreq):
        self.inicialFreq = float(inicialFreq)
        self.scope.write('FREQ:START '+ str(inicialFreq) + self.medida)
        self.centralFreq = (self.inicialFreq + self.finalFreq)/2.0
    
    # Muestra la frecuencia inicial en ese momento
    
    def getInicialFreqMHz(self):
        print("Frecuencia inicial: ",self.inicialFreq," MHz")
    
    # Modifica la frecuencia final y el atributo del objeto de la clase correspondiente
    
    def setFinalFreqMHz(self,finalFreq):
        self.finalFreq = float(finalFreq)
        self.scope.write('FREQ:STOP '+ str(finalFreq) + self.medida)
        self.centralFreq = (self.inicialFreq + self.finalFreq)/2.0
    
    # Muestra la frecuencia final en ese momento
    
    def getFinalFreqMHz(self):
        print("Frecuencia final: ",self.finalFreq," MHz")
    
    # Modifica el nivel de referencia y el atributo del objeto de la clase correspondiente
    
    def setReferenceLevelDBM(self,referenceLevel):
        self.referenceLevel = float(referenceLevel)
        self.scope.write('DISP:WIND:TRAC:Y:RLEV '+ str(referenceLevel))
    
    # Muestra el nivel de referencia en ese momento
    
    def getReferenceLevelDBM(self):
        print("Nivel de referencia: ",self.referenceLevel," dBm")
    
    # Muestra y devuelve el número de puntos observables y medibles en ese momento
    
    def getNumPoints(self):
        puntos = int(self.scope.query('SWE:POIN?'))
        #print("Número de puntos: ",puntos)
        return puntos
    
    # Modifica el número de puntos observables y medibles y el atributo del objeto de la clase correspondiente
    
    def setNumPoints(self,npoints):
        self.nPoints = int(npoints)
        self.scope.write('SWE:POIN '+ str(npoints))
    
    # Muestra y devuelve la frecuencia donde se encuentra la potencia máquina y la potencia máxima
    
    def getMaxFreqPower(self):
        self.scope.write('CALC:MARK:MAX')
        #print("Frecuencia donde se encuentra la potencia máxima: ",self.scope.query('CALC:MARK:X?')," MHz")
        #print("Potencia máxima: ",self.scope.query('CALC:MARK:Y?')," dBm")
        self.maxfreq = float(self.scope.query('CALC:MARK:X?'))/1e6
        power = float(self.scope.query('CALC:MARK:Y?'))
        return power
    
    # Función que devuelve la potencia referente a una frecuencia dada
    
    def getPowerDBM(self, freq):
        self.scope.write('CALC:MARK:X '+ str(freq)+ self.medida) 
        print("Potencia asociada a la frecuencia dada: ",self.scope.query('CALC:MARK:Y?'), " dBm")

############################################################################################
############## PLOT INFORMATION  ###########################################################
############################################################################################

    # Función que guarda una imagen png y la muestra en pantalla de la señal del Spectrum completa en ese momento

    def plotInfoAgilent(self):
        
        puntos = self.getNumPoints() # guardamos el número de puntos a representar con plot
        
        self.scope.write('FORM ASC') # Pide a la máquina que lo que se le pide lo devuelva en formato ASCII
        datos = self.scope.query('TRAC? TRACE1') # Pide a la máquina los datos del Spectrum (los datos son las potencias de los 10001 puntos observables y medibles)
        datosManipulables = datos.split(",") # separa todos los datos separados por comas y los guarda en una lista
        datosManipulables = [float(i) for i in datosManipulables] # transformo los datos de string a float para poder trabajar con ellos
        

        self.datosCapturados = datosManipulables.copy() # Para poder hacer uso de ellos en caso de querer buscar máximos, mínimos...
        
        freq = self.finalFreq - self.inicialFreq # definimos la amplitud del intervalo de frecuencias a representar
        pointWidth = freq / float(puntos) # defino la anchura que debe ocupar cada punto en la imagen (para saber donde colocar cada frecuencia en la imagen)
        
        
        # Creo una lista de todas las frecuencias a representar
        frequencies = []
        count = 0
        while len(frequencies) != puntos:
            frequencies.append(self.inicialFreq+(pointWidth*count))
            count+=1
        
        plot.clf()

        # Label for x-axis
        plot.xlabel("Frequency (MHz)")
 
        # Label for y-axis
        plot.ylabel("Power (dBm)")
 
        # title of the plot
        plot.title("Output of Spectrum Analyzer")

        # Add grid lines
        plot.grid()
        
        #Genero la imagen con las frecuencias calculadas y las potencias ofrecidas por la máquina
        
        plot.plot(frequencies,datosManipulables) 
        plot.savefig('./images/graphAgilent.png') # Dirección relativa donde se quiere que se guarde la imagen creada
        plot.show()