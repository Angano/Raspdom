import asyncio
import random
import time
import smbus
import math
from time import sleep
from config import db
try:
    import RPi.GPIO as gpio
    import RPi.GPIO as GPIO
    # make sure to install python-smbus using below command
    # sudo apt-get install python-smbus


except:
    pass
import json

class Common():

    # Identification appareil
    id_appareil = 0
    id_appareil_model = 0
    infos_entre = ['A définir']
    infos_sortie = ['A définir']
    valeur = 0
    appareils = []
    unite = ''
    valeur_cumule = 0
    valeur_courante = 0
    actived = False
    consigne = 0
    init = False

    def __init__(self, composant=None):
        self.composant = composant
        try:
            if composant.order_gpio == None:
                gpios = []
                for i in range(self.composant.nbre_gpio):
                    gpios.append('')
            else:
                gpios = json.loads(self.composant.order_gpio)

            for i in range(self.entre):
                data = 'I'+str(i)
                setattr(self,data,gpios[i])
            for i in range(self.sortie):
                data = 'A' + str(i)
                setattr(self,data,gpios[i+self.entre])
        except Exception as e:
            print(e)

        self.appareils = composant.appareils


    async def toto(self):
        compteur = 0
        while True:
            await asyncio.sleep(1)
            if True:
                #print('L60_Composants.py',self.valeur_cumule, self.consigne,'\n')

                self.valeur = random.randint(1,40)
                self.valeur_cumule = self.valeur_cumule + self.valeur
                self.valeur_courante = self.valeur
            else:
                self.valeur_courante = 0

    def gpio_on(self, Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]

            gpio.output(int(Gpio), gpio.LOW)
        except:
            print('gpio.out({}, gpio.LOW)'.format(Gpio), 'error')

        # mise à 0 d'un gpio
    def gpio_off(self, Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]
            gpio.output(int(Gpio), gpio.HIGH)
        except:
            print('gpio.out({}, gpio.HIGH)'.format(Gpio), 'error')
            pass

    def gpio_read(self,Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]
            return gpio.input(int(Gpio))
        except:
            print('gpio.input({}'.format(Gpio), 'error')
            return None
    def IT(channel):
        print('le bouton a été enfoncé!')
        print('sur le GPIO %s' % channel)
    def addEcouteur(self,Gpio):
        if self.ecouteur:
            try:
                Gpio = (Gpio.split('_'))[1]
                print(Gpio)

                #gpio.output(int(Gpio), gpio.LOW)
                gpio.add_event_detect(Gpio, gpio.FALLING, callback=self.IT(Gpio), bouncetime=200)
            except Exception as e:
                print(e)



            pass


    def test(self,instance):

        # instance => datas ( appareil) issue de la bdd
        # self => datas issue de Composants.py
        print(self,instance,'test')

        self.appareils = instance.appareils
        for data in self.appareils:
            print(globals()[data.categorieappareil+'_'+str(data.id)])
        #print(self.appareils)



class HCSR04(Common):
    valeur = 0
    entre = 1
    sortie = 1
    gpio = True
    categoriecomposant = 'Capteur de distance'
    unite = 'cm'

    infos_entre = ['TRIG']
    infos_sortie = ['ECHO']
    modele = "oooo"

    def label(self):
        "HC-SR04"
        pass
    """async def toto(self):
        compteur = 0
        while True:
            await asyncio.sleep(0.8)
            self.valeur = 3
            compteur = random.randint(0,10)"""

    async def toto(self):
        """step = time.time()
        while True:
            time.sleep(0.25)

            try:
                repeat = 10


                distance = 0
                debutImpulsion = time.time()
                finImpulsion = time.time()

                for x in range(int(repeat)):  # On prend la mesure "repet" fois
                    time.sleep(0.05)
                    self.gpio_on(self.A0)
                    step = time.time()

                    #self.gpio_on('Gpio_13')

                    time.sleep(0.00001)
                    self.gpio_off(self.A0)

                    #self.gpio_off('Gpio_13')

                    while self.gpio_read(self.I0) == 0:  ## Emission de l'ultrason
                        debutImpulsion = time.time()

                    while self.gpio_read(self.I0) == 1:  ## Retour de l'Echo
                        finImpulsion = time.time()


                    distance = distance + (finImpulsion - debutImpulsion) * 340 * 100 / 2  ## Vitesse du son = 340 m/s
                    try:
                        print(distance/x)
                    except:
                        pass

                self.valeur_cumule = self.valeur_cumule + self.valeur
                self.valeur_courante = round(distance / repeat, 1)

                print(round(distance / repeat, 1))
            except Exception as e:
                print(e, ' ### bug hcsr04 ### ')
                return 'bug hcsr04'"""
        # !/usr/bin/python

        import time

        GPIO.setmode(GPIO.BCM)



        Trig = 6  # Entree Trig du HC-SR04 branchee au GPIO 23
        Echo = 13  # Sortie Echo du HC-SR04 branchee au GPIO 24

        GPIO.setup(Trig, GPIO.OUT)
        GPIO.setup(Echo, GPIO.IN)

        GPIO.output(Trig, False)

        # repet = input("Entrez un nombre de repetitions de mesure : ")
        repet = 5
        while True:
            await asyncio.sleep(1)
            for x in range(int(repet)):  # On prend la mesure "repet" fois
                await asyncio.sleep(0.05)  # On la prend toute les 1 seconde
                GPIO.output(Trig, True)
                await asyncio.sleep(0.00001)
                GPIO.output(Trig, False)

                while GPIO.input(Echo) == 0:  ## Emission de l'ultrason
                    debutImpulsion = time.time()

                while GPIO.input(Echo) == 1:  ## Retour de l'Echo
                    finImpulsion = time.time()

            distance = round((finImpulsion - debutImpulsion) * 340 * 100 / 2, 1)  ## Vitesse du son = 340 m/s
            self.valeur_courante = round(distance,1)

            self.valeur_cumule = self.valeur_cumule + self.valeur
            print("La distance est de : ", distance, " cm")

        GPIO.cleanup()


class BMP180(Common):
    valeur = 0
    entre = 0
    sortie = 0
    DEVICE = 0x77  # Default device I2C address
    gpio = False
    categoriecomposant = 'Capteur de pression'

    # bus = smbus.SMBus(0)  # Rev 1 Pi uses 0


    def label(self):
        "BMP-180"
        pass

    def getDatas(self):
        """try:
            #bmp = bmp180(0x77)
            print(bmp.get_temp())
            print(bmp.get_pressure())
            print(bmp.get_altitude())
        except Exception as e:
            print(e)"""

        # Global variables
        address = None
        try:
            bus = smbus.SMBus(1)
        except Exception as e:
            print(e)

        mode = 1  # TODO: Add a way to change the mode

        # BMP180 registers
        CONTROL_REG = 0xF4
        DATA_REG = 0xF6

        # Calibration data registers
        CAL_AC1_REG = 0xAA
        CAL_AC2_REG = 0xAC
        CAL_AC3_REG = 0xAE
        CAL_AC4_REG = 0xB0
        CAL_AC5_REG = 0xB2
        CAL_AC6_REG = 0xB4
        CAL_B1_REG = 0xB6
        CAL_B2_REG = 0xB8
        CAL_MB_REG = 0xBA
        CAL_MC_REG = 0xBC
        CAL_MD_REG = 0xBE

        # Calibration data variables
        calAC1 = 0
        calAC2 = 0
        calAC3 = 0
        calAC4 = 0
        calAC5 = 0
        calAC6 = 0
        calB1 = 0
        calB2 = 0
        calMB = 0
        calMC = 0
        calMD = 0

        def __init__(self, address):
            self.address = address

            # Get the calibration data from the BMP180
            self.read_calibration_data()

        # I2C methods

        def read_signed_16_bit(self, register):
            """Reads a signed 16-bit value.

            register -- the register to read from.
            Returns the read value.
            """
            msb = self.bus.read_byte_data(self.address, register)
            lsb = self.bus.read_byte_data(self.address, register + 1)

            if msb > 127:
                msb -= 256

            return (msb << 8) + lsb

        def read_unsigned_16_bit(self, register):
            """Reads an unsigned 16-bit value.

            Reads the given register and the following, and combines them as an
            unsigned 16-bit value.
            register -- the register to read from.
            Returns the read value.
            """
            msb = self.bus.read_byte_data(self.address, register)
            lsb = self.bus.read_byte_data(self.address, register + 1)

            return (msb << 8) + lsb

        # BMP180 interaction methods

        def read_calibration_data(self):
            """Reads and stores the raw calibration data."""
            self.calAC1 = self.read_signed_16_bit(self.CAL_AC1_REG)
            self.calAC2 = self.read_signed_16_bit(self.CAL_AC2_REG)
            self.calAC3 = self.read_signed_16_bit(self.CAL_AC3_REG)
            self.calAC4 = self.read_unsigned_16_bit(self.CAL_AC4_REG)
            self.calAC5 = self.read_unsigned_16_bit(self.CAL_AC5_REG)
            self.calAC6 = self.read_unsigned_16_bit(self.CAL_AC6_REG)
            self.calB1 = self.read_signed_16_bit(self.CAL_B1_REG)
            self.calB2 = self.read_signed_16_bit(self.CAL_B2_REG)
            self.calMB = self.read_signed_16_bit(self.CAL_MB_REG)
            self.calMC = self.read_signed_16_bit(self.CAL_MC_REG)
            self.calMD = self.read_signed_16_bit(self.CAL_MD_REG)

        def get_raw_temp(self):
            """Reads and returns the raw temperature data."""
            # Write 0x2E to CONTROL_REG to start the measurement
            self.bus.write_byte_data(self.address, self.CONTROL_REG, 0x2E)

            # Wait 4,5 ms
            sleep(0.0045)

            # Read the raw data from the DATA_REG, 0xF6
            raw_data = self.read_unsigned_16_bit(self.DATA_REG)

            # Return the raw data
            return raw_data

        def get_raw_pressure(self):
            """Reads and returns the raw pressure data."""
            # Write appropriate data to sensor to start the measurement
            self.bus.write_byte_data(self.address, self.CONTROL_REG, 0x34 + (self.mode << 6))

            # Sleep for 8 ms.
            # TODO: Way to use the correct wait time for the current mode
            sleep(0.008)

            MSB = self.bus.read_byte_data(self.address, self.DATA_REG)
            LSB = self.bus.read_byte_data(self.address, self.DATA_REG + 1)
            XLSB = self.bus.read_byte_data(self.address, self.DATA_REG + 2)

            raw_data = ((MSB << 16) + (LSB << 8) + XLSB) >> (8 - self.mode)

            return raw_data

        def get_temp(self):
            """Reads the raw temperature and calculates the actual temperature.

            The calculations used to get the actual temperature are from the BMP-180
            datasheet.
            Returns the actual temperature in degrees Celcius.
            """
            UT = self.get_raw_temp()

            X1 = 0
            X2 = 0
            B5 = 0
            actual_temp = 0.0

            X1 = ((UT - self.calAC6) * self.calAC5) / math.pow(2, 15)
            X2 = (self.calMC * math.pow(2, 11)) / (X1 + self.calMD)
            B5 = X1 + X2
            actual_temp = ((B5 + 8) / math.pow(2, 4)) / 10

            return actual_temp

        def get_pressure(self):
            """Reads and calculates the actual pressure.

            Returns the actual pressure in Pascal.
            """
            UP = self.get_raw_pressure()
            UT = self.get_raw_temp()
            B3 = 0
            B4 = 0
            B5 = 0
            B6 = 0
            B7 = 0
            X1 = 0
            X2 = 0
            X3 = 0
            pressure = 0

            # These calculations are from the BMP180 datasheet, page 15

            # Not sure if these calculations should be here, maybe they could be
            # removed?
            X1 = ((UT - self.calAC6) * self.calAC5) / math.pow(2, 15)
            X2 = (self.calMC * math.pow(2, 11)) / (X1 + self.calMD)
            B5 = X1 + X2

            # Todo: change math.pow cals to constants
            B6 = B5 - 4000
            X1 = (self.calB2 * (B6 * B6 / math.pow(2, 12))) / math.pow(2, 11)
            X2 = self.calAC2 * B6 / math.pow(2, 11)
            X3 = X1 + X2
            B3 = (((self.calAC1 * 4 + int(X3)) << self.mode) + 2) / 4
            X1 = self.calAC3 * B6 / math.pow(2, 13)
            X2 = (self.calB1 * (B6 * B6 / math.pow(2, 12))) / math.pow(2, 16)
            X3 = ((X1 + X2) + 2) / math.pow(2, 2)
            B4 = self.calAC4 * (X3 + 32768) / math.pow(2, 15)
            B7 = (UP - B3) * (50000 >> self.mode)

            if B7 < 0x80000000:
                pressure = (B7 * 2) / B4
            else:
                pressure = (B7 / B4) * 2

            X1 = (pressure / math.pow(2, 8)) * (pressure / math.pow(2, 8))
            X1 = (X1 * 3038) / math.pow(2, 16)
            X2 = (-7357 * pressure) / math.pow(2, 16)
            pressure = pressure + (X1 + X2 + 3791) / math.pow(2, 4)

            return pressure

        def get_altitude(self, sea_level_pressure=101325):
            """Calulates the altitude.

            This method calculates the altitude using the pressure.
            This method is not reliable when the sensor is inside.
            sea_level_pressure -- the pressure at the sea level closest to you in
            Pascal.
            Returns the altitude in meters.

            !!! This method probably does not work correctly. I've tried to test
            it but at the moment I have no way of verifying the data. !!!
            """
            altitude = 0.0
            pressure = float(self.get_pressure())

            altitude = 44330.0 * (1.0 - math.pow(pressure / sea_level_pressure, 0.00019029495))

            return altitude

#pip install Adafruit_DHT
class DHT22(Common):
    valeur = 0
    entre = 1
    sortie = 0
    gpio = True
    categoriecomposant = 'Capteur d\'humite'
    unite = [{'Temp':'°C','Hygro':'%'}]

    def label(self):
        "DHT-22"
        pass

    # pip install Adafruit_DHT

    def getDatas(self):
        try:
            import Adafruit_DHT
        except Exception as e:
            print(e, "erreur import Adafruit_DHT")

        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.I0.split('_')[1])

        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('Failed to get reading. Try again!')

        return {'temperature': '{0:0.1f}'.format(temperature), 'humidite': '{0:0.1f}%'.format(humidity)}



class YFS201(Common):

    valeur = 0
    entre = 1
    sortie = 0
    gpio = True
    categoriecomposant = 'Débitmètre'
    infos_entre = ["Compteur d'impulsion"]
    doc = [' Formule de conversion: débit (en l/min) = fréquence (en Hz) / 7,5']
    unite = 'l/mn'



    def label(self):
        "YFS-201"
        pass

    """async def toto(self):
        compteur = 0
        while True:
            await asyncio.sleep(1)
            if True:
            #if self.valeur_cumule<self.consigne and self.actived:
                self.valeur = 1972 - random.randint(-25,25)
                self.valeur_cumule = self.valeur_cumule + self.valeur
                self.valeur_courante = self.valeur
            else:
                self.valeur_courante = 0"""


    def getDatas(self):
        try:
            print('hello ')

        except Exception as e:
            print(e, ' ### bug hcsr04 ### ')
            return 'bug hcsr04'

    """async def toto(self):
        compteur = 0
        while True:
            await asyncio.sleep(0.3)
            self.valeur = random.randint(0,45)"""


class Compteurs(Common):
    valeur = 0
    entre = 0
    sortie = 0
    ecouteur = True
    gpio = False
    categoriecomposant = 'Compteurs'
    infos_entre = ["Compteur d'impulsion"]
    doc = [' On compte']
    actived = False
    go = True
    end = False



    def label(self):
        "Compteur"
        pass

    def getDatas(self):
        try:
            print('L506_ Composants.py',self.valeur)

        except Exception as e:
            print(e, ' ### Compteur ### ')
            return 'Compteur'

    async def start(self):
        print('ooooopopopopp')
        self.valeur = 0
        if self.go==True:
            while self.end==False:

                await asyncio.sleep(1)
                self.valeur = self.valeur + 1
                print('L520_Composants.py',self.valeur)
                if self.valeur>25:
                    self.end=True
                    self.start = False

        return True
