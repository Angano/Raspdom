window.addEventListener('DOMContentLoaded',function(){
    var days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    
    var url = this.window.origin

    // gestion affichage tableau de données
    $('.md-btn-display').on('click',function(e){
       $('#'+e.target.dataset['target']).toggle().css('z-index',10).css('position','relative').css('background-color','white')
    })

    // gestion affichage des programmations
    $('div[data-span]').on('click',function(e){
        let ul = '<ul><li class="btn btn-sm btn-success">+ Programmation</li>'
        let xhr = new XMLHttpRequest();
        xhr.open('get',url+'/api/programmation/'+e.target.dataset['appareil'])
        xhr.responseType ='json'
        xhr.onload = function(){
     
           for(let toto in this.response){
            
            ul = ul + `<li class="d-flex justify-content-between mx-2"><div>${days[(this.response[toto].day)-1]}: ${this.response[toto].heure_debut}:${this.response[toto].min_debut}=>${this.response[toto].heure_fin}:${this.response[toto].min_fin}</div><div><span class="btn btn-sm btn-danger">X</span></div> </li>`
        }
        //console.log(e.target.dataset['span'])
        ul = ul + '</ul>'
        $('#'+e.target.dataset['span']).html(ul).toggle()   
        }
        xhr.send()
    })

    // gestion changement du mode de marche
    $('form').on('change',function(e){
        e.target.className = 'btn btn-sm btn-danger'
        let form = new FormData(e.currentTarget)
        let xhr = new XMLHttpRequest()
        xhr.open('post',url+'/api/mdm/'+e.target.dataset.appareil)
        //xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function(){
            if(xhr.status===200 && xhr.readyState===4){
                e.target.className = 'btn btn-sm btn-primary'
                $('#md-calendar-'+e.target.dataset.appareil).text('Changement pris en compte').show()
                .css('padding','1rem').css('width','max-content').css('border','solid 1px #dbcece').css('margin-left','5px').css('z-index',10)
                .addClass('bg-light text-dark')
                setTimeout(()=>{
                    $('#md-calendar-'+e.target.dataset.appareil).text('').hide();
                    location.reload()
                },2000)
            }
        }
        xhr.onprogress = function(){
            e.target.className='btn btn-sm btn-warning'
        }
      
        xhr.send(form);
    })

    // gestion valeur curseur
    $('.md-min').on('change', function(e){
        $('#'+e.currentTarget.dataset['target']).prop('value',e.target.value)
    })

    $('.md-max').on('change', function(e){
        $('#'+e.currentTarget.dataset['target']).prop('value',e.target.value)
    })

    // affichage cohérent entre curseur et input température
    $('.md-min').each(function(key,value){
        $('#'+value.dataset['target']).prop('value',value.value)
      
    })
    $('.md-max').each(function(key,value){
        $('#'+value.dataset['target']).prop('value',value.value)
    })
       
    $('.md-setting').on('click', function(e){
        $('.'+e.target.dataset['targetCursor']).toggle()
        
    })

    // affichage histogramme

    $('[data-targethistogramme]').on('click',function(e){
        console.log(e.target.dataset)
        $('[data-histogramme='+e.target.dataset.targethistogramme+']').toggle()
        console.log( $('[data-histogramme='+e.target.dataset.targethistogramme+']'))
        })

})