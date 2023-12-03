window.addEventListener('DOMContentLoaded',function(){
  
    this.setInterval(function(){
        getStatus()
    },1000)
    
})


function getStatus(){
    var xhr = new XMLHttpRequest()
    xhr.open('get', this.window.origin+'/api/configSystem')
    xhr.responseType = "json"
    xhr.onload = function(){
        displayStatus(this.response)
        
    }

    xhr.send()
}


function displayStatus(datas){

    $('#heure_systeme').text(datas['now_time'].now_time)
    
}

$('input').on('change',function(){
    var value = this.value

    var form = new FormData()

    if(this.type==='checkbox'){
        if ($(this).is(':checked')){
            value = 1
        }else{
        value = ""
            
        
    } 
    }
    
    form.append(this.name,value)
    form.append('csrf_token', csrf)

    var xhr = new XMLHttpRequest()
    xhr.open('post',window.origin+'/api/updatestatus',true)
    
    xhr.send(form)
})