import json
from datetime import datetime
import os

from config import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_required, login_user, \
                        logout_user, current_user

from forms import UserForm, LoginForm, EditUserForm, AppareilForm, GpioForm, ProgrammationForm, ModeDeMarcheForm, SondeForm, Ds1820bForm, ReglageSondeForm
from models import User, Appareil, Gpio, Programmation, ModeDeMarche, Sonde, Manuel, Status, ValeurSonde
from Appareils import Eclairage, ChauffageR, ChauffeEau

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# recharchement liste des appareils
def reload():
    status = Status.query.get(1)
    if status == None:
        status = Status()
    status.status = True
    db.session.add(status)
    db.session.commit()
    return  True

@login_manager.user_loader
def user_load(user_id):
    return User.query.get(user_id)


@app.route('/')
@login_required
def index():
    appareils = Appareil.query.all()
    # Récupération des instances des appareils en cours
    labels = dict()
    instances = list()
    #labels = [(data.categorieappareil, globals()[data.categorieappareil].label.__doc__) for data in appareils]
    for appareil in appareils:
        instances.append({'modelAppareil':appareil,'instanceAppareil':(globals()[appareil.categorieappareil])})

    gpios = Gpio.query.order_by('appareil_id').all()
    programmations = Programmation.query.order_by('appareil').all()

    return render_template('index.html', appareils=appareils, gpios=gpios, programmations=programmations, instances=instances)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash(message='Vous êtes déjà conecté')
        return redirect(url_for('index'))

    loginform = LoginForm(request.form)
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user and user.check_password(loginform.password.data):
            login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', loginform=loginform)


@app.route('/profil')
@login_required
def profil():
    return render_template('profil.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user', methods=['POST', 'GET'])
def user():
    userform = UserForm(request.form)
    if userform.validate_on_submit():
        user = User()
        userform.populate_obj(user)
        user.hash_password(userform.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('user.html', userform=userform)


@app.route('/user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    userform = EditUserForm(obj=user, data=request.form)
    if userform.validate_on_submit():
        userform.populate_obj(user)
        db.session.add(user)
        return redirect(url_for('users'))
    return render_template('edit_user.html', userform=userform)


@app.route('/users')
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/user/delete/<int:user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))


# appareil
@app.route('/appareil', methods=['POST', 'GET'])
def appareil():
    appareilform = AppareilForm(request.form)
    mode_de_marcheform = ModeDeMarcheForm(request.form)

    if appareilform.validate_on_submit():
        appareil = Appareil()
        mode_de_marche = ModeDeMarche()
        appareilform.populate_obj(appareil)
        mode_de_marcheform.populate_obj(mode_de_marche)
        print(appareilform.categorieappareil.data)

        try :
            instance_appareil = globals()[appareilform.categorieappareil.data]
            appareil.nbre_gpio = instance_appareil.sortie+instance_appareil.entre

        except ValueError:
            print(ValueError)
        appareil.label = instance_appareil.label.__doc__
        db.session.add(appareil)
        db.session.commit()

        mode_de_marche.appareil_id=appareil.id
        db.session.add(mode_de_marche)
        db.session.commit()

        return redirect(url_for('edit_appareil', appareil_id=appareil.id))
    
    #appareilform.categorie_appareil_id.choices = [(data.id, data.nom) for data in Categorieappareil.query.all()]
    return render_template('appareil/appareil.html', appareilform=appareilform, mode_de_marcheform=mode_de_marcheform)


@app.route('/appareil/<int:appareil_id>', methods=['POST','GET'])
def edit_appareil(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    appareilform = AppareilForm(obj=appareil, data=request.form)
    gpios = Gpio.query.order_by('mode','nom').all()

    print(appareilform.choices)
    for data in appareilform.gpios.data:
        print(data['valeur'])
        print(data)
    # appareil depuis Appareil.py
    instance_appareil = globals()[appareil.categorieappareil](appareil)

    if appareilform.validate_on_submit():

        if instance_appareil.sonde:
            sonde = Sonde.query.get(int((appareilform.sondes.data)[0]['capteur']))
            if sonde is None:
                sonde = Sonde()
                sonde.appareil_id = appareil_id
            data = (appareilform.sondes.data)[0]

            sonde.appareil_id = appareil.id
            sonde.min = data['min']
            sonde.max = data['max']
            sonde.en_service = data['en_service']
            sonde.unite = data['unite']

            db.session.add(sonde)
            db.session.commit()
            appareil.sonde_id = sonde.id

        appareil.nom = appareilform.nom.data
        appareil.categorieappareil = appareilform.categorieappareil.data
        appareil.description = appareilform.description.data
        appareil.sonde_actived = appareilform.sonde_actived.data
        #appareil.mode_de_marche = appareilform.mode_de_marche.data
        gpios_delete = Gpio.query.filter_by(appareil_id=appareil_id).all()
        gpios_order = list()
        if appareil.sonde_id:
            gpios_order.append('ds1820_'+str(sonde.id))
        for data in gpios_delete:
            db.session.delete(data)
            db.session.commit()
        for data in appareilform.gpios.data:
            gpioform = GpioForm()

            gpioform.nom.data = data['nom']
            gpioform.mode.data = data['mode']
            gpioform.valeur.data = data['valeur']
            gpioform.info.data = data['info']
            gpio = Gpio()
            gpios_order.append(data['valeur'])
            gpio.appareil_id = appareil_id
            if gpioform.validate_on_submit():

                gpioform.populate_obj(gpio)
                db.session.add(gpio)


        appareil.order_gpio = json.dumps(gpios_order)

        db.session.add(appareil)
        db.session.commit()

        if reload():
            print('reload')

        return redirect(url_for('appareils'))
    else:
        print(appareilform.errors)

    appareilform = AppareilForm(obj=appareil, data=request.form)

    #gpio_free = Gpio()
    #gpio_free = gpio_free.get_free_gpio()

    if not appareilform.gpios:
        if not instance_appareil.sonde:
            for i in range(instance_appareil.entre):
                gpioform = GpioForm()
                gpioform.mode = 'Input'

                gpioform.nom = ''

                try:
                    gpioform.info = instance_appareil.infos_entre[i]
                except:
                    gpioform.info = ''
                appareilform.gpios.append_entry(gpioform)

        for i in range(instance_appareil.sortie):
            gpioform = GpioForm()
            gpioform.mode = 'Output'
            gpioform.nom=''

            try:
                gpioform.info = instance_appareil.infos_sortie[i]
            except:
                gpioform.info = ''
            appareilform.gpios.append_entry(gpioform)


    if instance_appareil.sonde:

        #sonde = Sonde.query.filter_by(appareil_id=appareil.id).first()
        sonde = appareil.sonde
        if sonde is None:
            sonde = Sonde()

        if appareilform.sondes.__len__()<1:
            sondeform = SondeForm(obj=sonde)

            sondeform.unite = sonde.unite
            sondeform.min = sonde.min
            sondeform.max = sonde.max
            sondeform.en_service = sonde.en_service
            sondeform.type_sonde = sonde.type_sonde
            sondeform.capteur = sonde.id
            appareilform.sondes.append_entry(sondeform)


    #appareilform.categorie_appareil_id.choices = [(data.id, data.nom) for data in Categorieappareil.query.all()]
    return render_template('appareil/appareil_edit.html', appareilform=appareilform, gpios=gpios, appareil=appareil, isSonde=instance_appareil.sonde)

@app.route('/appareils')
def appareils():
    appareils = Appareil.query.order_by('nom')
    return render_template('appareil/appareils.html', appareils=appareils)


@app.route('/appareil/delete/<int:appareil_id>')
def delete_appareil(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    gpios = Gpio.query.filter_by(appareil_id=appareil_id)
    if gpios != None:
        for gpio in gpios:
            db.session.delete(gpio)

    programmations = Programmation.query.filter_by(appareil=appareil_id)
    if programmations != None:
        for programmation in programmations:
            db.session.delete(programmation)

    mode_de_marches = ModeDeMarche.query.filter_by(appareil_id=appareil_id)
    if mode_de_marches != None:
        for mode_de_marche in mode_de_marches:
            db.session.delete(mode_de_marche)
    db.session.delete(appareil)
    db.session.commit()
    reload()
    return redirect(url_for('appareils'))


@app.route('/appareil/test/<int:appareil_id>', methods=['POST','GET'])
def test(appareil_id):
    # liste des appareils pour affichage
    appareils = Appareil.query.all()

    appareil = Appareil.query.get(appareil_id)
    programmations = Programmation.query.filter_by(appareil=appareil_id).order_by(Programmation.day).all()

    if appareil.sonde_id:
        sonde = appareil.appareil_sonde
        sondeform = ReglageSondeForm(obj=sonde,data=request.form)
        if sondeform.validate_on_submit():
            sondeform.populate_obj(sonde)

            db.session.add(sonde)
            db.session.commit()
            print('commit')
        else:
            print('no commi')

    else:
        sondeform = False
        print('no form')

    instance_appareil = globals()[appareil.categorieappareil](appareil)
    mode_de_marche = ModeDeMarche.query.filter_by(appareil_id=appareil_id).first()

    mode_de_marcheform = ModeDeMarcheForm(obj=mode_de_marche, data=request.form)
    mode_de_marcheform.mode_de_marche.choices = instance_appareil.choices_mdm

    if mode_de_marcheform.validate_on_submit():
        mode_de_marcheform.populate_obj(mode_de_marche)
        # si passage en mode test=>passage de l'ordre à l'arrêt
        if mode_de_marcheform.mode_de_marche.data == 'test':
            manuel = Manuel.query.filter_by(appareil_id=appareil_id).first()

            if manuel == None:
                manuel = Manuel()
                manuel.appareil_id = appareil_id
                manuel.ordre = 'arret'

            else:
                manuel.ordre = 'arret'
            db.session.add(manuel)
        db.session.add(mode_de_marche)

    db.session.commit()
    #reload()

    tab2 = []
    gpios = Gpio.query.all()
    for gpio in gpios:
        var = gpio.valeur.split('_')[1]

        try:
            data = os.popen(f'raspi-gpio get {var}')
            dati = data.read()

            mode = dati.find('func=') + 5
            popo = dati.find('level=')

            toto = {
                'gpio': dati[5:popo - 2],
                'mode': dati[mode:mode + 6],
                'level': dati[popo + 6],
                'info': gpio.info
            }
            tab2.append(toto)
        except:
            print('no ds1820b')

    tab = []
    for gpio in appareil.gpios:

        var = gpio.valeur.split('_')[1]
        print(var)
        try:
            data = os.popen(f'raspi-gpio get {var}')
            dati = data.read()

            mode = dati.find('func=')+5
            popo = dati.find('level=')

            toto = {
                'gpio':dati[5:popo-2],
                'mode':dati[mode:mode+6],
                'level':dati[popo+6],
                'info': gpio.info
            }
            tab.append(toto)
        except:
            print('no ds1820b')

    tab2 = []
    return render_template('appareil/appareil_test.html', tab=tab, tab2=tab2, sondeform=sondeform, appareils=appareils, appareil=appareil, instance_appareil=instance_appareil, mode_de_marcheform=mode_de_marcheform, modedemarche=instance_appareil.choices_mdm, programmations=programmations)


# GPIO
@app.route('/gpio', methods=['POST', 'GET'])
def gpio():
    gpio = Gpio()
    gpioform = GpioForm(request.form)
    if gpioform.validate_on_submit():
        gpioform.populate_obj(gpio)
        db.session.add(gpio)
        #db.session.commit()
        return redirect(url_for('gpios'))
    gpioform.valeur.choices = gpio.get_free_gpio()
    #gpioform.appareils.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('gpio/gpio.html', gpioform=gpioform)


@app.route('/gpios')
def gpios():
    gpios_list = Gpio.query.order_by('appareil_id', 'mode').all()
    return render_template('gpio/gpios.html', gpio_list=gpios_list)


@app.route('/gpio/<int:gpio_id>', methods=['POST', 'GET'])
def edit_gpio(gpio_id):
    gpio = Gpio.query.get(gpio_id)
    gpioform = GpioForm(obj=gpio, data=request.form)
       
    if gpioform.validate_on_submit():
        gpioform.populate_obj(gpio)
        #db.session.add(gpio)
        #db.session.commit()
        return redirect(url_for('gpios'))
    gpioform.valeur.choices = gpio.get_free_gpio() 
    #gpioform.appareils.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('gpio/gpio.html', gpioform=gpioform)


@app.route('/gpio/delete/<int:gpio_id>')
def delete_gpio(gpio_id):
    gpio = Gpio.query.get(gpio_id)
    #db.session.delete(gpio)
    #db.session.commit()
    return redirect(url_for('gpios'))


# Programmation
@app.route('/programmation/add', methods=['POST', 'GET'])
def add_programmation():
    programmation = Programmation()

    programmationform = ProgrammationForm(request.form)
    if programmationform.validate_on_submit():
        programmationform.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
        return redirect(url_for('liste_programmations'))
    programmationform.appareil.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('programmation/programmation.html', programmationform=programmationform)


@app.route('/programmations')
def liste_programmations():
    programmations = Programmation.query.order_by('appareil', 'day').all()
    return render_template('programmation/programmations.html', programmations=programmations)

@app.route('/programmation/delete/<int:programmation_id>')
def delete_programmation(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    db.session.delete(programmation)
    db.session.commit()
    return redirect(url_for('liste_programmations'))

@app.route('/programmation/edit/<int:programmation_id>', methods=['POST','GET'])
def edit_programmation(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    programmationform = ProgrammationForm(obj=programmation, data=request.form)
    programmations = Programmation.query.filter_by(appareil=programmation.appareil_programmation.id).all()

    if programmationform.validate_on_submit():
        programmationform.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
        return redirect(url_for('liste_programmations'))
    programmationform.appareil.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('programmation/programmation.html', programmationform=programmationform, programmations=programmations)


# mode test
@app.route('/test_app', methods=['post'])
def test_app():
    ordre = (request.form.get('data').split('_'))[0]
    appareil = Appareil.query.get(int((request.form.get('data').split('_'))[1]))
    try:
       data = Manuel.query.filter_by(appareil_id=appareil.id).first()
       if data is None:     
            data = Manuel()
            data.appareil_id = appareil

       data.ordre = ordre
       db.session.add(data)
       db.session.commit()
    except:
        print('bug')
    return 'tata'

# déclaration des sondes type ds1820b
@app.route('/sondes')
def sondes():
    sondes = Sonde.query.all()
    return render_template('sonde/sonde.html', sondes=sondes)

@app.route('/sonde/<int:sonde_id>', methods=['get','post'])
def edit_sonde(sonde_id):
    sonde = Sonde.query.get(sonde_id)
    sondeform = Ds1820bForm(obj=sonde, data=request.form)
    if sondeform.validate_on_submit():
        sondeform.populate_obj(sonde)
        db.session.add(sonde)
        db.session.commit()
        return redirect(url_for('sondes'))
    return render_template('sonde/edit_sonde.html', sondeform=sondeform, sonde=sonde)

# delete sonde
@app.route('/delete_sondes')
def delete_sonde():
    sondes = Sonde.query.all()

    for sonde in sondes:
        db.session.delete(sonde)
        try:
            db.session.delete(sonde.sonde_valeur_id)
        except:
            pass
    db.session.commit()
    return 'true'

## Add programmation by a appareil
@app.route('/programmation/add/<int:appareil_id>', methods=['post','get'])
def add_programmation_by_app(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    form = ProgrammationForm(obj=appareil)
    if form.validate_on_submit():
        programmation = Programmation()
        form.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()

        return redirect(url_for('test',appareil_id=appareil.id))
    else:
        print(form.errors);

    return render_template('programmation/add_programmation_by_app.html', form = form, appareil_id=appareil_id)


## Add programmation by a appareil
@app.route('/api/programmation/add/<int:appareil_id>', methods=['post','get'])
def add_programmation_by_app_api(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    print(appareil)
    form = ProgrammationForm(obj=appareil)
    if form.validate_on_submit():
        programmation = Programmation()
        form.populate_obj(programmation)
        programmation.appareil = appareil.id
        db.session.add(programmation)
        db.session.commit()

        return redirect(url_for('test',appareil_id=appareil.id))
    else:
        print(form.errors);

    return jsonify({"app_id":appareil_id})



# Delete programmation from appareil
@app.route('/appareil/programmation/delete/<int:programmation_id>')
def delete_programmation_from_appareil(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    db.session.delete(programmation)
    db.session.commit()
    return redirect(url_for('test',appareil_id=programmation.appareil))

# Edit programmation from appareil
@app.route('/appareil/programmation/edit/<int:programmation_id>', methods=['get','post'])
def edit_programmation_from_appareil(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    form = ProgrammationForm(obj=programmation)
    if form.validate_on_submit():
        form.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
    return render_template('programmation/programmation.html',programmationform=form)

@app.route('/api/programmation/<int:id>', methods=['get'])
def api_programmation(id):
    programmation = Programmation.query.order_by('day').filter_by(appareil=id).all()
    appareil = Appareil.query.get(id)

    datas = dict()
    datas['programmations'] = dict()
    datas['appareil'] = appareil.nom
    datas['id'] = id

    for data in programmation:
        datas['programmations'][data.id] = {
            'id':data.id,
            'heure_debut':data.start,
            'min_debut':data.start_min,
            'heure_fin':data.end,
            'min_fin':data.end_min,
            'day':data.day
        }
    return (datas)

@app.route('/api/mdm/<int:id>', methods=['post','get'])
def api_mdm(id):
    form = request.form
    if request.method == 'POST':
        print(request.form['mdm'])
        print(request.method)
        appareil = Appareil.query.get(id)
        appareil.mode_de_marche.mode_de_marche = request.form['mdm']
        db.session.add(appareil)
        db.session.commit()
    return render_template('test.html')

@app.route('/api/temp-min/<int:id>', methods=['get','post'])
def temp_mini(id):
    if request.method == 'POST':
        appareil = Appareil.query.get(id)
        appareil.sonde.min = request.form['value']
        db.session.add(appareil)
        db.session.commit()
    return 'yes'

@app.route('/api/temp-max/<int:id>', methods=['get','post'])
def temp_max(id):
    if request.method == 'POST':
        appareil = Appareil.query.get(id)
        appareil.sonde.max = request.form['value']
        db.session.add(appareil)
        db.session.commit()
    return 'yes'

@app.route('/api/programmation/delete', methods=['post'])
def api_delete_programmation():

    if request.method == 'POST':

        programmation = Programmation.query.get(request.form['appareil'])
        db.session.delete(programmation)
        db.session.commit()
    return 'nice'

@app.route('/api/delete/sonde', methods=['post'])
def api_delete_sonde():
    #sonde = Sonde.query.get(request)
    sonde = Sonde.query.get(request.form['sonde'])
    db.session.delete(sonde)
    db.session.commit()

    return redirect('/sondes')


@app.route('/api/gpios/status', methods=['get'])
def api_gpios_status():
    tab2 = []

    appareils = Appareil.query.all()

    myAppareils = []

    for md in appareils:
        toto = {'id_appareil':md.id,'status':md.sortie}
        myAppareils.append(toto)

    #print(myAppareils)
    tab2.append({'appareils':myAppareils})
    dateMachine = str(str(datetime.now()).split(' ')[1]).split('.')[0]
    machine = {'dateMachine':dateMachine}

    tab2.append(machine)
    gpios = Gpio.query.all()

    for gpio in gpios:
        var = gpio.valeur.split('_')[1]

        try:
            data = os.popen(f'raspi-gpio get {var}')
            dati = data.read()

            mode = dati.find('func=') + 5
            popo = dati.find('level=')

            toto = {
                'gpio': dati[5:popo - 2],
                'mode': dati[mode:mode + 6],
                'level': dati[popo + 6],
                'info': gpio.info
            }
            tab2.append(toto)
        except:
            print('no ds1820b')
    print(tab2)
    return jsonify(tab2)


if __name__ == '__main__':
    app.debug = True
    #db.create_all()
    app.run()
    
