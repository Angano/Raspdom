from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, SelectField, SelectMultipleField, DecimalField,\
    IntegerField, FieldList, FormField, BooleanField

import Appareils
from models import Gpio, Sonde

import sys, inspect


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
    nom = StringField()
    mode = StringField(render_kw={'readonly': True})
    valeur = SelectField(choices=[], validate_choice=False,render_kw={'data-select':'gpio'})
    #appareils = SelectField(validate_choice=False, choices=action.get_appareil(), default='')
    info = StringField(render_kw={'readonly': True})

    def __init__(self, *args, **kwargs):
        super(GpioForm, self).__init__(*args, **kwargs)
        gpio = Gpio()
        self.valeur.choices = gpio.get_free_gpio()



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
    choices2 = [(data.id,data.nom) for data in Sonde.query.all()]
    for name, obj in inspect.getmembers(Appareils):

        if inspect.isclass(obj) :
            try:
                if obj.label.__doc__ != None:
                    choices.append((obj.__name__,obj.label.__doc__))
            except:
                print('no label')
    categorieappareil = SelectField(choices=choices)
    nom = StringField()
    description = StringField()
    gpios = FieldList(FormField(GpioForm))
    #sondes = FieldList(FormField(SondeForm))
    sonde = SelectField(choices=choices2,validate_choice=False)
    sonde_actived = BooleanField()
    min = DecimalField(render_kw={'style': 'width: 50px'})
    max = DecimalField(render_kw={'style': 'width: 50px'})

class App2Form(FlaskForm):

    choices2 = [(data.id, data.nom) for data in Sonde.query.all()]
    nom = StringField()
    description = StringField()
    # sondes = FieldList(FormField(SondeForm))
    sonde = SelectField(choices=choices2, validate_choice=False)
    sonde_actived = BooleanField()


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

    start = SelectField(choices=choices_hours)
    start_min = SelectField(choices=choices_min)
    end = SelectField(choices=choices_hours)
    end_min = SelectField(choices=choices_min)
    day = SelectField(choices=choices_day)
    appareil = SelectField(validate_choice=False)


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

