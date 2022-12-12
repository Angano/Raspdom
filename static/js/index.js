window.addEventListener('DOMContentLoaded',function(){
    var days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    
    var url = this.window.origin

    // gestion affichage tableau de données
    $('.md-btn-display').on('click',function(e){
       $('#'+e.target.dataset['target']).toggle()
    })

    $('span[data-span]').on('click',function(e){
        let ul = '<ul>'
        let xhr = new XMLHttpRequest();
        xhr.open('get',url+'/api/programmation/'+e.target.dataset['appareil'])
        xhr.responseType ='json'
        xhr.onload = function(){
            console.log(this.response)
           for(let toto in this.response){
            //Vendredi: 00:00=>17:55 Del Edit
            ul = ul + `<li>${days[(this.response[toto].day)-1]}: ${this.response[toto].heure_debut}:${this.response[toto].min_debut}=>${this.response[toto].heure_fin}:${this.response[toto].min_fin}</li>`
        }
        //console.log(e.target.dataset['span'])
        ul = ul + '</ul>'
        $('#'+e.target.dataset['span']).html(ul).toggle()
       
   
    }
    $('body').on('cick',function(){

    })
           
        
        xhr.send()
    })

    // gestion changement du mode de marche
    $('form').on('change',function(e){
       
        let form = new FormData(e.currentTarget)
        let xhr = new XMLHttpRequest()
        xhr.open('post',url+'/api/mdm/'+e.target.dataset.appareil)
        //xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function(){
            console.log(xhr.status, xhr.readyState)
            if(xhr.status===200 && xhr.readyState===4){
                e.target.className = 'btn btn-sm btn-success'
            }else{
                e.target.className = 'btn btn-sm btn-danger'
            }
        }
        xhr.onprogress = function(){
            e.target.className='btn btn-sm btn-warning'
        }
      
        xhr.send(form);
    })
})