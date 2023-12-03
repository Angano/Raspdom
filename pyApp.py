#!./venv/bin/python
import datetime

from models import ConfigBcm, Historique, Bus,Historiquecomposant, Valeur, Gpio, Programmation, Appareil, ModeDeMarche, Sonde, Manuel, Status, ValeurSonde, GpioBcm, Compteur, Composant
#from Appareils import Eclairage, ChauffageR, ChauffeEau, Pompe, Hygro, Contacteur2I, Demarreur_Etoile_Triangle
from Appareils import *
from Composants import HCSR04, BMP180, DHT22, YFS201, Compteurs
from config import session, db
import glob
import helpers

import time
import sys, inspect
import asyncio

mod_dev = False
try:
    import RPi.GPIO as gpio
    gpio.setmode(gpio.BCM)
    mod_dev = False
except Exception as e:
    print(e, "erreur import Rpi")
    #mode dev sur pc
    mod_dev = True


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
async def updateValeurDs1820():
    val = 10
    top = time.time() + val
    while True:

        datas = Status.query.filter(Status.identifiant=='update_temp').first()

        if datas == None:
            datas = Status()
            datas.identifiant = 'update_temp'
            datas.status = 0
            datas.valeur = '5'
            session.add(datas)
            session.commit()


        timer = time.time()
        if timer >top or datas.status==True:
            val = datas.valeur


            sondes = []
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28*')
            # present
            # chemin réf de  la sonde
            # nom ds1820b
            # valeur

            for device in device_folder:
                print('hello')
                file = open(device + '/w1_slave', 'r')
                data = float(file.read().partition("t=")[-1]) / 1000.0
                file.close()
                sondes.append((device.split('/')[-1], data))
                print('hello2')




            for sonde in sondes:
                sondeDS1820 = session.query(Sonde).filter_by(nom=sonde[0]).first()
                historique = Historique()
                historique.record_at = datetime.datetime.now()
                historique.valeur = float(sonde[1])
                historique.histo = sondeDS1820
                session.add(historique)
                sondeDS1820.historiques.valeur = 0.1
                #sondeDS1820.historiques.record_at = datetime.datetime.now()
                #sondeDS1820.sonde_valeur_id.valeur = sonde[1]
                sondeDS1820.sonde_valeur_id.valeur = float(sonde[1])
                print('hello3')

            db.session.commit()
            top = time.time()+float(datas.valeur)




        await asyncio.sleep(2)
        val = 20
        datas = None


 


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
        session.commit()

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
"""def get_status_gpio():
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
    return True"""

def status_gpio():
    gpios = Gpio.query.all()

    if mod_dev == False:
        for my_gpio in gpios:
            var = int(my_gpio.valeur.split('_')[1])

            try:
                my_gpio.status = gpio.input(var)

            except Exception as error:
                print(error, 'bug recupération status gpio')
        db.session.commit()
    else:
        pass

# Configuration des GPIO ( mode Input ou Output) utilisé en base de donnée
# Configuration également des ds1820b
def init(gpio):
    print('init')

    # Déclaration des gpios disponible pour configuration
    gpios_start = helpers.getrevision()['gpio_for_init']

    # On passe tous les GPIO en mode Input
    for Gpiod in gpios_start:
        try:
            gpio.setup(int(Gpiod), gpio.IN,pull_up_down=gpio.PUD_DOWN)
        except Exception as e:
            print(e, 'erreur passage gpio en input dans la phase d\'initialisation')

    #get_status_gpio()
    # Initialisation des capteur ds1820b
    check_ds1820b()

    # on affecte le mode Input ou Output aux GPIO
    # en fonction de la configuration entrée en bdd
    datas = [(data.mode, data.valeur.split('_')[1]) for data in session.query(Gpio).all()]
    for gpios in datas:
        # GPIO en mode Input
        if gpios[0] == 'Input':
            try:
                gpio.setup(int(gpios[1]),gpio.IN,pull_up_down=gpio.PUD_DOWN)
            except Exception as e:
                print(e, 'erreur attribution gpio')
                #print('je ne suis pas sur un raspberry')

        # GPIO en mode Output avec mise à 1 de la sortie
        elif gpios[0] == 'Output':
            try:
                gpio.setup(int(gpios[1]), gpio.OUT)
                gpio.output(int(gpios[1]), True)
            except Exception as e:
                print(e,'je ne suis pas sur un rasberry', 'erreur in Init(gpio)')


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
        #globals()[appareil.nom].start(mdm, sonde, programmation, ordre,appareil)
        globals()[str(appareil.categorieappareil)+'_'+str(appareil.id)].start(mdm, sonde, programmation, ordre, appareil)
        #print('oki', appareil.nom, mdm, sonde, programmation, ordre)

    except Exception as error:
        print(error,'not way', appareil.nom, mdm, sonde, programmation, ordre)
    return [globals()[str(appareil.categorieappareil)+'_'+str(appareil.id)],appareil]


# liste des instances des appareils
def get_appareils():
    appareils = list()
    # liste des appareil enregistrés dan la base de donnée
    #list_appareil = session.query(Appareil).all()
    list_appareil = Appareil.query.all()
    status = Status.query.filter(Status.identifiant == 'reload_config').first()

    if status == None:
        status = Status()
        status.identifiant = 'reload_config'
        status.status = False
        session.add(status)
        session.commit()

    """if mod_dev:
        init(gpio=None)
    else:
        init(gpio)"""

    for appareil in list_appareil:
        try:


            # création des instances correspondant à la liste des apppareils en bdd
            globals()[str(appareil.categorieappareil)+'_'+str(appareil.id)] = globals()[appareil.categorieappareil](appareil)



            data = {appareil: globals()[str(appareil.categorieappareil)+'_'+str(appareil.id)]}
            appareils.append(data)

        except Exception as error:
            print(error, 'erreur mise en place instance appareil')

    # renvoie de la liste des instances
    return appareils

def get_composants():
    #composants = list()
    # liste des appareil enregistrés dan la base de donnée
    list_composant = session.query(Composant).all()


    # On vérifie si la configuration a été modifié par l'ajout ou la suppression d'un appareil
    # si oui, on déclare/ recharge la nouvelle configuration
    status = Status.query.filter(Status.identifiant == 'reload_config').first()
    if status == None:
        status = Status()
        status.identifiant = 'reload_config'
    status.status = False
    session.commit()

    # Mise en place en premier des instances compteurs
    compteurs_list = [(compteur.compteur_id) for compteur in list_composant if compteur.compteur]

    for data_instance in compteurs_list:
        globals()['Compteurs_' + str(data_instance.id)] = globals()['Compteurs'](data_instance)

    # Ensuite mise en place des composants avec éventuellement des compteurs rattaché
    composants_list = [(composant) for composant in list_composant]
    for composant in composants_list:
        try:
            # création des instances correspondant à la liste des apppareils en bdd
            globals()[str(composant.categoriecomposant)+'_'+str(composant.id)] = globals()[composant.categoriecomposant](composant)
            data = {composant: globals()[composant.categoriecomposant]}

            # Attributiopn d'un conmpteur au composant
            if globals()[str(composant.categoriecomposant)+'_'+str(composant.id)].compteur :
                instance_compteur = globals()['Compteurs_'+str(composant.compteur_id.id)]
                globals()[str(composant.categoriecomposant)+'_'+str(composant.id)].compteur_id = instance_compteur
                print(f'Attribution du compteur { instance_compteur } au composant { data }')

            #composants.append(data)

        except Exception as e:
            print(e, 'L335 erreur mise en place instance appareil')

    return None #composants


async def start(gpio):
    print('l369')

    if init(gpio):

        # Configuration des bcm
        helpers.configBcm()
        # Gestion de la mise à jour température sonde
        step = 60*5
        #top = time.time()+step
        print('init oki')
        ###################### test

        appareils= get_appareils()


        while True:
            status_gpio()
            status = Status.query.filter(Status.identifiant == 'reload_config').first()
            if status == None:
                status = Status()
                status.identifiant = 'reload_config'
                status.status = True
                db.session.add(status)
                db.session.commit()

            status_run = Status.query.filter(Status.identifiant == 'mode_run').first()
            if status_run == None:
                status_run = Status()
                status_run.identifiant = 'mode_run'
                status_run.status = False
                db.session.add(status_run)
                db.session.commit()


            # récupération instance db de composant débimètre



            ## fin test
            helpers.read_status()
            if status_run.status:
                #print(globals()['Compteurs_64'].composant_test.valeur)
                if status.status:
                    init(gpio)
                    appareils = get_appareils()
                    print('l379')
                    get_composants()
                    print('get_appareil() && get_composants()')

                for appareil in appareils:

                    # Ici en récupère le modèle de l'appareil (bdd pour key) et l'instance 'physique' interagissant avec les les GPIO (pour value)
                    for key, value in appareil.items():
                        try:
                            if key.composants:
                                composant_key = globals()[str(key.composants.categoriecomposant) + '_' + str(key.composants.id)]
                                value.composant_id = composant_key
                            get_mdm(key)
                            value.valeurs = key
                            value.getComposants()
                            key.valeur_id = value.valeurs_model
                            key.sortie = value.current
                            db.session.add(key)
                        except Exception as error:
                            print(error,'bug L451')
                session.commit()

            else:
                print('not run')
                helpers.run_manuel()
            # Enregisrement de temps courant en bdd
            helpers.update_time()
            #print(globals()['Pompe_90'].composant_id.testa)
            await asyncio.sleep(1,result=True)
    else:
        print('init not good')

async def main(gpio):

    get_composants()

    try:
        # Mise en place instance compteurs
        compteurs = Compteur.query.all()
        mycounts = list()
        try:
            for data in compteurs:
                mycounts.append((Compteurs(data).start(globals()[data.composant_id[0].categoriecomposant+'_'+str(data.composant_id[0].id)])))
        except Exception as error:
            print("error L420",error)
        # Mise en place des composants
        composants = Composant.query.filter_by(compteur=None).all()
        mycomposant_instance = list()

        try:
            for composant in composants:
                mycomposant_instance.append(globals()[str(composant.categoriecomposant)+'_'+str(composant.id)].toto())
        except Exception as error:
            print('erreur L427',error)

        await asyncio.gather(start(gpio), updateValeurDs1820(),*mycounts,*mycomposant_instance)

        tache1 = asyncio.create_task(start(gpio))
        tache2 = asyncio.create_task(updateValeurDs1820())


        await tache2
        await tache1

        try:
            for task in compteurs:
                        await asyncio.create_task(Compteurs(task).start(globals()[task.composant_id[0].categoriecomposant+'_'+str(task.composant_id[0].id)]))
        except Exception as error:
            print('error L442',error)

        try:
            for task1 in mycomposant_instance:
                await asyncio.create_task(task1)
        except Exception as error:
            print('error L448',error)

    except Exception as error:
        print("error main",error)

# Configuration par defaut gpio


if mod_dev:
    asyncio.run(main(None))

else:
    #asyncio.run(start(gpio))
    asyncio.run(main(gpio))

