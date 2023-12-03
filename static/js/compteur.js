window.addEventListener('DOMContentLoaded',function(){
    
    this.setInterval(function(){
        getCompteurs()
    },2000)
})

function getCompteurs(){

    var xhr = new XMLHttpRequest()
    xhr.open('get',window.origin+'/api/compteur/getValues', true)
    xhr.responseType = 'json'
    xhr.onload = function(){
        
        this.response.forEach(element => {
           
         
            $('[data-valeur="'+element.id_compteur+'"]').text(element.valeur)
            $('[data-moyenne="'+element.id_compteur+'"]').text(element.moyenne)
          
        });
    }
    xhr.send()
}