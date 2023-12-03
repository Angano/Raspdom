import asyncio
import random
import time
import smbus
import math
from time import sleep
from config import db
from models import Status, Historiquecomposant


try:
    import RPi.GPIO as gpio
    import RPi.GPIO as GPIO
    # make sure to install python-smbus using below command
    # sudo apt-get install python-smbus


except:
    pass


try:
    import Adafruit_DHT
except Exception as e:
    print(e, "erreur import Adafruit_DHT")


import json, datetime




class Common():

    # Identification appareil
    enable = True
    id_appareil = 0
    id_appareil_model = 0
    infos_entre = ['A définir']
    infos_sortie = ['A définir']
    valeur = 0
    valeur2 = False
    unite2 = False
    appareils = []
    unite = ''
    unite2 = ''
    valeur_cumule = 0
    valeur_courante = 0
    actived = False
    consigne = 0
    init = False
    compteur = False

    mod_dev = False
    composant = None

    ## paramaetre enregistrement bdd cadencement
    cadence_record_bdd = 180 #secondes
    cadence_record_bdd_tps1 = time.time()
    valeur_moyenne_1 = 0
    valeur_moyenne_2 = 0
    compteur_passage_boucle_bdd = 0


    def toto(self):
        print('hello toto')

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
            print('error L86',e)

        #self.appareils = composant.appareils



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

    def record_historique(self):
            ## préparation pour enregistrement valeur moyenne en bdd
            if time.time() > self.cadence_record_bdd_tps1+ self.cadence_record_bdd:
                historique_composant = Historiquecomposant()
                historique_composant.histo = self.composant
                historique_composant.valeur = self.valeur_moyenne_1/self.compteur_passage_boucle_bdd
                historique_composant.unite = self.unite
                historique_composant.valeur2 = self.valeur_moyenne_2/self.compteur_passage_boucle_bdd
                historique_composant.unite2 = self.unite2
                historique_composant.record_at = datetime.datetime.now()
                db.session.commit()

                # reset parametre de départ
                self.cadence_record_bdd_tps1 = time.time()
                self.compteur_passage_boucle_bdd = 1
                self.valeur_moyenne_1 = self.composant.valeur
                self.valeur_moyenne_2 = self.composant.valeur2
                print('pass')
            else:
                self.compteur_passage_boucle_bdd = self.compteur_passage_boucle_bdd+1

                self.valeur_moyenne_1 = self.valeur_moyenne_1 + self.composant.valeur
                self.valeur_moyenne_2 = self.valeur_moyenne_2 + self.composant.valeur2

    def test(self,instance):

        # instance => datas ( appareil) issue de la bdd
        # self => datas issue de Composants.py
        print(self,instance,'test')

        self.appareils = instance.appareils

        #print(self.appareils)



class HCSR04(Common):
    valeur = 0
    entre = 1
    sortie = 1
    gpio = True
    categoriecomposant = 'Capteur de distance'
    unite = 'cm'

    infos_entre = ['ECHO']
    infos_sortie = ['TRIG']
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



        print(self.I0, self.A0)


        Trig = int(self.A0.split('_')[1]) # Output
        Echo = int(self.I0.split('_')[1]) # Input

        #GPIO.setup(Trig, GPIO.OUT)
        #GPIO.setup(Echo, GPIO.IN)

        #GPIO.output(Trig, False)
        self.gpio_off(self.A0)

        # repet = input("Entrez un nombre de repetitions de mesure : ")
        repet = 5
        while True:
            await asyncio.sleep(2,True)
            try:
                for x in range(int(repet)):  # On prend la mesure "repet" fois
                    await asyncio.sleep(0.5)  # On la prend toute les 1 seconde
                    #GPIO.output(Trig, True)
                    self.gpio_on(self.A0)
                    await asyncio.sleep(0.00001)
                    #GPIO.output(Trig, False)
                    self.gpio_off(self.A0)
                    surveillance = time.time()

                    while self.gpio_read(self.I0) == 0:  ## Emission de l'ultrason
                        debutImpulsion = time.time()

                        if debutImpulsion > surveillance+3:
                            print('surveillance aller')
                            break

                    while self.gpio_read(self.I0) == 1:  ## Retour de l'Echo
                        finImpulsion = time.time()
                        if finImpulsion>debutImpulsion+3:
                            print('surveillance retour')
                            break

                distance = round((finImpulsion - debutImpulsion) * 340 * 100 / 2, 1)  ## Vitesse du son = 340 m/s
                self.valeur_courante = round(distance,1)
                self.valeur = round(distance,1)
                self.valeur_cumule = self.valeur_cumule + self.valeur
                print("La distance est de : ", distance, " cm")
            except:
                print("error L244")

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
    valeur2 = 0
    unite = '°C'
    unite2 = '%'
    categoriecomposant = 'Capteur_humite'

    regulation_par_composant = True

    def label(self):
        "DHT-22"
        pass

    # pip install Adafruit_DHT

    async def toto(self):
      while True:

            await asyncio.sleep(25,True)
            if self.mod_dev == False:
                try:
                    humidity, temperature = Adafruit_DHT.read(Adafruit_DHT.DHT22, self.I0.split('_')[1])

                    #print({'temperature': '{0:0.1f}'.format(temperature), 'humidite': '{0:0.1f}%'.format(humidity)})
                    #data = round(humidity,5)
                    #print(data)
                    print(humidity, temperature)
                    if humidity is not None:
                        self.valeur_courante = round(humidity,3)
                        self.valeur = round(temperature, 2)
                        self.valeur2 = round(humidity,3)

                        self.valeur_cumule = round(humidity,3)
                except Exception as e:
                    print(e)
                    pass
            else:
                self.valeur_courante = random.randint(10,20)
                self.valeur = random.randint(21,40)
                self.valeur2 = random.randint(41,50)
                self.valeur_cumule = random.randint(51,70)

            self.composant.valeur = self.valeur
            self.composant.unite2 = self.unite2
            self.composant.valeur2 = self.valeur2
            self.composant.unite = self.unite
            db.session.commit()
            self.record_historique()
    """def record_historique(self):
            ## préparation pour enregistrement valeur moyenne en bdd
            if time.time() > self.cadence_record_bdd_tps1+ self.cadence_record_bdd:
                historique_composant = Historiquecomposant()
                historique_composant.histo = self.composant
                historique_composant.valeur = self.valeur_moyenne_1/self.compteur_passage_boucle_bdd
                historique_composant.unite = self.unite
                historique_composant.valeur2 = self.valeur_moyenne_2/self.compteur_passage_boucle_bdd
                historique_composant.unite2 = self.unite2
                historique_composant.record_at = datetime.datetime.now()
                db.session.commit()

                # reset parametre de départ
                self.cadence_record_bdd_tps1 = time.time()
                self.compteur_passage_boucle_bdd = 1
                self.valeur_moyenne_1 = self.composant.valeur
                self.valeur_moyenne_2 = self.composant.valeur2
                print('pass')
            else:
                self.compteur_passage_boucle_bdd = self.compteur_passage_boucle_bdd+1

                self.valeur_moyenne_1 = self.valeur_moyenne_1 + self.composant.valeur
                self.valeur_moyenne_2 = self.valeur_moyenne_2 + self.composant.valeur2"""




class YFS201(Common):

    compteur = True
    valeur = 0
    valeur_cumule = 0

    valeur_moyenne = 0
    entre = 0
    sortie = 0
    gpio = True
    categoriecomposant = 'Débitmètre'
    infos_entre = ["Compteur d'impulsion"]
    doc = [' Formule de conversion: débit (en l/min) = fréquence (en Hz) / 7,5']
    unite = 'l/mn'
    unite2 = 'Litres'
    compteur_id = None
    testa = time.time()
    composant_test = None
    cadence = None
    temps1 = time.time()
    temps2 = None
    frequence = 0
    debit = 0


    def label(self):
        "YFS-201"
        pass

    def calcul(self):


        if time.time()>self.temps1+3:
            self.frequence = 0
        if self.frequence == 0 :
            debit = 0
        else:
            debit = self.frequence / 7.5


        datas = {
            'valeur_cumule':round(self.valeur/450,2),
            'debit': round(debit,2),
            'frequence':round(self.frequence,2)
        }
        self.composant.valeur = round(debit,2)

        self.composant.valeur2 = round(self.valeur/450,2)

        db.session.commit()
        self.record_historique()

        return datas



    def getDatas(self):
        try:
            print('hello ', self.compteur_id.valeur)

        except Exception as e:
            print(e, ' ### bug hcsr04 ### ')
            return 'bug hcsr04'



class Compteurs(Common):
    valeur = 0
    entre = 1
    sortie = 0
    ecouteur = True
    gpio = False
    categoriecomposant = 'Compteurs'
    infos_entre = ["Compteur d'impulsion"]
    doc = [' On compte']
    actived = False
    go = True
    end = False
    try:
        horloge = Status.query.filter_by(identifiant='now_time').first().time_now.timestamp()
    except:
        horloge = datetime.datetime.now().timestamp()
    top = horloge + 2
    cadence = 2
    datatest = 0
    testo = 5
    composant_test = None
    temps1 = time.time()

    def __init__(self, compteur):
        super(Common, self).__init__()
        self.compteur = compteur



    def label(self):
        "Compteur"
        pass


    def getDatas(self):
        try:
            print('L506_ Composants.py', self.valeur)

        except Exception as e:
            print(e, ' ### Compteur ### ')
            return 'Compteur'

    def op(self, Null):
        # Pourquoi mettre null ? aucune idée mais c'est tombé en marche
        # voir sûrement la doc de Asyncio
        self.valeur = self.valeur + 1
        self.composant_test.valeur = self.valeur


        #self.composant_test.valeur_moyenne = self.compteur.moyenne / (self.cadence * 7.5)
        self.composant_test.valeur_cumule = self.valeur
        #self.composant_test.cadence = self.cadence

        # fréquence des impulsions
        self.composant_test.frequence = 1/(time.time() - self.temps1)

        self.temps1 = time.time()
        self.composant_test.temps1 = self.temps1



    async def start(self, composant_test ):
        self.composant_test = composant_test
        try:
            GPIO.add_event_detect(int((self.compteur.configbcm_compteur.name).split('_')[1]), GPIO.RISING, callback=self.op)  # add rising edge detection on a channel
            self.valeur = self.compteur.valeur
            self.composant_test.valeur = self.valeur

            while True:
                try:
                    self.horloge = time.time()
                    await asyncio.sleep(2)

                    self.compteur.moyenne = float(self.valeur - self.datatest) / (time.time()-self.horloge)

                    self.datatest = self.valeur
                    self.compteur.valeur = self.valeur
                    db.session.commit()


                except Exception as error:
                    print(error)
                #print('save', self.valeur)




        except Exception as error:
            print(error)
        return True
