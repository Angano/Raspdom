document.addEventListener('DOMContentLoaded', function(){

    // Gestion graphes
    const ctx = document.getElementById('myChart');

    var chart =  new Chart(ctx, {
            type: 'line',
            data: {
            labels: [''],
            datasets: [{
                label: ['S1'],
                data: [''],
                borderWidth: 1
            },{
                label: ['S2'],
                data: [''],
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

        });


   
})

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