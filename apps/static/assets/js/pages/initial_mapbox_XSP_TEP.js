/**
 *   FMM web application
 *   Author: Can Yang
 *   XSP TEP Demo Site
 *   Author: CHJ
 */

// Background map
var center = [25.07031, 121.530595]; // XSP-TEP
var zoom_level = 17;
map = new L.Map('map', {
    center: new L.LatLng(center[0], center[1]),
    zoom: zoom_level,
    minZoom:12,
});

// tile layer set to mapbox's non-free tiles using CHJ's personal mapbox account
/*
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
   attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
*/
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
	attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
	maxZoom: 18,
	id: 'mapbox/streets-v11',
	tileSize: 512,
	zoomOffset: -1,
	accessToken: 'pk.eyJ1IjoiY2hqaWFuZyIsImEiOiJjbDBodWFjajkwN2NpM2xtcTJvZm5wbGgzIn0.73B4dtJO0daFkRlMMrscwg'
}).addTo(map);

/* not setting geofence
var exteriorStyle = {
    "color": "#FFFF8C",
    "fill":false,
    "opacity":1.0,
    "weight":5,
    "dashArray":"10 10"
};

var boundary_layer = L.geoJson(boundary, {style: exteriorStyle});

boundary_layer.addTo(map);
not setting geofence */

// Two trajectories and two extra layers: raw GNSS and map-matched one using fmm
var rawtrajLayers = new L.FeatureGroup();
map.addLayer(rawtrajLayers);
var fmmtrajLayers = new L.FeatureGroup();
map.addLayer(fmmtrajLayers);

// Add reset button
L.Control.Reset = L.Control.extend({
    options: {
        position: 'topleft',
    },
    onAdd: function(map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-control leaflet-bar');
        var controlUI = L.DomUtil.create('a', 'fa fa-home', controlDiv);
        controlUI.title = 'Reset base-map';
        controlUI.setAttribute('href', '#');
        L.DomEvent
            .addListener(controlUI, 'click', L.DomEvent.stopPropagation)
            .addListener(controlUI, 'click', L.DomEvent.preventDefault)
            .addListener(controlUI, 'click', function() {
                map.setView(map.options.center, map.options.zoom);
            });
        return controlDiv;
    }
});
resetControl = new L.Control.Reset();
map.addControl(resetControl);

// Add clear history button
L.Control.RemoveAll = L.Control.extend({
    options: {
        position: 'topleft',
    },
    onAdd: function(map) {
        var controlDiv = L.DomUtil.create('div', 'leaflet-control leaflet-bar leaflet-draw-toolbar');
        var controlUI = L.DomUtil.create('a', 'leaflet-draw-edit-remove', controlDiv);
        controlUI.title = 'Clear historic trajectory';
        controlUI.setAttribute('href', '#');
        L.DomEvent.addListener(controlUI, 'click', L.DomEvent.stopPropagation)
                  .addListener(controlUI, 'click', L.DomEvent.preventDefault)
                  .addListener(controlUI, 'click', function() {
            if (fmmtrajLayers.getLayers().length == 0) {
                alert("No features drawn");
            } else {
                fmmtrajLayers.clearLayers();
                $("#uv-div").empty();
                // chart.destroy();
            }
        });
        return controlDiv;
    }
});
removeAllControl = new L.Control.RemoveAll();
map.addControl(removeAllControl);
