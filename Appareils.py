import datetime
from config import db
from models import Status, Message
import time, json, inspect

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
    titi = 'titi'
    id = None
    id_composant = 0
    enable = False
    valeur = 0
    valeur_composant = 0
    current = ''
    mdmApp = ''
    in_programmation = ''
    composant_categorie = [None]
    composant = False
    composants = []
    valeurs = None
    sonde = None
    valeurs_model =[]
    files_img = ['assets/composant/eclairage/1.webp', 'assets/composant/eclairage/2.webp',
                 'assets/composant/eclairage/3.webp']

    ###################
    tempo = False

    ###################
    seuil_haut = False
    seuil_bas = False
    consigne_atteinte = False
    valeur_regulateur = None

    valeur_cumule = 0
    appareil_on = True
    message = ''

    regulation_par_composant = False
    horloge = None

    ## gestion des messages
    nouveau_message = False
    message = ''
    message_type = ''

    def __init__(self, appareil):
        if Status.query.filter_by(identifiant='now_time').first() == None:
            status = Status()
            status.identifiant = 'now_time'
            status.time_now = datetime.datetime.now()
            db.session.add(status)
            db.session.commit()
            self.horloge = status
        else:
            self.horloge = Status.query.filter_by(identifiant='now_time').first()

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
        self.composants = appareil.composants

    def getComposants(self):

        self.valeurs_model = []
        #print(' ??????????????????????????? L106 Appareils.py',self.appareil,self.valeur_composant,self.valeur_cumule,' ?????????????????? \n')
        if self.regulation_par_composant:
            #print('     ################# valeur    ####################')
            for valeur in self.valeurs.valeur_id :
                #print(valeur, "L70")
                #print(valeur.valeur_cumule, valeur.consigne)
                if valeur.valeur_cumule is None:
                    valeur.valeur_cumule = 0
                if bool(valeur.actived) & self.regulation_par_composant:
                    if valeur.valeur_cumule < valeur.consigne:
                        self.consigne_atteinte = False
                        self.message = ' En régulation'
                    else:
                        self.consigne_atteinte = True
                        self.message = 'Consigne Atteinte'
                #print(bool(self.appareil_on))
                if bool(valeur.actived) and (valeur.valeur_cumule < valeur.consigne) and bool(self.appareil_on) == True:
                    #print("goggogogoggogo")
                    self.valeur_composant = valeur.val
                    self.valeur_cumule = self.valeur_cumule+valeur.val
                    valeur.valeur_cumule = valeur.valeur_cumule+valeur.val


                    if valeur.min > valeur.val:
                        self.seuil_bas = True
                    else:
                        self.seuil_bas = False

                    if valeur.max < valeur.val:
                        self.seuil_haut = True
                    else:
                        self.seuil_haut = False
                else:
                    valeur.val = 0
                    self.valeur_composant = 0
                    self.off()
                if bool(valeur.init):
                    self.consigne_atteinte = False
                    valeur.valeur_cumule = 0
                    valeur.init = False

                self.valeurs_model.append(valeur)



            #print('     ########### Fin Valeur     ########## \n')
                #db.session.add(valeur)
            #db.session.commit()
        #print(' ??????????????????????????? \n')

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
                print(self.appareil.mode_de_marche.mode_de_marche)

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
        elif mode_de_marche == 'manuel':
            try:
                self.manuel()
            except Exception as e:
                print('L167_', e)
                print('erreur mdm manuel', self.label.__doc__)

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

            gpio.output(int(Gpio), gpio.HIGH)
        except:
            print('gpio.out({}, gpio.LOW)'.format(Gpio), 'error')

        # mise à 0 d'un gpio

    def gpio_off(self, Gpio):

        try:
            Gpio = (Gpio.split('_'))[1]
            gpio.output(int(Gpio), gpio.LOW)
        except:
            print('gpio.out({}, gpio.HIGH)'.format(Gpio), 'error')
            pass

    def read_gpio(self,Gpio):
        try:
            Gpio = (Gpio.split('_'))[1]

            return gpio.input(int(Gpio))
        except:
            print('gpio.input({})'.format(Gpio), 'error')

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

    def off(self):
        pass

    def __repr__(self):
        return None

class Eclairage(Common):
    enable = False
    entre = 1
    sortie = 1
    infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('test', 'Test'), ('off', 'Off'), ('manu', 'Manuel'), ('prog', 'Programmation')]
    manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = False
    files_img = ['assets/composant/eclairage/1.webp','assets/composant/eclairage/2.webp','assets/composant/eclairage/3.webp']

    def __repr__(self):
        return "Contacteur avec bouton de commande Type éclairage ou autre"

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
    enable = True
    valeur_temp = 19
    sortie = 2
    entre = 0
    sonde = True
    sonde_type = 'ds1820b'
    infos_entre = ['Sonde ds1820']
    infos_sortie = ['Relais on/off', 'Relais eco' ]
    manuel = [('arret', 'Arrêt'), ('eco', 'Eco'), ('confort', 'Confort')]
    choices_mdm = [('off', 'Off'), ('eco', 'Eco'),('confort','Confort'), ('prog', 'Programmation')]
    current = 'Waiting ...'
    sonde_en_service = False
    composant = False

    # gestion message
    mdm = None
    mdm_prog = False
    stat_sortie =None



    def label(self):
        "Chauffage"
        pass



    # sonde:Détermine si la valeur actuelle dépasse la consigne mini
    def sonde_min_on(self):
        # si valeur > consigne mini
        if float(self.appareil.appareil_sonde.sonde_valeur_id.valeur)>float(self.appareil.min):

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

                self.gpio_off(self.A0)
                self.gpio_off(self.A1)
                self.current = self.appareil.categorieappareil+'_off'
                if self.stat_sortie != 'off':

                    message = Message()
                    message.appareil = self.appareil
                    message.recorded_at = datetime.datetime.now()
                    message.type = 'success'
                    message.message = 'off'
                    db.session.add(message)
                    db.session.commit()

                    self.stat_sortie = 'off'


        except Exception as e:
            print('L261')
            print(e)

    def mode_eco(self):
        if self.marcheForce():
            self.confort(self.sonde)
        else:

            self.gpio_on(self.A0)
            self.gpio_off(self.A1)
            self.current = self.appareil.categorieappareil+'_eco'
            if self.stat_sortie != 'eco':
                message = Message()
                message.appareil = self.appareil
                message.recorded_at = datetime.datetime.now()
                message.type = 'success'
                message.message = 'Chauffage temp confort'
                db.session.add(message)
                db.session.commit()

                self.stat_sortie = 'eco'

    def mode_confort(self):
        self.gpio_on(self.A0)
        self.gpio_on(self.A1)
        self.current = self.appareil.categorieappareil+'_confort'
        if self.stat_sortie != 'confort':
            message = Message()
            message.appareil = self.appareil
            message.recorded_at = datetime.datetime.now()
            message.type = 'success'
            message.message = 'Chauffage temp confort'
            db.session.add(message)
            db.session.commit()

            self.stat_sortie = 'confort'



    ## fin
    # programmation des modes de marches
    def off(self):
        self.mode_off()
        if self.mdm != 'off':
            message = Message()
            message.appareil = self.appareil
            message.recorded_at = datetime.datetime.now()
            message.type = 'success'
            message.message = 'mdm Off'
            db.session.add(message)
            db.session.commit()
            self.mdm = 'off'


    def eco(self, sonde):
        if self.mdm != 'eco' and self.mdm_prog == False:
            message = Message()
            message.appareil = self.appareil
            message.recorded_at = datetime.datetime.now()
            message.type = 'success'
            message.message = 'mdm eco'
            db.session.add(message)
            db.session.commit()
            self.mdm = 'eco'

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
        if self.mdm != 'confort':
            message = Message()
            message.appareil = self.appareil
            message.recorded_at = datetime.datetime.now()
            message.type = 'success'
            message.message = 'mdm Confort'
            db.session.add(message)
            db.session.commit()
            self.mdm = 'confort'
            #self.mdm_prog = False
        try:
            if sonde.en_service and self.appareil.sonde_actived:
                if not self.sonde_max_on():
                    self.mode_confort()

                elif self.sonde_max_on():
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

        """if self.mdm_prog == False:
            message = Message()
            message.appareil = self.appareil
            message.recorded_at = datetime.datetime.now()
            message.type = 'success'
            message.message = 'mdm programmation'
            db.session.add(message)
            db.session.commit()
        self.mdm_prog = True"""


        if programmation or self.marcheForce() == True:

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

    def __repr__(self):
        return "Chauffage avec ou sans régulation (sonde)"
class ChauffeEau(Common):
    enable = True
    entre = 0
    sortie = 1
    #infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('marche', 'Marche'), ('prog', 'Programmation')]
    #manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = False
    composant_categorie = [None]

    regulation_par_composant = False

    def __repr__(self):
        return " Contacteur simple Type commande Chauffeau-eau, arrosage automatique ou autre "


    def label(self):
        "Contacteur simple"
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
        self.current = self.appareil.categorieappareil+'_on'



    def marche(self):
        self.on()
        print('marche')

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


class Pompe(Common):
    enable = True
    valeur = 0
    entre = 0
    sortie = 1
    # infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('marche', 'Marche'), ('prog', 'Programmation')]
    # manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = True
    composant_categorie = ['Capteur de distance','Débitmètre']
    instance_composant = 'null'
    debimetre = None
    capteur_distance = None
    message = ''
    testo = 'ii'
    regulation_par_composant = True
    composant_id = 21
    consigne = 14000

    def __repr__(self):
        return "Contacteur Régulé par un débit ou un niveau Type pompe"
    def label(self):
        "Pompe"
        pass

    def test(self,instance):
        # instance => datas ( appareil) issue de la bdd
        # self => datas issue de Composants.py
        pass


    def off(self):
        # ! very important
        #print(self.composant_id.compteur_id.compteur.valeur)


        if self.marcheForce() and self.consigne_atteinte == False:
            self.appareil_on = True
            self.gpio_on(self.A0)
            self.current = self.appareil.categorieappareil + '_on'
            print('marche forcée')
        else:
            self.appareil_on = False
            self.gpio_off(self.A0)
            self.current = self.appareil.categorieappareil + '_off'
            print('off pompe', self.A0)

    def programmation(self):

        print('programmation pompe')
        pass

    def marche(self):
        print(self.composant_id.compteur_id.compteur.valeur, self.consigne)

        if self.composant_id.compteur_id.compteur.valeur< self.consigne:
            self.appareil_on = True
            self.gpio_on(self.A0)

            self.current = self.appareil.categorieappareil + '_on'
            print(self.appareil_on,'marche pompmmme', self.message)
        else:
            self.gpio_off(self.A0)
        pass

class Contacteur2I(Common):
    enable = True
    entre = 2
    sortie = 1
    infos_entre = ['Bouton On','Bouton Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('manuel', 'Manuel'), ('prog', 'Programmation')]
    manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = False
    composant_categorie = [None]

    regulation_par_composant = False



    def __repr__(self):
        return "Contacteur avec bouton marche et boutton arrêt "

    def label(self):
        "Contacteur2I"
        pass

    def off(self):
        self.off(self.A0)

    def manuel(self):
        try:
            print('manunuu', self.read_gpio(self.A0), self.read_gpio(self.I0),self.read_gpio(self.I1))


            # si bp_marche + relais_off => self.on
            if int(self.read_gpio(self.I0))==1 and int(self.read_gpio(self.A0)==1):
                print('on')
                self.gpio_on(self.A0)

            if int(self.read_gpio(self.I1)) == 1 and int(self.read_gpio(self.A0)==0):
                self.gpio_off(self.A0)
                print('off')
            # si bp_arrêt et relais_on
            #if self.read_gpio(self.I0) == False and self.read_gpio(self.I1)==True and self.read_gpio(self.A0)==True:
            #    print('off')


        except Exception as error:
            print('erreur lecture input, L595', error)


class Contacteur_Temporise(Common):
    enable = True
    entre = 2
    sortie = 1
    infos_entre = ['Bouton On', 'Bouton Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('manuel', 'Manuel'), ('prog', 'Programmation')]
    manuel = [('arret', 'Arrêt'), ('marche', 'Marche')]
    sonde = False
    composant = False
    composant_categorie = [None]
    tempo = True
    regulation_par_composant = False
    top = 0.2
    def __repr__(self):
        return "Contacteur temporisé avec bouton marche et boutton arrêt "

    def label(self):
        "Contacteur temporisé"
        pass

    def s_off(self):
        self.gpio_off(self.A0)
        self.current = self.appareil.categorieappareil + '_off'
        self.appareil.tempos.start = False
        self.appareil.tempos.finish = True

    def s_on(self):
        self.gpio_on(self.A0)
        self.current = self.appareil.categorieappareil + '_on'
        self.appareil.tempos.start_at = datetime.datetime.now()
        self.appareil.tempos.start = True
        self.appareil.tempos.finish = False

    # Mode de marche
    def off(self):
        self.s_off()



    def manuel(self):
        try:


            # si bp_marche + relais_off => self.on
            if int(self.read_gpio(self.I0)) == 1 :
                self.s_on()
                self.top = self.horloge.time_now.timestamp() + float(self.appareil.tempos.consigne)

                message = Message()
                message.appareil = self.appareil
                message.recorded_at = datetime.datetime.now()
                message.type = 'success'
                message.message = 'Manuel - On'
                db.session.add(message)
                db.session.commit()

            elif (int(self.read_gpio(self.I1)) == 1 and int(self.read_gpio(self.A0) == 0)) or (self.top < self.horloge.time_now.timestamp() and int(self.read_gpio(self.I0))==0 and int(self.read_gpio(self.A0) == 0)):
                self.s_off()
                self.top = 0.2

                message = Message()
                message.appareil = self.appareil
                message.recorded_at = datetime.datetime.now()
                message.type = 'success'
                message.message = 'Manuel - Off'
                db.session.add(message)
                db.session.commit()

            elif int(self.read_gpio(self.A0)) == 0 and self.top == None and int(self.read_gpio(self.I1)) == 1:
                self.top = self.horloge.time_now.timestamp() + float(self.appareil.tempos.consigne)


        except Exception as error:
            print('erreur lecture input, L595', error)

    def programmation(self, programmation):
        try:
            if programmation or self.marcheForce() == True:
                self.in_programmation = True
                if self.read_gpio(self.A0)==1:
                    message = Message()
                    message.message = "Programmation On"
                    message.type = "success"
                    message.recorded_at = datetime.datetime.now()
                    message.appareil = self.appareil
                    db.session.add(message)
                    db.session.commit()

                self.s_on()

            else:
                if self.read_gpio(self.A0)==0:
                    message = Message()
                    message.message = "Programmation Off"
                    message.type = "success"
                    message.recorded_at = datetime.datetime.now()
                    message.appareil = self.appareil
                    db.session.add(message)
                    db.session.commit()

                self.s_off()
                # print('roto',self.current)
                self.in_programmation = False
        except Exception as error:
            print(error, 'bug contacteur temporisé programmation')

class Hygro(Common):
    enable = False
    valeur = 0
    entre = 0
    sortie = 1
    # infos_entre = ['Bouton On/Off']
    infos_sortie = ['Relais on/off']
    choices_mdm = [('off', 'Off'), ('marche', 'Marche'), ('prog', 'Programmation')]
    # manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = True
    composant_categorie = ['Capteur_humite']
    instance_composant = ''
    debimetre = None
    capteur_distance = None
    message =''
    regulation_par_composant = True



    def __repr__(self):
        return "Régulateur Hygrométrique "

    def label(self):
        "Hygro"
        pass

class Demarreur_Etoile_Triangle(Common):
    enable = True
    entre = 3
    sortie = 3
    infos_entre = ['On','Off','Défaut thermique']
    infos_sortie = ['Ligne','Etoile','Triangle']
    choices_mdm = [('off', 'Off'), ('manuel', 'Manuel'), ('prog', 'Programmation')]
    manuel = [('arret','Arrêt'), ('marche','Marche')]
    sonde = False
    composant = False
    composant_categorie = [None]
    top = 0
    tempo = True

    regulation_par_composant = False

    # defaults
    default_thermique = False
    demande_arret = False


    def __repr__(self):
        return "Démarreur étoile-triangle "

    def label(self):
        "Démarreur étoile-triangle"
        pass
    def off(self):
        self.top = 0
        self.gpio_off(self.A0)
        self.gpio_off(self.A1)
        self.gpio_off(self.A2)
        self.appareil.tempos.start = False
        self.appareil.tempos.finish = True
        return True

    def manuel(self):

        if int(self.read_gpio(self.I2))== 0 and self.default_thermique == False:
            self.default_thermique = True
            message = Message()
            message.appareil = self.appareil
            message.type = 'warning'
            message.message = ' Déclenchement Relais thermique'
            message.recorded_at = datetime.datetime.now()
            db.session.add(message)
            db.session.commit()
            self.nouveau_message = True
        elif int(self.read_gpio(self.I2))== 1 and self.default_thermique == True:
            self.default_thermique = False

        try:
            # Gestion du relais thermique
            if int(self.read_gpio(self.I2)) == 0:
                if(self.read_gpio(self.A0)==0):
                    self.off()

            # si bp_marche + relais_off => self.on
            if int(self.read_gpio(self.I0)) == 1 and int(self.read_gpio(self.A0)) == 1 and int(
                    self.read_gpio(self.I2)) == 1:
                print('Etoile')
                self.demande_arret = False
                self.gpio_on(self.A0)
                self.gpio_on(self.A1)
                self.appareil.tempos.start_at = datetime.datetime.now()
                self.appareil.tempos.start = True
                self.appareil.tempos.finish = False

                message = Message()
                message.appareil = self.appareil
                message.type = 'success'
                message.message = ' Demande de marche'
                message.recorded_at = datetime.datetime.now()
                db.session.add(message)
                db.session.commit()


            if int(self.read_gpio(self.A0)) == 0 and self.top == 0 and int(self.read_gpio(self.A2)) == 1 and int(
                    self.read_gpio(self.I2)) == 1:
                self.top = self.horloge.time_now.timestamp() + float(self.appareil.tempos.consigne)


            if self.top < self.horloge.time_now.timestamp() and int(self.read_gpio(self.A0) == 0) and int(
                    self.read_gpio(self.A1) == 0) and int(self.read_gpio(self.I2)) == 1:
                self.gpio_on(self.A0)
                self.gpio_off(self.A1)
                self.gpio_on(self.A2)
                print('Triangle')
                self.appareil.tempos.start = False
                self.appareil.tempos.finish = True

            # si bp_arrêt et relais_on
            if bool(self.read_gpio(self.I0)) == False and bool(self.read_gpio(self.I1))==True and bool(self.read_gpio(self.A0))==False:
                print('arret',self.demande_arret)
                if self.demande_arret == False:
                    self.off()

                    message = Message()
                    message.appareil = self.appareil
                    message.type = 'warning'
                    message.message = ' Demande d\'arrêt'
                    message.recorded_at = datetime.datetime.now()
                    db.session.add(message)
                    db.session.commit()

                    print('arret')
                    self.demande_arret = True


        except Exception as error:
            print('erreur lecture input, L678',error,self.top)