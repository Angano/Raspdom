window.addEventListener('DOMContentLoaded',function(){
 $('*[data-gpio]').on('click',function(e){

        let url = window.location.origin+'/api/updategpio'
        let gpio = $(this).data('gpio')

        let data = `csrf_token=${CSRF_TOKEN}&gpio=${gpio}`
        let xhr =  new XMLHttpRequest()

        xhr.open('post',url,true)
        xhr.responseType="json"
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.onload = function(){

        var text = 'Maj impossible'
        var toto = this.response.result
        var datas = this.response.datas
        datas.forEach(function(element){
            var node = ''
            if(element.mode=='Input'){
                node = `<span class="btn btn-sm md-inputio">${element.mode}</span>`
                $(`#id-${element.name}`).html(node)
            }else{
                node = `<span class="btn btn-sm md-outputio" >${element.mode}</span>`
                $(`#id-${element.name}`).html(node)
            }

        })
        var classe = 'warning'
        if(toto==='true'){
            text = 'Maj Ok'
            classe = 'success'
        }
        let message = `<span style="position:absolute;top:1rem; right:1rem" class="btn btn-sm btn-${classe}">${text}</span>`


        $('#message_api').html(message).fadeIn("slow")
        setTimeout(function(){
            $('#message_api:first-child').fadeOut("slow")
            $('#message_api').children().first().fadeOut("slow")
        },2000)
        }
        xhr.send(data)
    })

    /* Pour mise à jour champ nom */

 $('input[data-input]').on('change',function(){


    var datas = $(this).parents('form')[0]
   //var datas = document.getElementById('form-3')
    var form = new FormData(datas)
    var xhr = new XMLHttpRequest()
    xhr.open('post',window.origin+'/api_next', true)
    xhr.responseType="json"


    xhr.onload = function(){
       var text = 'Maj impossible'
       toto = true

        var classe = 'warning'
        if(toto==='true' || true){
            text = 'Maj Ok'
            classe = 'success'
        }
        let message = `<span style="position:absolute;top:1rem; right:1rem" class="btn btn-sm btn-${classe}">${text}</span>`


        $('#message_api').html(message).fadeIn("slow")
        setTimeout(function(){
            $('#message_api:first-child').fadeOut("slow")
            $('#message_api').children().first().fadeOut("slow")
        },2000)

    }
    xhr.send(form)



 })

 this.setInterval(function(){
    apiGetConfigbcm()
 },1000)

})



function apiGetConfigbcm(){
    var element
    var xhr = new XMLHttpRequest()
    xhr.open('get',window.origin+'/api/get_configBcm',true)
    xhr.responseType = 'json'
    xhr.onload = function(){
        for(var i=0;i<this.response.length;i++){
            element =  this.response[i]

            if(element.write_status==true){

                $(`#label_off_${element.id}`).removeClass('md-spi')
                $(`#label_on_${element.id}`).addClass('md-test')
            }else{
                $(`#label_off_${element.id}`).addClass('md-spi')
                $(`#label_on_${element.id}`).removeClass('md-test')
            }
            if(element.read_status==true){

                $(`#read_${element.id}`).html('<b style="font-size:.85rem">On</b>')

            }else{
                $(`#read_${element.id}`).html('<small>Off</small>')
                
            }
        }
    }

    xhr.send()
}
