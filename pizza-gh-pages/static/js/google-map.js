var google;

function init() {
    // Coordenadas para o "UDF Centro Universitário" (Ajuste conforme necessário)
    var myLatlng = new google.maps.LatLng(-15.788497, -47.916341); // Latitude e Longitude aproximada da UDF

    var mapOptions = {
        zoom: 15, // Aumentei o zoom para que a área fique mais visível
        center: myLatlng,
        scrollwheel: false,
        styles: [
            { elementType: 'geometry', stylers: [{ color: '#242f3e' }] },
            { elementType: 'labels.text.stroke', stylers: [{ color: '#242f3e' }] },
            { elementType: 'labels.text.fill', stylers: [{ color: '#746855' }] },
            {
                featureType: 'administrative.locality',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#d59563' }]
            },
            {
                featureType: 'poi',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#d59563' }]
            },
            {
                featureType: 'poi.park',
                elementType: 'geometry',
                stylers: [{ color: '#263c3f' }]
            },
            {
                featureType: 'poi.park',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#6b9a76' }]
            },
            {
                featureType: 'road',
                elementType: 'geometry',
                stylers: [{ color: '#38414e' }]
            },
            {
                featureType: 'road',
                elementType: 'geometry.stroke',
                stylers: [{ color: '#212a37' }]
            },
            {
                featureType: 'road',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#9ca5b3' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry',
                stylers: [{ color: '#746855' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'geometry.stroke',
                stylers: [{ color: '#1f2835' }]
            },
            {
                featureType: 'road.highway',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#f3d19c' }]
            },
            {
                featureType: 'transit',
                elementType: 'geometry',
                stylers: [{ color: '#2f3948' }]
            },
            {
                featureType: 'transit.station',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#d59563' }]
            },
            {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [{ color: '#17263c' }]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.fill',
                stylers: [{ color: '#515c6d' }]
            },
            {
                featureType: 'water',
                elementType: 'labels.text.stroke',
                stylers: [{ color: '#17263c' }]
            }
        ]
    };

    // Obter o elemento HTML que conterá o mapa
    var mapElement = document.getElementById('map');

    // Criar o mapa do Google usando o elemento e as opções definidas
    var map = new google.maps.Map(mapElement, mapOptions);

    // Endereço para o UDF Centro Universitário
    var address = 'UDF Centro Universitário, Brasília, DF';

    // Solicitação de geocodificação
    $.getJSON('https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=YOUR_API_KEY', function(data) {
        if (data.status === "OK") {
            var location = data.results[0].geometry.location;
            var latlng = new google.maps.LatLng(location.lat, location.lng);

            // Criar o marcador no mapa
            new google.maps.Marker({
                position: latlng,
                map: map,
                title: address,
                icon: 'images/loc.png'  // Caminho do ícone (opcional)
            });

            // Centraliza o mapa na localização do marcador
            map.setCenter(latlng);
        }
    });
}

// Adicionar o evento do DOM para carregar o mapa
google.maps.event.addDomListener(window, 'load', init);

