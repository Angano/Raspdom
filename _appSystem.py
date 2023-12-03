from config import app, db
from models import ConfigBcm, Bus, Status
from flask import render_template, url_for,redirect,request
from flask import jsonify
import helpers

@app.route('/configSytem')
def configSystem():
    # retourne dans base de donnée heure system, forçage mise à jour temps sonde, temps raffraichissement tps sonde
    status = Status.query.all()

    datas = dict()
    for data in status:
        # print(data.id, data.status, data.identifiant, data.valeur)
        if data.identifiant == "update_temp":
            datas[data.identifiant] = {
                'status': data.status,
                'valeur': data.valeur
            }
    datas['getversion'] = helpers.getrevision()
    return render_template('config/systeme.html', status = datas)


@app.route('/api/configSystem')
def api_syteme():
    # retourne dans base de donnée heure system, forçage mise à jour temps sonde, temps raffraichissement tps sonde
    status = Status.query.all()

    datas = dict()
    for data in status:
        #print(data.id, data.status, data.identifiant, data.valeur)
        if data.identifiant == "update_temp":

            datas[data.identifiant]= {
                    'status':data.status,
                    'valeur':data.valeur
            }
        elif data.identifiant == "now_time":
            datas[data.identifiant]= {
                'status':data.status,
                'valeur':data.valeur,
                'now_time':data.time_now
            }
    return jsonify(datas)

@app.route('/api/updatestatus',methods=['post'])
def api_update_status():
    form = request.form

    try:
        result = form['forcage_maj']
        status = Status.query.filter_by(identifiant='update_temp').first()
        status.status = bool(result)
        db.session.add(status)
        db.session.commit()
        print(result)
        return result
    except:

        pass
    try:
        result = form['temps_sonde']
        status = Status.query.filter_by(identifiant='update_temp').first()
        status.valeur = float(result)
        db.session.add(status)
        db.session.commit()
        print(result)
        return result
    except:
        pass

    return 'hlo'