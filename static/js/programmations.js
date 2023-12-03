window.addEventListener('DOMContentLoaded',function(){
    var url = this.window.origin

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
                $('#exampleModal').modal('hide').slow()
            }
            xhr.send(formdata)
        })
    }

    $('*[data-appareil]').on('click',function(e){
        var appareil = e.target.dataset['appareil']
        let xhr = new XMLHttpRequest();
        xhr.open('get',`${url}/api/programmation/${appareil}`)
        xhr.responseType ='json'

        xhr.onload = function(){

            appareilobject = this.response
            addProgrammation(appareilobject)
        }
        xhr.send()
        
    })
})