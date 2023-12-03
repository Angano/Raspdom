
    var days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    var url = this.window.origin
    var dateMachine

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

            let tab = []
            let resultats = this.response.programmations
            
            for(let variable in this.response.programmations){
                tab.push(this.response.programmations[variable])
            }
           
           
            tab.sort(function(a,b){
                return a.day-b.day
            })

            let day_temp = 1
            let hr = ''

            for(let toto in tab){
                
                if(day_temp!==tab[toto].day){
                    day_temp = tab[toto].day
                    hr = '<hr>'
                }else{
                    hr = ''
                }    
                ul = ul + `${hr}<li class="d-flex justify-content-between mx-2">
                <div>${days[(tab[toto].day)-1]}: ${tab[toto].heure_debut}:${tab[toto].min_debut}=>${tab[toto].heure_fin}:${tab[toto].min_fin}</div>
                    <div>
                        <form method="post" action="">
                            <input type="hidden" name="appareil" value="${tab[toto].id}" >
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
        
        $('[data-histogramme='+e.target.dataset.targethistogramme+']').toggle('slow')

        })

    $('.card-header').on('click',function(){
        $('.md-max').hide('slow')
        $('.md-min').hide('slow')
        $('div[data-histogramme]').hide('slow')
        /*$('table').hide('slow')*/
    })

    function reload(appareil){
     let ul = '<ul id="ul-programmations">'
        let xhr = new XMLHttpRequest();
        xhr.open('get',window.origin+`/api/programmation/${appareil.id}`)
        xhr.responseType ='json'


        xhr.onload = function(){

            $(`[data-span=md-calendar-${appareil.id}]`).text('🗓('+Object.keys(this.response.programmations).length+')')

            let tab = []
            let resultats = this.response.programmations
            
            for(let variable in this.response.programmations){
                tab.push(this.response.programmations[variable])
            }
           
           
            tab.sort(function(a,b){
                return a.day-b.day
            })

            let day_temp = 1
            let hr = ''

            for(let toto in tab){
                
                if(day_temp!==tab[toto].day){
                    day_temp = tab[toto].day
                    hr = '<hr>'
                }else{
                    hr = ''
                }    
                ul = ul + `${hr}<li class="d-flex justify-content-between mx-2">
                <div>${days[(tab[toto].day)-1]}: ${tab[toto].heure_debut}:${tab[toto].min_debut}=>${tab[toto].heure_fin}:${tab[toto].min_fin}</div>
                    <div>
                        <form method="post" action="">
                            <input type="hidden" name="appareil" value="${tab[toto].id}" >
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
        /*
        var days = `<select name="day">`
        for(let i=1; i<8; i++){
            days = days + `<option value="${i}">${day[i]}</option>`
        }
        days = days + `</select>`
        */
       var days = ``
       for(let i=1; i<8; i++){
        days = days + `<div class="form-check"><label class="form-check-label"><input class="form-check-input" type="checkbox" name="day" value="${i}">${day[i]}</label></div>`
    }

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
                
                // Gestion affichage mode de marche
                var tab = element.appareils
                for(index in tab){

                    var el = element.appareils[index]
                    $(`#md-mdmr${el.id_appareil}`).attr('src','/static/assets/'+el.status+'.webp')

                    ////////////// Gestion affichage du temps restant sur mode forcée
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
                    ////////////////////////

                        var dataDate = ``
                        if(debTime>nowTime){
                            dataDate = dataDate +`<small style="line-height:0px">Début dans: ${calculRestant(maDateDebut)}</small><br>`
                            }
                        dataDate = dataDate +`<small style="line-height:0px">Fin dans: ${calculRestant(maDate)}</small><br>`
                        dataDate = dataDate +`<small style="line-height:0px">Durée:  ${calculRestant(duree)}</small>`
                        $(`[data-mfdisplay="${el.id_appareil}"]>p`).last().html(dataDate)
                    }

                    if(nowTime<finTime && el.actived === true){
                        $(`div[data-mfdisplay="${el.id_appareil}"]`).show('slow')
                    }else{
                        $(`div[data-mfdisplay="${el.id_appareil}"]`).hide('slow')
                    }



                    // gestion affichage marche forcée
                    if(el.actived === true){
                        var textmf = `<div class="p-0 m-0 w-100" style="font-size:80%;text-align:left">${debutData} => ${finData}<img class="mx-2" data-mf-desactived="${el.id_appareil}" src="static/assets/cancel-icon.webp" width="15px" style="cursor:pointer; display:inline-block"></div>`
                        $(`div[data-mf="${el.id_appareil}"]`).html(textmf).show('slow')
                    }else{
                        $(`div[data-mf="${el.id_appareil}"]`).html('').hide('slow')
                    }


                }
  
                // Affichage temps restant sur une tempos
                if(element['appareils']){
                    element['appareils'].forEach(function(key,value){
                        $(`[data-timeout=${key.id_appareil}]`).html(key.tempo_remaining)
                        if(key.tempo_remaining===null){
                             $(`[data-timeoutstart=${key.id_appareil}]`).addClass('d-none')
                        }else{
                             $(`[data-timeoutstart=${key.id_appareil}]`).removeClass('d-none')
                        }
                        
                        // Gestion affichage si programmation active
                        if(key.status_prog==true){
                            $($(`[data-span="md-calendar-${key.id_appareil}"]`)[0]).removeClass('border-secondary').addClass('md-programmation')
                        }else{
                            $($(`[data-span="md-calendar-${key.id_appareil}"]`)[0]).removeClass('md-programmation').addClass('border-secondary')
                        }
                    })
                }
                // Affichage statut GPIO
                if(element.mode == 'Output'){
                    
                    if(element.level == '0'){
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','radial-gradient(#e9e9ed,#ffffffb0)').css("border-bottom-color", "#13b713")

                    }else{
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css("background","white").css("border-bottom-color", "red")

                    }

                }
                else if(element.mode == 'Input'){
                                        if(element.level == '1'){
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','radial-gradient(#ffffffb0, #e9e9ed)').css('border-bottom-color','blue')

                    }else{
                        $(`[data-gpio="Gpio_${element.gpio}"]`).css('background','white').css('border-bottom-color','#d7d70d')
                    }
                }

                // Mise a jours valeurs sondes
                var sondes = element.sondes
                for(datas in sondes){
                    $(`[data-sondeId="${sondes[datas].id}"]`).text(`${Math.round(sondes[datas].temp * 10) / 10} °C`)
                  
                }

               // Gestion des messages
               
               if(element['dateMachine']){
                    dateMachine = element['dateMachine']
               }
               if(element['messages']){
                    manageMessages(element['messages'],dateMachine)
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
        },5000)

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

// permet de retourner un calcul de temps restant
function calculRestant(dataTime){

                        var resultat = ''
                        dataTime = dataTime.getTime()+3600000

                        const convSeconde = 1000
                        const convMinute = 60*convSeconde
                        const convHeure = 60*convMinute;
                        const convJour = 24*convHeure

                        var resteJour = Math.trunc(dataTime/convJour)+'j '
                        if(resteJour === '0j '){
                            resteJour=''}
                        var temp = dataTime%convJour
                        var resteHeure = ('0'+Math.trunc(temp/convHeure)).slice(-2)+'h:'

                        if(resteJour === '' && resteHeure === '00h:'){
                            resteHeure = ''}

                        temp = temp%convHeure
                        var resteMinute = ('0'+Math.trunc(temp/convMinute)).slice(-2)+'mn:'

                        if(resteJour === '' && resteHeure === '' && resteMinute === '00mn:'){
                            resteMinute = ''}

                        temp= temp%convMinute
                        var resteSeconde = ('0'+Math.trunc(temp/convSeconde)).slice(-2)+'s'


                        // Mise en forme de l'affichage

                        var resultat = resteJour+resteHeure+resteMinute+resteSeconde
                        return resultat}

// Récupération donnée d'un appareil lors d'un click sur "More"

$('*[data-more]').on('click',function(){
    $('#md-modal-body').html('')
    $('#exampleModalLabel').html('')
    $('#md-modal-footer').html('')
    getMore(this.dataset.more)


})


function getMore(appareil_id){
    var xhr = new XMLHttpRequest()
    var url = window.origin+'/api/getMore/'+appareil_id
   
    xhr.open('get',url,true)
    xhr.responseType = 'json'
    xhr.onload = function(){
        

        var gpios = ``
        $(this.response['gpios']).each(function(key,value){
            gpios = gpios+`
            <tr>
                <td>${value.info}</td><th>${value.mode}</th><td>${value.valeur}</td> <td>${value.nom}</td>
            </tr>`
            
        })

        // affichage des données dans la modal
        var datas = `
        
        <table class="table">
            
            <tbody>
                <tr>
                    <th>Description</th><td>${this.response.description}</td>
                </tr>
                <tr>
                    <th>Catégorie</th><td>${this.response.categorie}</td></tr>`
                    
        if(this.response.tempos){
            datas = datas + `
                <tr>
                    <th>Tempo</th>
                    <td>
                   
                    <input  style="border:none" readonly="readonly" data-appareil="${this.response.appareil_id}" name="update_consigne" type="text" value="${this.response.tempos}" id="tempos">
                    <span data-name="update-consigne">🔄</span>
                   </td>
                </tr>`
        }
        datas = datas + 
                
                `
                
                
            </tbody>
        </table>
        <legend>Gpios</legend>
        <table class="table">
            <tr>
                <th>Nom</th><th>Mode</th><th>Bcm</th><th>Repère</th>
                </tr>
        ${gpios}
        </table>
        `

        $('#md-modal-body').html(datas)
        $('#exampleModalLabel').html(`<h6>${this.response.nom}</h6>`)


        // Mise à jour de la consigne tempos
        majTempo()

    }
    xhr.send()
}
    
// mise à jour consigne tempo 
function majTempo(){

    $('*[data-name="update-consigne"]').on('click',function(){
            $('input[name="update_consigne"]').prop('readonly','').prop('style','border:solid 1px')
            
        })
    $('input[name="update_consigne"]').on('change',function(){

        $(this).prop('style','border:none')
        var form = new FormData()
        form.append('appareil', this.dataset.appareil)
        form.append('consigne',$(this).prop('value'))
        form.append('csrf_token',csrf)


        var xhr = new XMLHttpRequest()

        xhr.open('post',window.origin+'/api/update_consigne_tempo')
        
        
        xhr.send(form)

    })
    
}

// Gestion des messages
function manageMessages(messages,dateMachine){
    var element = $('.md-message>ul')
    var date_machine = new Date(dateMachine).getTime()
    var date_toto
    //date_to_compare.setMinutes(new Date(dateMachine).getMinutes()-1)
    $(element).html('')
    
    // Affichage des messages
    for(const[key,value] of Object.entries(messages)){
        var setMemory = []

        date_toto = new Date(value.message_recorded_at).getTime()+15000
        
        var li = document.createElement('li')
        li.textContent = value.message_recorded_at+'-'+value.message;
        $(li).css('list-style','none')

        if(date_toto>date_machine){
           setMemory = true
            $(li).css('background-color','rgb(229, 233, 238)')
            //$($(`ul[data-message="${value.message_appareil_id}"]`).parents()[0]).css('top','10.9999rem').css('max-height','4.4rem')
        }else{
            $(li).css('background-color','white')
           
            
        }
        $(`ul[data-message="${value.message_appareil_id}"]`).append(li)
    } 
    $(element).each((key,value)=>{
        $(value).children().first().css('font-weight','bold')
    })

    
 
    
}

$('.md-message').on('click',function(event){
    $(this).css('max-height','8rem').css('position','absolute').css('min-height','2.4rem').css('width','65%').css('border','1px solid black')
   event.stopPropagation();
   
})

$('div:not(.md-message)').on('click',function(){
    $('.md-message').css('max-height','2.4rem').css('position','absolute').css('min-height','2.4rem').css('width','65%').css('border','initial')

})
