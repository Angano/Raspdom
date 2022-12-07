window.addEventListener('DOMContentLoaded',function(){

    let origin = location.origin;

    document.getElementById('form_prog').addEventListener('submit', function(e){

        e.preventDefault();

        var form = new FormData(document.getElementById('form_prog'));
        console.log(form);

        let xhr = new XMLHttpRequest();
        xhr.open('post',`${origin}/api/programmation/add/`+document.getElementById('app').value);
        xhr.send(form);

        var myModalEl = document.getElementById('exampleModal');
        var modal = bootstrap.Modal.getInstance(myModalEl)
        modal.hide();
        xhr.onreadystatechange = function(){
            if(this.status===200 && this.readyState===4){
                location.reload();
            }
        }

    });

    document.getElementById('form_mdm').addEventListener('submit',function(e){
        e.preventDefault();
    })

    document.querySelectorAll('[data-mdm]').forEach(element => {
        element.addEventListener('click',function(e){
        document.getElementById('mode_de_marche').value = e.target.dataset.mdm;

        var form = new FormData(document.getElementById('form_mdm'));
        var xhr = new XMLHttpRequest();
        var url = `${origin}/appareil/test/`+document.getElementById('app').value
        xhr.open('post',url,true)
        xhr.onreadystatechange = function(){
            if(this.readyState === 4 && this.status === 200 ){
                location.reload();
            }
        }
        xhr.send(form);

        })
    });

    // Selection de l'heure de début

//////////////////////////////////////////////////////////////////////////////////////
// heure
    Array.from(document.getElementById('toto').children).forEach(element=>{
        element.addEventListener('click', function(e){
        if(document.querySelector('.md-active').id === 'deb'){
            document.getElementById('hStart').value = e.target.innerText
            // data dans input
            document.getElementById('i-deb').value = e.target.innerText+':'+document.getElementById('i-deb').value.split(':')[1]
            hStart = true;

        }
        else if(document.querySelector('.md-active').id === 'fin'){
            document.getElementById('hEnd').value = e.target.innerText
            // data dans input
            document.getElementById('i-fin').value = e.target.innerText+':'+document.getElementById('i-fin').value.split(':')[1]
            hEnd = true
        }

    })
    })

// efface les selection jours
function initDays(){
    Array.from(document.getElementById('bof').children).forEach(element=>{
         element.className = "btn btn-sm btn-primary";
     });
}

// minute
    Array.from(document.getElementById('titi').children).forEach(element=>{

        element.addEventListener('click', function(e){

        if(document.querySelector('.md-active').id === 'deb'){
            document.getElementById('mStart').value = e.target.innerText

            // data dans input
            document.getElementById('i-deb').value = document.getElementById('i-deb').value.split(':')[0]+':'+e.target.innerText
            mStart = true;
        }
        else if(document.querySelector('.md-active').id === 'fin'){
            document.getElementById('mEnd').value = e.target.innerText
            // data dans input
            document.getElementById('i-fin').value = document.getElementById('i-fin').value.split(':')[0]+':'+e.target.innerText
            mEnd = true;
            }
        })
    })


    // jour
    this.document.getElementById('days').addEventListener('click', function(e){
        document.getElementById('select-day').value = e.target.dataset.value;
        initDays()

        e.target.className = "btn btn-sm btn-success"
        document.getElementById('add-day').className = 'btn btn-sm btn-success'
        document.getElementById('add-day').innerText = e.target.innerText
        days = true;
   
    })
    
    this.document.getElementById('deb').addEventListener('click',function(){
        this.className = 'border border-3 border-primary btn btn-sm btn-light md-active'
        document.getElementById('fin').className = 'btn btn-sm btn-light'
        $('#i-fin').css('font-weight','400')
        $('#i-deb').css('font-weight','900')
    })

    this.document.getElementById('fin').addEventListener('click',function(){
        this.className = 'border border-3 border-primary btn btn-sm btn-light md-active'
        $('#i-fin').css('font-weight','900')
        document.getElementById('deb').className = "btn btn-sm btn-light"
        $('#i-deb').css('font-weight','400')
    })

///////////////////////////////////////////////////////////////////

// masque le calendrier
function hideCalendar(){
    $('#titi').hide();
    $('#toto').hide();
    $('#days').hide();
}

function showCalendar(){
    $('#titi').show();
    $('#toto').show();
    $('#days').show();
}

hideCalendar();



$('#tab-fin,#tab-deb').on('click','#fin,#deb', function(){
    showCalendar();
})

$('#tab-fin').on('click',function(){

    // gestion affichage cohérence des heures proposées
    var test = parseInt($('#i-deb').val().split(':')[0]);
    var totos = Array.from(document.getElementById('bob').children)

    for(let i=0; i<test; i++){
        totos[i].className = "d-none";
    }
})

$('#tab-deb').on('click',function(){
    
    // gestion affichage cohérence des heures proposées
    Array.from(document.getElementById('bob').children).forEach(element=>{

        element.className = "my-1 btn btn-sm btn-primary";
    })

})


$('body #exampleModal').on('click', function(e){
    if(e.target.id !== "fin" && e.target.id !== "deb" && e.target.className !=='btn btn-sm btn-success' &&
        e.target.className !== "my-1 btn btn-sm btn-primary"){
        hideCalendar();
    };
})

// Contôle de la saisie des données
let mStart, hStart, mEnd, hEnd, days;
$('#exampleModal').on('click',function(){
    if( mStart === true && hStart === true && mEnd === true && hEnd === true && days === true){
       
        $('#result').text('👍');
        $('input:submit').show();
    }else{
        $('#result').text('');
        $('input:submit').hide();
    }

})

// gestion slider température
this.document.getElementById("min-range").addEventListener('change',function(e){
    $('#min').val(e.target.value)
    $('#span-min').val(e.target.value)
})

this.document.getElementById("max-range").addEventListener('change',function(e){
    $('#max').val(e.target.value)
    $('#span-max').val(e.target.value)
})


})

