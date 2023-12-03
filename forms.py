import time

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, SelectMultipleField, DecimalField,\
    IntegerField, FieldList, FormField, BooleanField, HiddenField, TimeField, DateTimeField, FloatField

import Appareils, Composants
from models import Gpio, Sonde, Composant, ConfigBcm

import sys, inspect
import datetime


class UserForm(FlaskForm):
    username = StringField()
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    password = PasswordField(validators=[
        validators.EqualTo(
            "verif_password",
            message="Les mots de passe ne correspondent pas"
            )
        ])
    verif_password = PasswordField(label="Confirm password")


class LoginForm(FlaskForm):
    username = StringField()
    password = PasswordField()


class EditUserForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    email = StringField()


class ModeDeMarcheForm(FlaskForm):
    choices = [('off','Off'), ('manu', 'Manu'), ('auto', 'Auto'), ('prog', 'Programmation')]
    mode_de_marche = SelectField('Mode de Marche', choices=choices)


class GpioForm(FlaskForm):
    nom = HiddenField(render_kw={'value':''})
    mode = StringField(render_kw={'class':' md-input','readonly': True, 'class':'md-input', "style":"background-color:transparent"})
    valeur = SelectField(choices=[], validate_choice=False,render_kw={'class':'form-select','data-select':'gpio'})
    #appareils = SelectField(validate_choice=False, choices=action.get_appareil(), default='')
    info = StringField(render_kw={'class':'md-input','readonly': True,"style":"display:inline-block;background-color:transparent"})

    def __init__(self, *args, **kwargs):
        output = [(data.name.split('_')[1],data.alt_fct_name_other) for data in ConfigBcm.query.filter(ConfigBcm.name.like('%Gpio_%')).filter_by(alt_fct=0,mode='Output').all() ]
        reserve = [2, 3, 4, 10,9,11,19,8,7,16,20,21]
        input = [(data.name.split('_')[1]) for data in ConfigBcm.query.filter(ConfigBcm.name.like('%Gpio_%')).filter_by(alt_fct=0,mode='Input').all() ]

        #input = [13,9, 10, 11,5]

        gpios = [ (gpio.valeur) for gpio in Gpio.query.all()]
        super(GpioForm, self).__init__(*args, **kwargs)

        if self.mode.data == 'Input':
            self.valeur.choices = [('Gpio_' + str(data)) for data in input if 'Gpio_' + str(data) not in gpios ]

        if self.mode.data == 'Output':
            self.valeur.choices = [('Gpio_' + str(data[0]),'Gpio_' + str(data[0]+' '+str(data[1]))) for data in output if 'Gpio_' + str(data[0]) not in gpios]

        # gpio = Gpio()
        #self.valeur.choices = gpio.get_free_gpio()


class SondeForm(FlaskForm):
    choices = [('deg','T°c'),('cm','Cm')]

    min = DecimalField(render_kw={'style': 'width: 50px'},default=18.0)
    max = DecimalField(render_kw={'style': 'width: 50px',},default =19.0)
    unite = SelectField(choices=choices)
    en_service = BooleanField()
    capteur = SelectField()


    def __init__(self, *args, **kwargs):
        super(SondeForm, self).__init__(*args, **kwargs)
        self.capteur.choices = [(data.id,data.info) for data in Sonde.query.all()]


class ReglageSondeForm(FlaskForm):
    choices = [('deg','T°c'),('cm','Cm')]
    min = DecimalField(render_kw={'style': 'width: 50px'})
    max = DecimalField(render_kw={'style': 'width: 50px'})
    unite = SelectField(choices=choices)
    en_service = BooleanField()


class AppareilForm(FlaskForm):
    choices = list()


    try:
        choices3 = [(data.id,data.emplacement) for data in Composant.query.all()]
    except:
        choices3 = []

    for name, obj in inspect.getmembers(Appareils):

        if inspect.isclass(obj) :
            try:
                if obj.label.__doc__ != None and obj.enable==True:
                    choices.append((obj.__name__,obj.label.__doc__))
            except:
                print('no label')

    categorieappareil = SelectField(choices=choices, validate_choice=False)
    nom = StringField()
    description = StringField()
    gpios = FieldList(FormField(GpioForm))
    #sondes = FieldList(FormField(SondeForm))
    sonde_id = SelectField(validate_choice=False,coerce=int)
    sonde_actived = BooleanField()
    min = DecimalField(render_kw={'style': 'width: 50px'})
    max = DecimalField(render_kw={'style': 'width: 50px'})
    composants = SelectField(choices=choices3,validate_choice=False)

    def __init__(self, *args, **kwargs):
        try:
            choices2 = [(data.id, data.info) for data in Sonde.query.all()]
            choices2.insert(0, (0, 'Aucune'))
        except:
            choices2 = []
        super(AppareilForm, self).__init__(*args, **kwargs)
        self.sonde_id.choices = choices2


class App2Form(FlaskForm):
    nom = StringField()
    description = StringField()
    # sondes = FieldList(FormField(SondeForm))
    sonde_id = SelectField(validate_choice=False)
    sonde_actived = BooleanField()

    def __init__(self, *args, **kwargs):
        try:
            choices2 = [(data.id, data.info) for data in Sonde.query.all()]
        except:
            choices2 = []
        super(App2Form, self).__init__(*args, **kwargs)
        self.sonde_id.choices = choices2


class Ds1820bForm(FlaskForm):
    #nom = StringField(render_kw={'readonly':'readonly'})
    present = BooleanField()
    info = StringField()
    en_service = BooleanField()


class ProgrammationForm(FlaskForm):
    choices_day = [(1, 'Lundi'), (2, 'Mardi'), (3, 'Mercredi'), (4, 'Jeudi'), (5, 'Vendredi'), (6, 'Samedi'),
                   (7, 'Dimanche')]
    choices_min = [data for data in range(0,60,1)]
    choices_hours = [data for data in range(0,24)]


    day = SelectField(choices=choices_day)
    start = TimeField(default=datetime.time())
    end = TimeField(default=datetime.time())
    appareil_id = SelectField(validate_choice=False)


class CategorieAppareilForm(FlaskForm):
    choices = list()

    for name, obj in inspect.getmembers(Appareils):

        if inspect.isclass(obj):
            try:
                choices.append((name,obj.label.__doc__))
            except:
                print('no label')
    nom = StringField()
    nbre_entre = IntegerField()
    nbre_sortie = IntegerField()
    appareils = SelectField('Modède d\'appareil', choices=choices)

###---- Composant ---###
class ComposantForm(FlaskForm):
    choices = list()

    for name, obj in inspect.getmembers(Composants):

        if inspect.isclass(obj):
            try:
                choices.append((name, obj.label.__doc__))
            except:
                print('no label')
    modele = StringField(render_kw={'readonly':'readonly'})
    description = StringField(render_kw={'readonly':'readonly'})
    gpios = FieldList(FormField(GpioForm))
    categoriecomposant = SelectField('Modède d\'appareil', choices=choices)
    emplacement = StringField()

class CompteurForm(FlaskForm):
    try:
        choices = [(data.id,data.name+' '+data.alt_fct_name) for data in ConfigBcm.query.filter_by(mode='Input').all()]
    except:
        choices = []
    actived = BooleanField(render_kw={'value':1})
    name = StringField()
    configbcm_id = SelectField(choices=choices,validate_choice=False)


class Composant2Form(FlaskForm):
    gpios = FieldList(FormField(GpioForm))
    categoriecomposant = StringField(render_kw={'readonly':'readonly'})
    emplacement = StringField()
    compteur = FieldList(FormField(CompteurForm))



class CompteurComposantForm(FlaskForm):
    choices = []
    compteur = SelectField(choices=choices,validate_choice=False)
    gpios = FieldList(FormField(GpioForm))

class CompteurComposant2Form(FlaskForm):
    choices = []
    compteur = SelectField(choices=choices,validate_choice=False)
    gpios = FieldList(FormField(CompteurComposantForm))


class TempoForm(FlaskForm):
    consigne = FloatField()
    start_at = DateTimeField()