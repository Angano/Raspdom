$('select').on('change', function(e){

    var selectzs = $('select[data-select="gpio"]').not('#'+e.target.id)
    //var selects = $($(selectzs+'>option')).not(`[value=${e.target.value}]`)

    var options = $(selectzs).not('option[value='+e.target.value+']')
   console.log(e.target.value)
    //console.log($('select[data-select="gpio"]').not('#'+e.target.id))

    $('select[data-select="gpio"]').not('#'+e.target.id).each(function(){
        console.log(this.options)
        $(this.options).each(function(key,value){

            if(value.value==e.target.value){
            this.remove()
            }
        })
    })
   //selects[0].options.remove(0)
   //console.log($('select[data-select="gpio"]').not('#'+e.target.id))

})