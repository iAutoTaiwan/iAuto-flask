$(document).ready(function() {
    console.log('Connect to ' + 'http://' + document.domain + ':' + location.port);
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    var geojsonMarkerOptions = {
        radius: 5,
        fillColor: "#ff7800",
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    };

    function onEachFeature(feature, layer) {
        layer.on({
            'click': function() {
                window.location.href = 'iauto_dashboard/' + this.feature.properties.name + '.html';
            },
        });
    };

    socket.on('vehicle_position', function(data) {
        // console.log(data);
        rawtrajLayers.clearLayers();
        for (const val of data) {
            var geojson_layer = L
                .geoJson(val.data, {
                    win_url: val.url,
                    onEachFeature: onEachFeature,
                    pointToLayer: function (feature, latlng) {
                        return L.circleMarker(latlng, geojsonMarkerOptions);
                    }
                })
                .bindTooltip(val.label)
                .addTo(rawtrajLayers);
        };
    });

    socket.on('vehicle_history', function(data) {
        console.log(data);
        fmmtrajLayers.clearLayers();
        var geojson_layer = L.geoJson(data, {
            style: function(feature) {
                return {
                    color: 'red',
                    "weight": 5,
                    "opacity": 0.5
                };
            }
        });
        fmmtrajLayers.addLayer(geojson_layer);
    });
})
