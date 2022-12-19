#!./venv/bin/python
from models import Gpio, Programmation, Appareil, ModeDeMarche, Sonde, Manuel, Status, ValeurSonde, GpioBcm
from Appareils import Eclairage, ChauffageR, ChauffeEau
from config import session
import glob

import time
import sys, inspect

# mode dev sur pc
mod_dev = True

try:
	import RPi.GPIO as gpio
	gpio.setmode(gpio.BCM)
except:
	pass
"""try:
    import RPi.GPIO as gpio
    mode = gpio.getmode()
    print(mode)
    exit()
except:
    print('erreur import RPi.GPIO')"""
def findDS1820():
    tab = []
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')
    # present
    # chemin réf de  la sonde
    # nom ds1820b
    # valeur

    for device in device_folder:
        file = open(device+'/w1_slave','r')
        data = float(file.read().partition("t=")[-1])/1000.0
        file.close()
        tab.append((device.split('/')[-1],data))
    return tab
##################################################################
def updateValeurDs1820():
    sondes = findDS1820()
    for sonde in sondes:
        sondeDS1820 = session.query(Sonde).filter_by(nom=sonde[0]).first()
        #sondeDS1820.sonde_valeur_id.valeur = sonde[1] 
        sondeDS1820.sonde_valeur_id.valeur = float(sonde[1])
        
    session.commit()


 


# Initialisation des capteurs ds1820b avec lecture des valeurs
# on rentre les capteurs valident avec leur valeur dans la base de donnée
def check_ds1820b():
    # capteurs présents avec lecture des valeurs
    # Valeur factisses
    #list_ds1820b = [('ds_1',19.23), ('ds_2',22.21),('ds_3',18.4), ('ds_4',24.65)]
    list_ds1820b = findDS1820()

    # capturs déclarés dans la bdd
    ds1820bs = [ (data.nom) for data in session.query(Sonde).all()]

    # reset 'présence' ds1820b en bdd
    # plus lecture valeur sonde et enregistrement en bdd
    if len(ds1820bs)>0:
        for ds1820b in ds1820bs:

            data = session.query(Sonde).filter_by(nom=ds1820b).first()
            if data == None:
                data = Sonde()
                valeursonde = ValeurSonde()
                data.sonde_valeur = valeursonde
                session.add(valeursonde)
            data.present = False
            session.add(data)


    # inscription des nouveaux capteurs détectés
    # et passage à 1 des capteurs déclarés en bdd  et détecté physiquement
    # les valeurs lues sont inscrites également
    for ds1820b in list_ds1820b:
        if ds1820b[0] in ds1820bs:
            sonde = session.query(Sonde).filter_by(nom=ds1820b[0]).first()
            sonde.present = True
            sonde.type_sonde = 'Ds1820b'
            sonde.sonde_valeur = float(ds1820b[1])
            session.add(sonde)
        else:
            sonde = Sonde()
            sonde.nom = ds1820b[0]
            sonde.present = True

            valeursonde = ValeurSonde()
            valeursonde.valeur = ds1820b[1]

            sonde.sonde_valeur_id = valeursonde

            session.add(sonde)
            session.add(valeursonde)
    session.commit()
    return True

# On transfert les valeurs des GPIO dans la table Gpio_Bcm
# Cette valeur sera lu par le programme
# Plus ( a vérifier ) on entre le nom du gpio dans la table GpioBcm
def get_status_gpio():
    gpios = [(data) for data in range(27)]

    # On transfert les valeurs des GPIO dans la table Gpio_Bcm
    # Cette valeur sera lu par le programme
    try:
        if gpio:
            for data in gpios:
                Gpio = session.query(Gpio_Bcm).filter_by(name=str(data)).first()
                Gpio.status = gpio.input(int(data))
                session.add(Gpio)
            session.commit()
           
    except:
        pass
        
    # Initialisation des nom des GPIO dans la table GpioBcm
    for data in gpios:
        Gpio = session.query(GpioBcm).filter_by(name=str(data)).first()
        if Gpio==None:
            Gpio = GpioBcm()
            Gpio.name = str(data)
            session.add(Gpio)
        session.commit()
    return True

# Configuration des GPIO ( mode Input ou Output) utilisé en base de donnée
# Configuration également des ds1820b
def init(gpio):
    get_status_gpio()
    gpios_start = [ (data) for data in range(0,27) if data not in [0,1,2,3,4]]

    # On passe tous les GPIO en mode Input
    for Gpiod in gpios_start:
        try:
            gpio.setup(Gpiod, gpio.IN)
        except Exception as e: print(e)
		
            #print('je eeeeeeee ne suis pas sur un Raspberry')

    # Initialisation des capteur ds1820b
    check_ds1820b()

    # on affecte le mode Input ou Output aux GPIO
    # en fonction de la configuration entrée en bdd
    datas = [(data.mode, data.valeur.split('_')[1]) for data in session.query(Gpio).all()]
    for gpios in datas:
        # GPIO en mode Input
        if gpios[0] == 'Input':
            try:
                gpio.setup(int(gpios[1]),gpio.IN)
            except Exception as e: print(e)
                #print('je ne suis pas sur un raspberry')

        # GPIO en mode Output avec mise à 1 de la sortie
        elif gpios[0] == 'Output':
            try:
                gpio.setup(int(gpios[1]), gpio.OUT)
                gpio.output(int(gpios[1]), True)
            except:
                print('je ne suis pas sur un rasberry')

    try:
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        # déclaration des GPIOs
        for gpio in datas:
            if gpio[0] == 'Input':
                print('gpio.setup({},gpio.IN)'.format(gpio[1]))
            elif gpio[0] == 'Output':
                print('gpio.setup({}, gpio.OUT)'.format(gpio[1]))
       
    except:
        print('bug RPI.GPIO')
    session.commit()
    return True


# Optention du mode de marche déclarer en bdd d'un appareil
def get_mdm(appareil):
    mdm = appareil.mode_de_marche.mode_de_marche
    if appareil.appareil_sonde:
        sonde = appareil.appareil_sonde
    else:
        sonde = False
    # Si présence de programmation en relation avec l'appareil
    # on récupère ses programmations
    if mdm=='prog':
        programmation = appareil.get_programmations()
    else:
        programmation = False

    if mdm == 'test':
        ordre = appareil.manuel
    else:
        ordre = False
    # on lance l'appareil
    try:
        globals()[appareil.nom].start(mdm, sonde, programmation, ordre)
    except :
        print('not way', appareil.nom, mdm, sonde, programmation, ordre)
    #print(globals()[appareil.nom].current, appareil.id, appareil.nom)
    return [globals()[appareil.nom],appareil]


# liste des instances des appareils
def get_appareils():
    appareils = list()
    # liste des appareil enregistrés dan la base de donnée
    list_appareil = session.query(Appareil).all()
    status = session.query(Status).get(1)
    # On vérifie si la configuration a été modifié par l'ajout ou la suppression d'un appareil
    # si oui, on déclarage/ recharge la nouvelle configuration
    if status == None:
        status = Status()
    status.status = False
    session.add(status)
    session.commit()

    if mod_dev:
        init(gpio=None)
    else:
        init(gpio)

    for appareil in list_appareil:
        try:
            # création des instances correspondant à la liste des apppareils en bdd
            globals()[appareil.nom] = globals()[appareil.categorieappareil](appareil)

            data = {appareil: globals()[appareil.nom]}
            appareils.append(data)

        except ValueError:
            print(ValueError, 'erreur mise en place instance appareil')

    # renvoie de la liste des instances
    return appareils

def start(gpio):
    if init(gpio):
        
        # Gestion de la mise à jour température sonde
        step = 60*5
        top = time.time()+step
        

        print('init oki')
        appareils = get_appareils()
        while True:
            if time.time()>top:
                top = time.time()+step
                updateValeurDs1820()
                print(top)
                print('updateValeurDs1820')
            #appareils = get_appareils()
            status = session.query(Status).get(1).status
            session.commit()
            if status:
                appareils = get_appareils()
                print('get_appareil()')
            print(time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec)
            for appareil in appareils:
                for key, value in appareil.items():
                    try:
                        datas = (get_mdm(key))

                        #print(datas[0], datas[1].nom, datas[1].id)
                        ############################################
                        infos = {
                            'appareil_id':datas[1].id,
                            'sonde':datas[1].sonde,
                            'sonde_id':datas[1].sonde_id,
                            'sonde_actived':datas[1].sonde_actived,
                            'sonde_presente':datas[1].sonde.present,
                            'sonde_valeur':datas[1].sonde.sonde_valeur_id.valeur,
                            'sonde_valeur_min':datas[1].sonde.min,
                            'sonde_valeur_max':datas[1].sonde.max,
                            'status':datas[0].current,
                            'mdm':datas[0].mdmApp,
                            'mdm model':datas[1].mode_de_marche.mode_de_marche,
                            'in_programmation':datas[0].in_programmation}

                        datas[1].sortie = infos['status']
                        #print(infos['appareil_id'])
                        session.add(datas[1])
                        ############################################
                    except :
                        print(ValueError.__doc__)
            session.commit()
            updateValeurDs1820()
            time.sleep(5)
           

            print('####  ###')
    else:
        print('init not good')

if mod_dev:
    start(gpio=None)
else:
    start(gpio)
