window.addEventListener('DOMContentLoaded',function(){



    modalUpdate()
    setInterval(function(){
        
       getComposants();
       getAppareils();
    },8000);
    
    
    updateValeur();
    resetValeurCumule()
    toggleActived()
    /* Display composant */
    $('*[data-display-composants]').on('click',function(){
        let element = $(this).data('display-composants')
        $(`*[data-composants="${element}"]`).toggle('slow')
        
        
    })




})



function getComposants(){
         let xhr = new XMLHttpRequest()
        let url = window.origin+'/api/composants'
    
        xhr.open('get',url, true)
        xhr.responseType = 'json'
        xhr.onload = function(){
            for(let t in this.response){
                $(`span[data-composant-id=${t}]`).html(this.response[t])
                $(`td[data-composant-id-td=${t}]`).addClass('bg-light').css('opacity','1')
                setTimeout(function(){
                   $(`td[data-composant-id-td=${t}]`).css('opacity','1')
                },1500)
            }
        }
        xhr.send()
    
}

function getAppareils(){
         let xhr = new XMLHttpRequest()
        let url = window.origin+'/api/valeurs'
    
        xhr.open('get',url, true)
        xhr.responseType = 'json'
        xhr.onload = function(){
            for(let t in this.response){
              
            $(`span[data-composant-id-val=${this.response[t].id_valeur}]`).html(this.response[t].session).addClass('bg-light').css('opacity','1')
            $(`td[data-composant-id-td=${this.response[t].id_valeur}]`).html(this.response[t].composant_valeur).addClass('bg-light').css('opacity','1')
            
            $(`input[data-composant-id=${this.response[t].id_valeur}][name="consigne"]~span`).html(this.response[t].consigne).addClass('bg-light').css('opacity','1')
            $(`input[data-composant-id=${this.response[t].id_valeur}][name="min"]~span`).html(this.response[t].min).addClass('bg-light').css('opacity','1')
            $(`input[data-composant-id=${this.response[t].id_valeur}][name="max"]~span`).html(this.response[t].max).addClass('bg-light').css('opacity','1')
            $(`span[data-composant-id-valeur_cumule=${this.response[t].id_valeur}]`).html(this.response[t].cumul).addClass('bg-light').css('opacity','1')
            $(`td[data-composant-id-actived=${this.response[t].id_valeur}]>span`).first().html(this.response[t].actived).addClass('bg-light').css('opacity','1')
            
            $(`td`).css('opacity','1')
            $(`td>span`).css('opacity','1')
            setTimeout(function(){
                   $(`td`).css('opacity','1')
                   $(`td>span`).css('opacity','1')
                },1500)
             
             
            }
        }
        xhr.send()
    
}

function updateValeur(){
    
    $('.md-input~span').on('click',function(event){
            $(this).hide()
            $(this).siblings('input:first').prop('type','text').prop('readonly',false).focus().focusout(function(element){
                $(this).siblings('span:first').show()
                el = $(element.currentTarget)
                
                el.prop('type','hidden')
                
                
                /* ################## */
                let xhr = new XMLHttpRequest()
                let url = window.origin+'/api/valeur/update'
                let datas = `valeur_id=${el.data('valeur-id')}&valeur_name=${el.prop('name')}&valeur_valeur=${el.val()}&csrf_token=${csrf}`
                xhr.open('post',url,true)
                xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                xhr.send(datas)
                
                
                
            }
            )
          
            
    })
        
    
}

function resetValeurCumule(){
    $('span[data-composant-id-reset]').on('click',function(){
        let valeur_id = $(this).data('composant-id-reset')
        let valeur_name = 'init'
        let valeur_valeur = 1
      
        let xhr = new XMLHttpRequest()
        let url = window.origin+'/api/valeur/update'
        let datas = `valeur_id=${valeur_id}&valeur_name=${valeur_name}&valeur_valeur=${valeur_valeur}&csrf_token=${csrf}`
        xhr.open('post',url,true)
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.send(datas)
        
        
    })}
    
function toggleActived(){
    $('span[data-composant-id-actived]').on('click',function(){
        let valeur_id = $(this).data('composant-id-actived')
        let valeur_name = 'actived'
        let valeur_valeur = 1
      
        let xhr = new XMLHttpRequest()
        let url = window.origin+'/api/valeur/update'
        let datas = `valeur_id=${valeur_id}&valeur_name=${valeur_name}&valeur_valeur=${valeur_valeur}&csrf_token=${csrf}`
        xhr.open('post',url,true)
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.send(datas)
        
        
    })}


/* Chart.js */

function getChart(chart){


    var xhr =new XMLHttpRequest()
    xhr.open('get',window.origin+'/api/graph/test_tempSonde', true)
    xhr.responseType = 'json'
    xhr.onload = function(){

        chart.data.labels = this.response.historique.date

        chart.data.datasets[0].data =this.response.historique.temp
        chart.data.datasets[1].data =this.response.historique.temp2

        chart.update()

       /* const ctx = document.getElementById('myChart');

        new Chart(ctx, {
            type: 'line',
            data: {
            labels: this.response.historique.date,
            datasets: [{
                label: this.response.info,
                data: this.response.historique.temp,
                borderWidth: 1
            }]
            },
            options: {
            scales: {
                y: {
                beginAtZero: true
                }
            }
            }

        });*/
    }
    xhr.send()
}


function addData(chart, label, newData) {
    chart.data.labels.push(label);
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(newData);
    });
    chart.update();
    }



function modalUpdate(){
    $('[data-composant_id]').on('click',function(e){
        e.stopPropagation();
        
        var composant_id = $(this).data('composant_id')[0]

         // Gestion graphes
        const ctx = document.getElementById('myChart');

        var chart =  new Chart(ctx, {
                type: 'line',
                data: {
                labels: [''],
                datasets: [{
                    label: [''],
                    data: [''],
                    borderWidth: 1
                },{
                    label: [''],
                    data: [''],
                    borderWidth: 1
                }]
                },
                options: {
                scales: {
                    y: {
                    beginAtZero: false
                    }
                }
                }

            });

        var xhr =new XMLHttpRequest()
        //xhr.open('get',window.origin+'/api/graph/test_tempSonde', true)
        xhr.open('get',window.origin+`/api/graph/composant/${composant_id}`, true)
        xhr.responseType = 'json'
        xhr.onload = function(){
            $("#modele").text(this.response.modele)
            $("#description").text(this.response.description)
            $("#categorie").text(this.response.categorie)
            $("#emplacement").text(this.response.emplacement)
            chart.data.datasets[0].label = this.response.unite1
            chart.data.datasets[1].label = this.response.unite2
            chart.data.labels = this.response.recorded_at

            chart.data.datasets[0].data =this.response.valeur1
            chart.data.datasets[1].data =this.response.valeur2

            chart.update()
            $('#exampleModal').on('hidden.bs.modal', function () {
                chart.destroy()
            });

        }
        xhr.send()

    })


    }















