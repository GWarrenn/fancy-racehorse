mapboxgl.accessToken = 'pk.eyJ1IjoiZ3dhcnJlbm4iLCJhIjoiY2p4d294Z2xhMGh4czNub2N1c202dnNvdCJ9.iRGx2PURnTzXBHgRIH2zKg';

//filtering out commute rides from vis

filter_value = ''

function showHideCommute(){
	currentMode = document.querySelector('input[name="mode"]:checked').value;
	if (currentMode === 'Show') {
		filter_value = ''
	}	
	if (currentMode === 'Hide') {
		filter_value = 'True'
	}	

	plot()
}

map_style = 'mapbox://styles/gwarrenn/ck0sl05xqetj01crs3u4prvyb'

function changeMapType(){
	currentMode = document.querySelector('input[name="maptype"]:checked').value;
	if (currentMode === 'Minimal') {
		map_style = 'mapbox://styles/gwarrenn/ck0sl05xqetj01crs3u4prvyb'
	}	
	if (currentMode === 'Detailed') {
		map_style = 'mapbox://styles/mapbox/dark-v10'
	}	

	plot()
}

// Mapping

const plot = async () => {

	const map = new mapboxgl.Map({
		container: 'map',
		style: map_style,
		center: [-77.030034, 38.92],
		showZoom: true,
		//pitch: 40,
		zoom: 11
	});

	map.addControl(new MapboxGeocoder({
		accessToken: mapboxgl.accessToken,
		mapboxgl: mapboxgl
	}));

	map.addControl(new mapboxgl.NavigationControl());

	map.on('load', function() {
		map.addLayer({
			"id": 'cycling-results',
			"type": "line",
			"source": {
				type: 'vector',
				url: 'mapbox://gwarrenn.dgwdb2ow'
			},
			"source-layer": "result",
			"layout": {
				"line-join": "round",
				"line-cap": "round"
			},
			"paint": {
				"line-color": ['match',['get','Commute'],'True','#f68f46','False','#e8fa5b','#ccc'],
				"line-width": 1,
				"line-opacity": .2
			},
			"filter": ["!=", "Commute", filter_value]
		})
	});
}

plot()