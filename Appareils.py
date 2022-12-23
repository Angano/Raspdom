import datetime
from config import db
#from models import Appareil as appareilModel
import time, json, inspect
from time import sleep
try:
	import RPi.GPIO as gpio
except:
	pass

from models import Appareil, Manuel
try:
    import RPi.GPIO as gpio
except:
    print('bug import gpio')

class Common():
    current = ''
    mdmApp = ''
    in_programmation = ''
    def __init__(self, appareil=None):
        self.appareil = appareil

        if appareil.order_gpio == None:
            gpios = []
            for i in range(self.appareil.nbre_gpio):
                gpios.append('')
        else:
            gpios = json.loads(self.appareil.order_gpio)

        for i in range(self.entre):
            data = 'I'+str(i)
            setattr(self,data,gpios[i])
        for i in range(self.sortie):
            data = 'A' + str(i)
            setattr(self,data,gpios[i+self.entre])


    def start(self, mode_de_marche, sonde, programmation, ordre, appareil):

        if mode_de_marche == 'arret':
            try:
                self.off()
            except Exception as e:
                print('L41_',e)
                print('erreur mdm arrêt', self.label.__doc__)

        elif mode_de_marche == 'off':
            try:
                self.off()
            except Exception as e:
                print('L48_',e)
                print('erreur mdm off', self.label.__doc__)

        elif mode_de_marche == 'on':
            if sonde:
                try:
                    self.on(sonde)
                except:
                    print('erreur on(sonde)', self.label.__doc__)
            else:
                try:
                    self.on()
                except:
                    print('erreur on()', self.label.__doc__)
        elif mode_de_marche == 'eco':
            try:
                self.eco(sonde)
            except:
                print('erreur mdm eco', self.label.__doc__)
        elif mode_de_marche == 'confort':
            try:
                self.confort(sonde)
            except:
                print('erreur mdm confort', self.label.__doc__)
        elif mode_de_marche == 'prog':
            try:
                self.programmation(programmation)
            except:
                print('bug programmation', self.appareil.nom)
                self.off()
        elif mode_de_marche == 'manu':
            print('manu')

        elif mode_de_marche == 'hs':
            print('hs')
        elif mode_de_marche == 'es':
            print('en service')
        elif mode_de_marche == 'test':
            self.test(ordre, sonde)
        elif mode_de_marche == 'marche':
            self.marche()
        else:
            print('pas trouvé de mode de marche ', mode_de_marche)
        self.mdmApp = mode_de_marche

        # mise à un d'un gpio

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


    def marcheForce(self):
        if self.appareil.mf is not None:
            print('hellooooo')
            debut = self.appareil.mf.debut
            fin = self.appareil.mf.fin
            now = datetime.datetime.now()

            if fin>now>debut and self.appareil.mf.actived == True:
                print('ça force !')
                return True
            else:
                print('ça ne force pas !')
                if fin<now and self.appareil.mf.actived == True:

                    self.appareil.mf.actived = False
                    db.session.add(self.appareil)
                    db.session.commit()
                return False
        else:
            return False


class Eclairage(Common):
    entre = 1
    sortie = 1
    infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('test', 'Test'), ('off', 'Off'), ('manu', 'Manuel'), ('prog', 'Programmation')]
    manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False


    def label(self):
        "Eclairage"
        pass

    def off(self):
        if self.marcheForce():
            self.gpio_on(self.A0)
            self.current = self.appareil.categorieappareil+'_on'
        else:
            self.gpio_off(self.A0)
            self.current = self.appareil.categorieappareil+'_off'

    def on(self):
        self.gpio_on(self.A0)
        self.current = self.appareil.categorieappareil+'_on'

    def manu(self):
        if self.I0 is True or self.marcheForce():
            self.on()
        else:
            self.off()

    def test(self, ordre, sonde):
        if self.marcheForce():
            self.on()
        else:
            try:
                if ordre.ordre == 'marche':
                    self.on()
                else:
                    self.off()
            except ValueError:
                print(ValueError)

    def programmation(self,programmation):

        if programmation or self.marcheForce():
            self.on()
            self.in_programmation = 'True'
        else:
            self.off()
            self.in_programmation = 'False'


class ChauffageR(Common):
    valeur_temp = 19
    sortie = 2
    entre = 1
    sonde = True
    sonde_type = 'ds1820b'
    infos_entre = ['Sonde ds1820']
    infos_sortie = ['Relais on/off', 'Relais eco' ]
    manuel = [('arret', 'Arrêt'), ('eco', 'Eco'), ('confort', 'Confort')]
    choices_mdm = [('off', 'Off'),('test','Test'), ('eco', 'Eco'),('confort','Confort'), ('prog', 'Programmation')]
    current = 'Waiting ...'
    sonde_en_service = False



    def label(self):
        "Chauffage"
        pass
        """ mis cette section dans common
   # mise à un d'un gpio
    def gpio_on(self, Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]
            
            gpio.output(int(Gpio), gpio.LOW)
        except :
            print('gpio.out({}, gpio.LOW)'.format(Gpio), 'error')

   # mise à 0 d'un gpio
    def gpio_off(self, Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]
            gpio.output(int(Gpio), gpio.HIGH)
        except:
             #print('gpio.out({}, gpio.HIGH)'.format(Gpio), 'error')
            pass
        
    """


    # sonde:Détermine si la valeur actuelle dépasse la consigne mini
    def sonde_min_on(self):
        # si valeur > consigne mini
        if float(self.appareil.appareil_sonde.sonde_valeur_id.valeur)>float(self.appareil.min):
            print(self.appareil.min,'print mini')
            return True
        else:
            return False


    # sonde:Détermine si la valeur actuelle dépasse la consigne max
    def sonde_max_on(self):
        if float(self.appareil.appareil_sonde.sonde_valeur_id.valeur)>float(self.appareil.max):
            return True
        else:
            return False


   ## Mode de marche du radiateur
    def mode_off(self):
        try:
            if self.marcheForce() == True:
                self.confort(self.sonde)
            else:
                print('arret')
                self.gpio_off(self.A0)
                self.gpio_off(self.A1)
                self.current = self.appareil.categorieappareil+'_off'
        except Exception as e:
            print('L261')
            print(e)

    def mode_eco(self):
        if self.marcheForce():
            self.confort(self.sonde)
        else:
            print('eco')
            self.gpio_on(self.A0)
            self.gpio_off(self.A1)
            self.current = self.appareil.categorieappareil+'_eco'

    def mode_confort(self):
        print('confort')
        self.gpio_on(self.A0)
        self.gpio_on(self.A1)
        self.current = self.appareil.categorieappareil+'_confort'


    ## fin
    # programmation des modes de marches
    def off(self):
        self.mode_off()


    def eco(self, sonde):
        if sonde.en_service and self.appareil.sonde_actived:
            if not self.sonde_min_on():
                #print('true on chauffe')
                self.mode_confort()
            elif self.sonde_min_on():
                #print('true stop chauffe')
                self.mode_off()
            else:
                print('pas compris')
                self.mode_confort()
        else:
            self.mode_eco()


    def confort(self,sonde):
        try:
            if sonde.en_service and self.appareil.sonde_actived:
                if not self.sonde_max_on():
                    print('False on chauffe')
                    self.mode_confort()

                elif self.sonde_max_on():
                    print('true stop chauffe')
                    self.mode_off()

                else:
                    print('pas compris')
                    self.mode_off()
            else:
                self.mode_confort()
        except Exception as e:
            print(e)
            self.mode_confort()


    def programmation(self, programmation):
        if programmation or self.marcheForce() == True:
            print('force')
            self.confort(self.appareil.appareil_sonde)
            self.in_programmation = True
        else:
            self.eco(self.appareil.appareil_sonde)
            #print('roto',self.current)
            self.in_programmation = False


    def test(self, ordre, sonde):
        sonde.en_service = False
        if ordre.ordre == 'arret':
           self.mode_off()
        elif ordre.ordre == 'eco':
            self.eco(sonde)
        elif ordre.ordre == 'confort':
            self.confort(sonde)
        else:
            print('else')

class ChauffeEau(Common):
    entre = 0
    sortie = 1
    #infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('marche', 'Marche'), ('prog', 'Programmation')]
    #manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False


    def label(self):
        "Chauffe eau"
        pass

    def off(self):
        if self.marcheForce():
            self.on()
        else:
            self.gpio_off(self.A0)
            self.in_programmation = 'False'
            self.current = self.appareil.categorieappareil+'_off'

    def on(self):
        self.gpio_on(self.A0)
        self.in_programmation = 'True'
        self.current = self.appareil.categorieappareil+'_on'



    def marche(self):
        self.on()

    def test(self, ordre, sonde):
        if self.marcheForce():
            self.on()
        else:
            try:
                if ordre.ordre == 'marche':
                    self.on()
                else:
                    self.off()
            except ValueError:
                print(ValueError)

    def programmation(self,programmation):
        if programmation or self.marcheForce():
            self.on()
        else:
            self.off()



