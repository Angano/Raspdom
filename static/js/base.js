 $('#btnctr').on('click',function(){
                $('#part-one').toggle('slow')

                })

// Affichage heure courante serveur
function getTime(){

    var url = window.origin+'/api/getTime'
    let xhr = new XMLHttpRequest()

    setInterval(function(){
        xhr.open('get', url )
    xhr.setRequestHeader('Access-Control-Allow-Origin','*');
    xhr.responseType = 'json'
    xhr.onload = function(){
        
        $('#dateMachine').text(this.response.dateMachine)
        
        // Traitement infos connexions
        let types = []
        $('#exampleModalLabel2').text('Connections actives')
        let datasConnexion = `
        <table class="table">
            <thead>
                <tr>
                <th>Device</th>
                <th>Name</th>
                <th>Type</th>
                <th>IP</th>
                <th>STATUS</th>
                </tr>
            </thead>
            <tbody>`
        for(const [key,value] of Object.entries(this.response.connexion)){
            types.push(value['TYPE'])
            
           
            datasConnexion = datasConnexion+`
            <tr><td>${value['DEVICE']}</td><td>${value['NAME']}</td><td>${value['TYPE']}</td><td>${value['IP']}</td><td>${value['STATUS']}</td></tr>
            `
        }
        
        if(types.includes('ethernet')){
            $('#fail-ethernet').animate({
                'opacity':0},1000)
        }else{
            $('#fail-ethernet').animate({
                'opacity':0.7},1000)
        }
        if(types.includes('wifi')){
            $('#fail-wifi').animate({
                'opacity':0}
                )
        }else{
            $('#fail-wifi').animate({
                'opacity':0.7}
                )
        }
        datasConnexion = datasConnexion +`</ul>`

        $('#md-modal-body2').html(datasConnexion)


    }
        xhr.send()

    },5000)

}

getTime()
$('.md-icon-connect').on('click', function(){
 
    $('#exampleModal2').modal('toggle')
   
})
