window.addEventListener('DOMContentLoaded',function(){

 $('span[data-edit]').on('click',function(e){
   
    $($(this).siblings('span')[0]).toggle('slow')


 })
  
 $('input[data-input]').on('change',function(){
 

    var datas = $(this).parents('form')[0]
   //var datas = document.getElementById('form-3')
    var form = new FormData(datas)
    var xhr = new XMLHttpRequest()
    xhr.open('post',window.origin+'/api_next', true)
    xhr.responseType="json"
 
   
    xhr.onload = function(){
      console.log('kk')
    }
    xhr.send(form)

    
    
 }) 

 $('form').on('submit',function(e){
   e.preventDefault();
     var datas = e.target
      console.log(datas)
     var form = new FormData(datas)
     var datas = `csrf_token=${CSRF_TOKEN}&gpio=rr`
     var xhr = new XMLHttpRequest()
   
      xhr.open('post',window.origin+'/api_next', true)
      xhr.responseType="json"
      //xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
      xhr.onload = function(){
         console.log('kk')
      }
     xhr.send(form)
 
 })

 })