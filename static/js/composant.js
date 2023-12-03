window.addEventListener('DOMContentLoaded',function(){

    $('.carousel-inner').each(function(key,value){
        
        $(value).children().first().addClass('active')
    })

})