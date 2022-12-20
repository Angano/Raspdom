from config import db
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_login import UserMixin
import time, datetime


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
    programmations = db.relationship('Programmation', backref='appareil_programmation', lazy=True)
    mode_de_marche = db.relationship('ModeDeMarche',  uselist=False,  backref='appareil_mode_de_marche', lazy=True)
    auto = db.relationship('Auto', uselist=False, backref='appareil_auto', lazy=True)
    sonde_id = db.Column(db.Integer, db.ForeignKey('sonde.id'))
    sonde = db.relationship('Sonde', uselist=False, backref='appareil_sonde', lazy=True)
    manuel = db.relationship('Manuel', uselist=False, backref='appareil_ordre', lazy=True)
    label = db.Column(db.String(250))
    sonde_actived = db.Column(db.Boolean,default=False, nullable=False)
    #mf = db.Column(db.Integer, db.ForeignKey('mf.id'), nullable=True)
    mf = db.relationship('Mf',  cascade="delete",uselist=False, backref='app_mf', lazy=True)

    def get_appareil(self):
        return self.query.all()
    
    def get_programmations(self):
        try:
            programmations = self.programmations
            top_time = time.localtime().tm_hour * 24 + time.localtime().tm_min
            for programmation in programmations:
                start = programmation.start*24+programmation.start_min
                end = programmation.end*24+programmation.end_min
                if top_time>=start and top_time<end:
                    return True
            return False
                    
        except:
            return False


class Sonde(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200))
    min = db.Column(db.Float())
    max = db.Column(db.Float())
    unite = db.Column(db.String(20), default='')
    present = db.Column(db.Boolean(),default=False)
    appareil = db.relationship('Appareil', backref='appareil_sonde', lazy=True)
    en_service = db.Column(db.Boolean(), default=False)
    info = db.Column(db.String(200))
    chemin = db.Column(db.String(200))
    type_sonde = db.Column(db.String(20))
    #sonde_id = db.relationship('Sonde', backref='sonde_appareil', uselist=False, lazy=True, cascade="delete")
    sonde_valeur_id = db.relationship('ValeurSonde', backref='sonde_valeur', uselist=False, lazy=True, cascade="delete")


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
    appareil_id = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True, default='')
    #gpiobcm_id = db.Column(db.Integer, db.ForeignKey('gpiobcm.id'), nullable=False, default='')
    
    # get choice of gpio free with gpio select for instance
    def get_free_gpio(self):

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
    start = db.Column(db.Integer)
    start_min = db.Column(db.Integer)
    end = db.Column(db.Integer)
    end_min = db.Column(db.Integer)
    day = db.Column(db.Integer)
    appareil = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True)


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean(), default=False)

class Mf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debut = db.Column(db.DateTime())
    fin = db.Column(db.DateTime())
    appareil_mf = db.Column(db.Integer, db.ForeignKey('appareil.id'), nullable=True)
    actived = db.Column(db.Boolean(),default=False)