from config import app, db
from models import ConfigBcm, Bus, Status
from flask import render_template, url_for,redirect,request
from flask import jsonify
from sqlalchemy import or_
@app.route('/configBcm',methods=['get','post'])
def configBcm():


    mode_run = Status.query.filter(Status.identifiant=='mode_run').first()
    '''if request.method=='POST':
        if request.form.get('I2C1') == 'off':
            i2c1 = False
            for data in ConfigBcm.query.filter_by(bus='I2C1').all():
                data.alt_fct = False
                db.session.add(data)
        else:
            i2c1 = True
            for data in ConfigBcm.query.filter_by(bus='I2C1').all():
                data.mode = 'Input'
                data.alt_fct = True
                db.session.add(data)

        if request.form.get('SPI0') == 'off':
            spi0 = False
            for data in ConfigBcm.query.filter_by(bus='SPI0').all():
                data.alt_fct = False
                db.session.add(data)
        else:
            spi0 = True
            for data in ConfigBcm.query.filter_by(bus='SPI0').all():
                data.mode = 'Input'
                data.alt_fct = True
                db.session.add(data)

        if request.form.get('SPI1') == 'off':
            spi1 = False
            for data in ConfigBcm.query.filter_by(bus='SPI1').all():
                data.alt_fct = False
                db.session.add(data)
        else:
            spi1 = True
            for data in ConfigBcm.query.filter_by(bus='SPI1').all():
                data.mode = 'Input'
                data.alt_fct = True
                db.session.add(data)

        data1 = Bus.query.filter_by(name='I2C1').first()
        data1.actived = i2c1
        db.session.add(data1)

        data1 = Bus.query.filter_by(name='SPI0').first()
        data1.actived = spi0
        db.session.add(data1)

        data1 = Bus.query.filter_by(name='SPI1').first()
        data1.actived = spi1
        db.session.add(data1)



        db.session.commit()'''
    datas_bank1 = ConfigBcm.query.filter(ConfigBcm.pin%2==0).all()
    datas_bank2 = ConfigBcm.query.filter(ConfigBcm.pin%2!=0).all()
    datas_bank3 = ConfigBcm.query.filter(ConfigBcm.name.contains('Gpio_')).order_by(ConfigBcm.bus.asc()).all()
    return render_template('configBcm/index.html',datas_bank1=datas_bank1,datas_bank2=datas_bank2,datas_bank3=datas_bank3,mode_run=mode_run)


@app.route('/configBcm_other')
def configBcm_other():

    datas = ConfigBcm.query.filter(ConfigBcm.name.like('GPIO%'),ConfigBcm.mode.like('Output')).order_by('alt_fct_name_other').all()
    return render_template('configBcm/other.html', datas=datas)

@app.route('/api/updategpio',methods=['get','post'])
def api_updategpio():
    gpio = ConfigBcm.query.filter_by(name=request.form.get('gpio')).first()

    results =  dict()

    if not gpio.used_in and  (gpio.configbcm_bus==None or gpio.configbcm_bus.actived==False):

        if gpio.mode == 'Input':
            gpio.mode = 'Output'
        elif gpio.mode == 'Output':
            gpio.mode = 'Input'
        db.session.add(gpio)
        db.session.commit()

        results['result'] = 'true'
    else:
        results['result'] = 'false'

    gpios = ConfigBcm.query.all()
    datas = list()
    for data in gpios:
        toto = {
            'id': data.id,
            'pin': data.pin,
            'name': data.name,
            'alt_fct': data.alt_fct,
            'alt_fct_name': data.alt_fct_name,
            'bus': data.bus,
            'mode': data.mode,
            'used_in': data.used_in,
            'bus_id': data.bus_id,
            'bus_used':'false'

        }
        if data.used_in != None:
            toto['used_in'] = 'true'
        if data.bus_id != None:
            toto['bus_used']= data.configbcm_bus.actived
        datas.append(toto)

    results['datas'] = datas
    return jsonify(results)


@app.route('/api_next',methods=['post'])
def api_next():
    
  
    if request.method == 'POST':
        if request.form.get('gpio') != None:
            configbcm = ConfigBcm.query.get(request.form.get('gpio'))


            if request.form.get('name')!=None:

                configbcm.alt_fct_name_other = request.form.get('name')
            elif request.form.get('mode') != None and request.form.get('mode')== 'on' and configbcm.mode == 'Output':

                configbcm.write_status = True #request.form.get('mode')
            elif request.form.get('mode') != None and request.form.get('mode') == 'off' and configbcm.mode == 'Output':

                configbcm.write_status = False  # request.form.get('mode')
            db.session.add(configbcm)
            db.session.commit()

        if request.form.get('run') != None:
            print(request.form.get('run'))
            status = Status.query.filter(Status.identifiant=='mode_run').first()
            status.status = bool(int(request.form.get('run')))
            db.session.add(status)
            db.session.commit()
    return 'hello'
@app.route('/api/get_configBcm')
def api_get_config_bcm():
    config_bcm = ConfigBcm.query.filter(or_(ConfigBcm.mode=='Input',ConfigBcm.mode=='Output')).all()
    datas = []
    for config in config_bcm:
        datas.append(
            {
                'gpio_name':config.name,
                'read_status':config.read_status,
                'write_status':config.write_status,
                'mode':config.mode,
                'id':config.id
            }
        )
    return jsonify(datas)