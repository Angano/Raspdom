from config import db
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin
import time, datetime
from flask import jsonify
#from sqlalchemy.dialects.mysql import TIME


composants = db.Table('composants',
                      db.Column('composant_id',db.Integer, db.ForeignKey('composant.id'),primary_key=True),
                      db.Column('appareil_id',db.Integer,db.ForeignKey('appareil.id'),primary_key=True))

tempos = db.Table('tempos',
                      db.Column('tempo_id',db.Integer, db.ForeignKey('tempo.id'),primary_key=True),
                      db.Column('appareil_id',db.Integer,db.ForeignKey('appareil.id'),primary_key=True))

historiques = db.Table('historiques',
                      db.Column('historique_id',db.Integer, db.ForeignKey('historique.id'),primary_key=True),
                      db.Column('sonde_id',db.Integer,db.ForeignKey('sonde.id'),primary_key=True))


historiquescomposant = db.Table('historiquescomposant',
                      db.Column('historiquecomposant_id',db.Integer, db.ForeignKey('historiquecomposant.id'),primary_key=True),
                      db.Column('composant_id',db.Integer,db.ForeignKey('composant.id'),primary_key=True))

messages = db.Table('messages',
                      db.Column('message_id',db.Integer, db.ForeignKey('message.id'),primary_key=True),
                      db.Column('appareil_id',db.Integer,db.ForeignKey('appareil.id'),primary_key=True))


class Appareil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    description = db.Column(db.String(200))
    categorieappareil = db.Column(db.String(200), nullable=True)
    sortie = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    gpios = db.relationship('Gpio', backref='appareil', lazy=True)
    order_gpio = db.Column(db.String(200))
    nbre_gpio = db.Column(db.Integer)
    programmations = db.relationship('Programmation', backref='appareil_programmation', lazy=True, order_by='Programmation.day.asc(),Programmation.start.asc()')
    mode_de_marche = db.relationship('ModeDeMarche',  uselist=False,  backref='appareil_mode_de_marche', lazy=True)
    auto = db.relationship('Auto', uselist=False, backref='appareil_auto', lazy=True)
    sonde_id = db.Column(db.Integer, db.ForeignKey('sonde.id'))
    #sonde = db.relationship('Sonde', uselist=False, backref='appareil_sonde', lazy=True)
    manuel = db.relationship('Manuel', uselist=False, backref='appareil_ordre', lazy=True)
    label = db.Column(db.String(250))
    sonde_actived = db.Column(db.Boolean,default=False, nullable=False)
    min = db.Column(db.Float(),default=17.0)
    max = db.Column(db.Float(),default=19.0)
    consigne = db.Column(db.Float(), nullable=True)
    #mf = db.Column(db.Integer, db.ForeignKey('mf.id'), nullable=True)
    mf = db.relationship('Mf',  cascade="delete",uselist=False, backref='app_mf', lazy=True)
    #composants = db.Column(db.Integer, db.ForeignKey('composant.id'), nullable=True)
    #composants = db.relationship('Composant',secondary=composants,lazy='subquery', backref=db.backref('appareils',lazy=True))

    composants = db.relationship('Composant',uselist=False, secondary='composants', lazy='subquery', backref=db.backref('appareils', lazy=True))

    valeur_id = db.relationship('Valeur', lazy=True, backref="toto", cascade="all, delete-orphan")

    tempos = db.relationship('Tempo', uselist=False, secondary='tempos', lazy='subquery',
                                 backref=db.backref('appareils', lazy=True))

    messages_app = db.relationship('Message',secondary='messages',backref='maurice', order_by="Message.recorded_at.desc()")
    def get_appareil(self):
        return self.query.all()
    
    def get_programmations(self):
        time_now = Status.query.filter_by(identifiant='now_time').first().time_now

        compare_time = datetime.time(hour=time_now.hour, minute=time_now.minute, second=time_now.second)

        try:
            programmations = self.programmations


            for programmation in programmations:

                start = programmation.start
                end = programmation.end
                if compare_time>=start and compare_time<end and time_now.weekday()==programmation.day-1:
                    return True
            return False
                    
        except Exception as error:
            return 'bug'+str(error)

class Historique(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    valeur = db.Column(db.Float())
    record_at = db.Column(db.DateTime())
    histo = db.relationship('Sonde', uselist=False, secondary='historiques', lazy='subquery',
                                  backref=db.backref('historiques', lazy=True))
class Sonde(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    min = db.Column(db.Float(),default=17.0)
    max = db.Column(db.Float(),default=19.0)
    unite = db.Column(db.String(20), default='')
    present = db.Column(db.Boolean(),default=False)
    appareil = db.relationship('Appareil', backref='appareil_sonde', lazy=True)
    en_service = db.Column(db.Boolean(), default=False)
    info = db.Column(db.String(200))
    chemin = db.Column(db.String(200))
    type_sonde = db.Column(db.String(20))
    #sonde_id = db.relationship('Sonde', backref='sonde_appareil', uselist=False, lazy=True, cascade="delete")
    sonde_valeur_id = db.relationship('ValeurSonde', backref='sonde_valeur', uselist=False, lazy=True, cascade="delete")
    #historique_sonde = db.relationship('Historique', backref='histo_sonde', uselist=False, lazy=True, cascade="delete")



class ValeurSonde(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valeur = db.Column(db.Float())
    sonde_id = db.Column(db.Integer, db.ForeignKey('sonde.id'), nullable=False)

class ModeDeMarche(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appareil_id = db.Column(db.Integer,db.ForeignKey('appareil.id'), nullable=False)
    mode_de_marche = db.Column(db.String(200), default='off')


class Auto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'))
    start = db.Column(db.Boolean(), default=False)


class Manuel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'))
    ordre = db.Column(db.String(100))


class Gpio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    mode = db.Column(db.String(10))
    valeur = db.Column(db.String(10))
    info = db.Column(db.String(200))
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True, default=None)
    #composant_id = db.Column(db.Integer, db.ForeignKey('composant.id'), nullable=True, default='')
    #gpiobcm_id = db.Column(db.Integer, db.ForeignKey('gpiobcm.id'), nullable=False, default='')
    configbcm_used_in = db.Column(db.Integer, db.ForeignKey('config_bcm.id'), nullable=False, default='')
    status = db.Column(db.Boolean,default=False)
    
    # get choice of gpio free with gpio select for instance
    def get_free_gpio(self):
        # gpio réservés
        relais = [12,17,18,22,23,24,25,27]
        reserve = [2,3,4,5,6,7,8,13,16,19,20,21,26]
        input = [9,10,11]

        try:
            gpio = self.valeur.split('_')[1]
        except:
            gpio = None
        gpio_used = [(int(data.valeur.split('_')[1])) for data in Gpio.query.all()]
        try:
            gpio_used.remove(int(gpio))

        except:
            pass

        tab = []
        dati = list()
        dati.append('')
        dati.append('Select')
        tab.append(dati)
        for i in range(0, 27):
            if i not in gpio_used:
                data = list()
                data.append('Gpio_'+str(i))
                data.append('Gpio_'+str(i))
                tab.append(data)

        return tab


class GpioBcm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    mode = db.Column(db.String(10), default='Input')
    status = db.Column(db.Boolean, default=False)
    #gpios = db.relationship('Gpio', backref='gpiobcm', lazy=True)


class CategorieCapteur(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    nom = db.Column(db.String(200))
    description = db.Column(db.String(200))
    image = db.Column(db.String(200), nullable=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(200))
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))


    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Programmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Time())
    end = db.Column(db.Time())
    day = db.Column(db.Integer())
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True)

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean(), default=False)
    identifiant = db.Column(db.String(200))
    valeur = db.Column(db.Float())
    time_now = db.Column(db.DateTime())

class Mf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debut = db.Column(db.DateTime())
    fin = db.Column(db.DateTime())
    appareil_mf = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True)
    actived = db.Column(db.Boolean(),default=False)


class Composant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modele = db.Column(db.String(200))
    description = db.Column(db.String(200))
    emplacement = db.Column(db.String(200))
    #gpios = db.relationship('Gpio', backref='composant', lazy=True,cascade="all,delete",)
    order_gpio = db.Column(db.String(200))
    nbre_gpio = db.Column(db.Integer)
    categoriecomposant = db.Column(db.String(200), nullable=True)
    sortie = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(200), nullable=True)
    valeur = db.Column(db.Float())
    unite = db.Column(db.String(20))
    valeur2 = db.Column(db.Float())
    unite2 = db.Column(db.String(20))
    #appareils = db.relationship('Appareil', backref='composant_appareil', lazy=True )
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True)
    valeur_id = db.relationship('Valeur', lazy=True, backref="titi")
    valeur_id2 = db.relationship('Valeur', lazy=True, backref="titi2")
    compteur = db.Column(db.Integer,db.ForeignKey('compteur.id'), nullable=True, default=None)
    compteur_id = db.relationship('Compteur', cascade="delete", backref="compteur_id", lazy=True)

    def get_historique_for_api(self,start=None,end=None):
        time_now = Status.query.filter_by(identifiant='now_time').first().time_now

        # test
        '''SELECT date(t1.record_at),hour(t1.record_at), AVG(t1.valeur)
            FROM historiquecomposant t1
            GROUP BY date(t1.record_at), hour(t1.record_at)'''

        # temperatures pour les sondes
        """SELECT date(historique.record_at),hour(historique.record_at), AVG(historique.valeur)
        from historique
        INNER join historiques on historique.id = historiques.historique_id
        where historiques.sonde_id = 1
        GROUP BY date(historique.record_at), hour(historique.record_at)"""

        if start == None:
            start = str(time_now.year) + '-' + str(time_now.month) + '-' + str(time_now.day)

        if end == None:
            end = time_now+datetime.timedelta(days=1)
            end = str(end.year)+'-'+str(end.month)+'-'+str(end.day)
        print(start,end)
        try:
            # histo_test = Historiquecomposant.query.filter(Historiquecomposant.histo.has(histo=self.id)).filter(Historiquecomposant.record_at.between('2023-10-13','2023-10-14')).all()
            histo_test = Historiquecomposant.query.filter(Historiquecomposant.histo.has(id=self.id)).filter(Historiquecomposant.record_at.between(start,end)).all()
            print(histo_test)
        except Exception as err:
            print(err)
            pass

        # fin test

        datas = {}
        datas['valeur2'] = list()
        datas['valeur1'] = list()
        datas['recorded_at'] = list()
        datas['unite1'] = self.unite
        datas['unite2'] = self.unite2
        datas['description'] = self.description
        datas['categorie'] = self.categoriecomposant
        datas['composant_id'] = self.id
        datas['emplacement'] = self.emplacement
        datas['modele'] = self.modele

        historiques_datas = histo_test
        for data in historiques_datas:
            datas['recorded_at'].append(data.record_at)
            if data.valeur is None or data.valeur > 100:
                datas['valeur1'].append(100)
            else:
                datas['valeur1'].append(data.valeur)

            if data.valeur2 is None or data.valeur2 > 100:
                datas['valeur2'].append(100)
            else:
                datas['valeur2'].append(data.valeur2)

        return datas


class Historiquecomposant(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    valeur = db.Column(db.Float())
    unite = db.Column(db.String(200))
    valeur2 = db.Column(db.Float())
    unite2 = db.Column(db.String(200))
    record_at = db.Column(db.DateTime())
    histo = db.relationship('Composant', uselist=False, secondary='historiquescomposant', lazy='subquery',
                                  backref=db.backref('historiquescomposant', lazy=True))

class ConfigBcm(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    pin = db.Column(db.Integer)
    name = db.Column(db.String(200))
    alt_fct = db.Column(db.Boolean(),default=False)
    alt_fct_name = db.Column(db.String(200))
    alt_fct_0 = db.Column(db.String(200))
    alt_fct_1 = db.Column(db.String(200))
    alt_fct_2 = db.Column(db.String(200))
    alt_fct_3 = db.Column(db.String(200))
    alt_fct_4 = db.Column(db.String(200))
    alt_fct_5 = db.Column(db.String(200))
    alt_fct_name_other = db.Column(db.String(200))
    class1 = db.Column(db.String(200))
    class2 = db.Column(db.String(200))
    bus = db.Column(db.String(200))
    mode = db.Column(db.String(200),default="", nullable=True)
    used_in = db.relationship('Gpio', backref='gpio_user_in', lazy=True )
    bus_id = db.Column(db.Integer,db.ForeignKey('bus.id'), nullable=True, default=None)
    gpio = db.relationship('Compteur', backref="configbcm_compteur", lazy=True)
    read_status = db.Column(db.Boolean(),default=False, nullable=True)
    write_status = db.Column(db.Boolean(),default=False, nullable=True)

class Bus(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    actived = db.Column(db.Boolean(), default=False)
    name = db.Column(db.String(200))
    gpio = db.relationship('ConfigBcm',backref="configbcm_bus",lazy=True)


class Compteur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actived = db.Column(db.Boolean(), default=False)
    name = db.Column(db.String(200))
    valeur = db.Column(db.Integer,nullable=True, default=0)
    moyenne = db.Column(db.Float, nullable=True, default=0)
    configbcm_id = db.Column(db.Integer, db.ForeignKey('config_bcm.id'), nullable=True, default=None)
    categoriecomposant = db.Column(db.String(200), nullable=True)
    composant_id = db.relationship('Composant', cascade="delete",backref="totor", lazy=True)



class Valeur(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    val = db.Column(db.Float())
    composant_id = db.Column(db.Integer, db.ForeignKey('composant.id'),nullable=False)
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'),nullable=False)
    min = db.Column(db.Float())
    consigne = db.Column(db.Float())
    max = db.Column(db.Float())
    actived = db.Column(db.Boolean())
    valeur_cumule = db.Column(db.Float())
    unite = db.Column(db.String(10))
    init = db.Column(db.Boolean())


class Tempo(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    consigne = db.Column(db.Float())
    start_at = db.Column(db.DateTime())

    start = db.Column(db.Boolean(),default=False, nullable=False)
    finish = db.Column(db.Boolean(),default=False, nullable=False)

class Message(db.Model):
    id =db.Column(db.Integer(), primary_key=True)
    message = db.Column(db.Text())
    type = db.Column(db.String(200), nullable=True,default=None)
    appareil = db.relationship('Appareil', uselist=False, secondary='messages', lazy='subquery',
                                  backref=db.backref('messages', lazy=True))
    recorded_at = db.Column(db.DateTime())


