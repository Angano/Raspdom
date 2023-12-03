window.addEventListener('DOMContentLoaded',function(){
    $('*[data-sonde-id]').on('click',function(){
        console.log($(this).data('sonde-id'))
        let element = $(this)

      

        let xhr = new XMLHttpRequest()
        let url = window.origin+'/api/sonde'
        let form = new FormData()
        form.append('sonde',$(this).data('sonde-id'))
        form.append('csrf_token', csrf)
        xhr.open('post',url,true)
        xhr.onload = function(){
            
            $(element.next().text(this.response))
        }
        xhr.send(form)
    })


    function gpios_status(){
        let xhr = new XMLHttpRequest()

        var url = window.origin+'/api/gpios/status'

        xhr.open('get', url )
        xhr.setRequestHeader('Access-Control-Allow-Origin','*');
        xhr.responseType = 'json'

        xhr.onload = function(){

            this.response.forEach(function(element){

                // Mise a jours valeurs sondes
                var sondes = element.sondes
                for(datas in sondes){
                    $(`[data-sondeId="${sondes[datas].id}"]`).text(`${Math.round(sondes[datas].temp * 10) / 10} °C`)
                  
                }

              

            })

     

        }
        xhr.send()
    }


    setInterval(function(){
        gpios_status();
    },1000)
})