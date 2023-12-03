document.addEventListener('DOMContentLoaded', function(){

    
    $('[data-ssid').on('click', function(){
        
        let ordre = $(this).data('ordre')
        let ssid = $(this).data('ssid')

        let url = window.origin+'/api/config/reseaux'

        let form = new FormData()
        form.append('ordre',ordre)
        form.append('ssid',ssid)
        form.append('csrf_token', csrf)

        let xhr = new XMLHttpRequest()
        xhr.open('post',url,true)
        xhr.send(form)
    })

})