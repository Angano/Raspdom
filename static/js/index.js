
    var days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    var url = this.window.origin

    // gestion affichage tableau de données
    $('.md-btn-display').on('click',function(e){
       $('#'+e.target.dataset['target']).toggle().css('z-index',10).css('position','relative').css('background-color','white')
    })

    // gestion affichage des programmations
    $('div[data-span]').on('click',function(e){

        var appareil = e.target.dataset['appareil']
        eraseModal()
        $('#md-modal-footer').html(' <span id="md-modal-btn1" class="btn btn-sm btn-success">Ajouter une programmation</span>')

        let ul = '<ul id="ul-programmations">'
        let xhr = new XMLHttpRequest();
        xhr.open('get',`${url}/api/programmation/${appareil}`)
        xhr.responseType ='json'

        xhr.onload = function(){

            for(let toto in this.response.programmations){

                ul = ul + `<li class="d-flex justify-content-between mx-2">
                <div>${days[(this.response.programmations[toto].day)-1]}: ${this.response.programmations[toto].heure_debut}:${this.response.programmations[toto].min_debut}=>${this.response.programmations[toto].heure_fin}:${this.response.programmations[toto].min_fin}</div>
                    <div>
                        <form method="post" action="">
                            <input type="hidden" name="appareil" value="${this.response.programmations[toto].id}" >
                            <input class="btn btn-sm btn-danger" type="submit" value="X">
                            </form>
                    </div> </li>`
            }

            ul = ul + '</ul>'

            //$('#'+e.target.dataset['span']).css('border','solid 1px #dbcece').css('padding','inherit').css('text-align','inherit').html(ul)
            $('.modal-body').html(ul)
            appareilobject = this.response
            $('#exampleModalLabel').html(`${appareilobject.appareil} - <small> Liste des programmations</small>`)
            $('#md-modal-btn1').on('click', function(){

                addProgrammation(appareilobject)
                //$('#md-modal-body').html('').text('')

            })
            // Suppression d'une programmation
            $('#ul-programmations>li>div>form').on('submit', function(e){
            e.preventDefault()
            var form = new FormData(e.target)
            form.append('csrf_token', csrf)
            eraseModal()
            var xhr2 = new XMLHttpRequest()
            xhr2.open('post', url+'/api/programmation/delete')
            xhr2.onload = function(){
                $('.modal.body').html(reload(appareilobject))
            }
            xhr2.send(form)

        })

            }
        xhr.send()
    })

    // gestion changement du mode de marche
    $('form').on('change',function(e){
        var appareil = e.target.dataset['appareil']
        //e.target.className = 'btn btn-sm btn-danger'
        let form = new FormData(e.currentTarget)
        let xhr = new XMLHttpRequest()
        xhr.open('post',url+'/api/mdm/'+e.target.dataset.appareil)
        //xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function(){
            if(xhr.status===200 && xhr.readyState===4){
                //e.target.className = 'btn btn-sm btn-primary'
                $('#md-calendar-'+e.target.dataset.appareil).text('Changement pris en compte').show()
                .css('padding','1rem').css('width','max-content').css('border','solid 1px #dbcece').css('margin-left','5px').css('z-index',10)
                .addClass('bg-warning text-dark border border-1 border-dark ')
                setTimeout(()=>{
                    $('#md-calendar-'+e.target.dataset.appareil).text('').hide();
                    if(e.target.value == 'prog'){
                        $(`[data-span=md-calendar-${appareil}]`).removeClass('d-none')
                    }else{
                        $(`[data-span=md-calendar-${appareil}]`).addClass('d-none')
                    }

                    if(e.target.value == 'off' || e.target.value == 'test'){
                        $(`[data-md-card-appareil=${appareil}]`).addClass('d-none')
                    }else{
                        $(`[data-md-card-appareil=${appareil}]`).removeClass('d-none')
                    }
                },2000)
            }
        }
        xhr.onprogress = function(){
            //e.target.className='btn btn-sm btn-warning'
        }
      
        xhr.send(form);
    })

    // gestion valeur curseur
    $('.md-min').on('change', function(e){
        $('#'+e.currentTarget.dataset['target']).text(e.target.value)
        var value = e.target.value
        var appareil = e.target.id.split('-')[2]
        var url = window.origin+'/api/temp-min/'+appareil
        var datas = new FormData()
        datas.append('value',value)
        datas.append('csrf_token',csrf)

        let xhr = new XMLHttpRequest()
        xhr.open('post', url)
        xhr.send(datas)

    })

    $('.md-max').on('change', function(e){
        $('#'+e.currentTarget.dataset['target']).text(e.target.value)
        var value = e.target.value
        var appareil = e.target.id.split('-')[2]
        var url = window.origin+'/api/temp-max/'+appareil
        var datas = new FormData()
        datas.append('value',value)
        datas.append('csrf_token',csrf)

        let xhr = new XMLHttpRequest()
        xhr.open('post', url)
        xhr.send(datas)
    })

    // affichage cohérent entre curseur et input température
    $('.md-min').each(function(key,value){
        $('#'+value.dataset['target']).text(value.value)
      
    })
    $('.md-max').each(function(key,value){
        $('#'+value.dataset['target']).text(value.value)
    })
       
    $('.md-setting').on('click', function(e){
        $('#'+e.target.dataset['targetCursor']).toggle('slow')
        $('#'+e.target.dataset['targetCursor'])[0].focus()
    })

    // affichage histogramme

    $('[data-targethistogramme]').on('click',function(e){
        console.log(e.target.dataset)
        $('[data-histogramme='+e.target.dataset.targethistogramme+']').toggle('slow')

        })

    $('.card-header').on('click',function(){
        $('.md-max').hide('slow')
        $('.md-min').hide('slow')
        $('div[data-histogramme]').hide('slow')
        $('table').hide('slow')
    })

    function reload(appareil){
     let ul = '<ul id="ul-programmations">'
        let xhr = new XMLHttpRequest();
        xhr.open('get',window.origin+`/api/programmation/${appareil.id}`)
        xhr.responseType ='json'


        xhr.onload = function(){
            $(`[data-span=md-calendar-${appareil.id}]`).text('🗓('+Object.keys(this.response.programmations).length+')')

            for(let toto in this.response.programmations){

            ul = ul + `<li class="d-flex justify-content-between mx-2">
            <div>${days[(this.response.programmations[toto].day)-1]}: ${this.response.programmations[toto].heure_debut}:${this.response.programmations[toto].min_debut}=>${this.response.programmations[toto].heure_fin}:${this.response.programmations[toto].min_fin}</div>
                <div>
                    <form method="post" action="">
                        <input type="hidden" name="appareil" value="${this.response.programmations[toto].id}" >
                        <input class="btn btn-sm btn-danger" type="submit" value="X">
                        </form>
                </div> </li>`
            }

            ul = ul + '</ul>'

            //$('#'+e.target.dataset['span']).css('border','solid 1px #dbcece').css('padding','inherit').css('text-align','inherit').html(ul)
            $('.modal-body').html(ul)

            ////////////////////////////////////////////////////////////////////////////////

             // Suppression d'une programmation
            $('#ul-programmations>li>div>form').on('submit', function(e){
            $('#md-modal.footer').html('')
            e.preventDefault()

            var form = new FormData(e.target)

            form.append('csrf_token', csrf)

            var xhr2 = new XMLHttpRequest()
            xhr2.open('post', url+'/api/programmation/delete')
            xhr2.onload = function(){
                $('.modal.body').html(reload(appareilobject))
            }
            xhr2.send(form)

        })

            //////

            }
        xhr.send()
        $('#exampleModalLabel').html(`${appareil.appareil} - <small>Liste des programmations</small>`)
        //$('#md-modal-btn1').text('Ajouter une programmation')
        $('#md-modal-btn2').hide()
        $('#md-modal-btn1').show()


        return ul

    }

    function addProgrammation(appareil){

        // Rechargement de la liste des programmations en cas d'appui sr "retour à la liste des ..."
        $('#md-modal-btn2').on('click',function(){
            $('.modal-body').html(reload(appareil))
        })

        $('#md-modal-btn2').show().text('Retour à la liste')
        $('#md-modal-btn1').hide()

        // Ajout titre dans Modal
        var titre = `${appareil.appareil} - <small>Ajout d\'une programmation</small>`
        $('h1[data-md-appareil]').html(titre)

        const day = {1:'lundi',2:'mardi',3:'Mercredi', 4:'Jeudi', 5:'Vendredi', 6:'Samedi', 7:'Dimanche'}

        // Ajout appareil dans data-md-appareil
        $('#exampleModalLabel').attr('data-md-appareil',appareil.id)

        // Heure de début
        var h_start = `<select name="start">`
        for(let i=0; i<24; i++){
            h_start = h_start + `<option value="${i}">${i}</option>`
        }
        h_start = h_start + `</select>`

        var m_start = `<select name="start_min">`
        for(let i=0; i<59; i=i+5){
            m_start = m_start + `<option value="${i}">${i}</option>`
        }
        m_start = m_start + `</select>`

        // Heure fin
        var h_fin = `<select name="end">`
        for(let i=0; i<24; i++){
            h_fin = h_fin + `<option value="${i}">${i}</option>`
        }
        h_fin = h_fin + `</select>`

        var m_fin = `<select name="end_min">`
        for(let i=0; i<59; i=i+5){
            m_fin = m_fin + `<option value="${i}">${i}</option>`
        }
        m_fin = m_fin + `</select>`


        // jour semaine
        var days = `<select name="day">`
        for(let i=1; i<8; i++){
            days = days + `<option value="${i}">${day[i]}</option>`
        }
        days = days + `</select>`



        var form = `
        <form method="post" action="${url}/api/programmation/add/${appareil.id}" id="md-form-programmation">
            <div class="d-flex justify-content-center">
                <input type="hidden" name="csrf_token" value="${csrf}">
                <span class="mt-auto mb-0">${days}</span>
                <div>
                    <div>Début</div>
                    <div>${h_start}:${m_start} => </div>
                </div>
                <div>
                    <div>Fin</div>
                    <div>${h_fin}:${m_fin}</div>
                </div>
            </div>
            <div class="text-center pt-3"><input class="btn btn-sm btn-primary" type="submit" value="Valider"></div>

        </form>`


        $('.modal-body').html(form)

        $('#md-form-programmation').on('submit', function(e){
            e.preventDefault()
            var formdata = new FormData(e.target)

            let xhr = new XMLHttpRequest()
            xhr.open('post', `${url}/api/programmation/add/${appareil.id}`)
            xhr.onload = function(){
                $('.modal-body').html(reload(appareil))

            }
            xhr.send(formdata)
        })
    }

    // Affichage status des gpios
    function gpios_status(){
        let xhr = new XMLHttpRequest()

        var url = window.origin+'/api/gpios/status'

        xhr.open('get', url )
        xhr.setRequestHeader('Access-Control-Allow-Origin','*');
        xhr.responseType = 'json'

        xhr.onload = function(){

            this.response.forEach(function(element){

                //gestion affichage mode de marche
                var tab = element.appareils
                for(index in tab){

                    var el = element.appareils[index]
                    $(`#md-mdmr${el.id_appareil}`).text(el.status)

                    // convertion des dates
                    let mois = ['Janv','Fev','Mars','Avr','Mai','Juin','Jui','Août','Sept','Oct','Nov','Dec']
                    let jours = ['Dim','Lundi','Mardi','Mer','Jeudi','Vend','Sam']

                    let debut = new Date(el.debut)
                    let fin = new Date(el.fin)

                    let debutData = jours[debut.getDay()]+'-'+ debut.getDate()+'-'+mois[debut.getMonth()]+'-'+debut.getFullYear() +' <b>'+('0'+debut.getUTCHours()).slice(-2)+':'+('0'+debut.getMinutes()).slice(-2)+':'+('0'+debut.getSeconds()).slice(-2)+'</b>'
                    let finData = jours[fin.getDay()]+'-'+ fin.getDate()+'-'+mois[fin.getMonth()]+'-'+fin.getFullYear() +' <b>'+('0'+fin.getUTCHours()).slice(-2)+':'+('0'+fin.getMinutes()).slice(-2)+':'+('0'+fin.getSeconds()).slice(-2)+'</b>'

                    let now = new Date()


                    let nowTime = now.getTime()+3600000
                    let debTime = debut.getTime()
                    let finTime = fin.getTime()


                    if(finTime>nowTime && el.actived == true){
                        var maDate = new Date(finTime-nowTime-3600000)
                        var maDateDebut = new Date(debTime-nowTime-3600000)
                        var duree = new Date(finTime-debTime-3600000)

                        var dataDate = ``
                        if(debTime>nowTime){
                            dataDate = dataDate +`<small style="line-height:0px">Début dans: ${maDateDebut.getMonth()}mois ${maDateDebut.getDate()}jours ${maDateDebut.getHours()}h ${maDateDebut.getMinutes()}mn ${maDateDebut.getSeconds()}sec</small><br>`
                            }
                        dataDate = dataDate +`<small style="line-height:0px">Fin dans:  ${maDate.getMonth()}mois ${maDate.getDate()}jours  ${maDate.getHours()}h ${maDate.getMinutes()}mn ${maDate.getSeconds()}sec</small><br>`
                        dataDate = dataDate +`<small style="line-height:0px">Durée totale: ${duree.getMonth()}mois ${duree.getDate()}jours ${duree.getHours()}h ${duree.getMinutes()}mn ${duree.getSeconds()}sec</small>`
                        $(`[data-mfdisplay="${el.id_appareil}"]>p`).last().html(dataDate)
                    }


                    if(nowTime<finTime && el.actived === true){
                        $(`div[data-mfdisplay="${el.id_appareil}"]`).show('slow')

                    }else{

                    $(`div[data-mfdisplay="${el.id_appareil}"]`).hide('slow')


                    }



                    // gestion affichage marche forcée
                    if(el.actived === true){
                        var textmf = `<p class="p-0 m-0">${debutData} => ${finData}<img class="mx-2" data-mf-desactived="${el.id_appareil}" src="static/assets/cancel-icon.webp" width="25px" style="cursor:pointer; display:inline-block"></p>`
                        $(`div[data-mf="${el.id_appareil}"]`).html(textmf).show('slow')
                    }else{
                        $(`div[data-mf="${el.id_appareil}"]`).html('').hide('slow')
                    }


                }


                $('#dateMachine').text(element.dateMachine)

                if(element.mode == 'OUTPUT'){
                    if(element.level == '0'){
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','green')

                    }else{
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','red')

                    }

                }
                else if(element.mode == 'INPUT\n'){
                                        if(element.level == '1'){
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','red')

                    }else{
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','blue')
                    }
                }

            })

            // gestion désactivation marche forcée
            $('img[data-mf-desactived]').on('click',function(){

                let appareil_id = this.dataset['mfDesactived']

                let xhr = new XMLHttpRequest()
                xhr.open('get',`${window.origin}/api/mf/desactived/${appareil_id}`)
                xhr.send()
            })

        }
        xhr.send()
    }


    setInterval(function(){
        gpios_status();
    },2000)

    // gestion marche forcée
    $('img[data-marcheforce]').on('click',function(){
        eraseModal()

        let id = this.dataset['marcheforce']

        // récupération des infos de l'appareil
        let form = `<form action="/api/marcheforce/add" method="post" id="md-form-mf">
                    <input type="hidden" name="csrf_token" value="${csrf}">
                    <input type="hidden" name="appareil_mf" value="${id}">
                    <div>
                        <label>Début</label>
                        <input id="datetimepickerdebut" type="text" name="debut">
                    </div>
                    <div>
                        <label>Fin</label>
                        <input id="datetimepicker" type="text" name="marcheforce">
                    </div>


                     </form>`
        $('#md-modal-footer').html(`<input type="submit" id="md-modal-submit" class="btn btn-sm btn-success" value="ajouter une marche forcée">`)
        let xhr = new XMLHttpRequest()
        xhr.open('get', `${url}/api/appareil/${id}`)
        xhr.responseType = 'json'
        xhr.onload = function(){

            $('#exampleModalLabel').text(this.response['appareil'] + ' - Marche Forcée')
            $('#md-modal-body').html(form)

            // DatetimePicker
            jQuery('#datetimepicker').datetimepicker({
            step:5,
            format:'d-m-Y H:i:s'
            });

            jQuery('#datetimepickerdebut').datetimepicker({
            step:5,
            format:'d-m-Y H:i:s'
            });

            $('#md-modal-submit').on('click', function(e){
                e.preventDefault()
                let form3 = $('#md-form-mf')

                let sendform = new FormData(form3[0])
                let xhr2 = new XMLHttpRequest()
                xhr2.open('post',`${url}/api/marcheforce`)
                xhr2.onload = function(e){
                    $('#exampleModal').modal('hide')
                    eraseModal()
                }
                xhr2.send(sendform)
            })
            }



        xhr.send()
    })

    function eraseModal(){
        $('#exampleModalLabel').text('')
        $('#md-modal-body').html('')
        $('#md-modal-footer').html('')
    }
