mapboxgl.accessToken = 'pk.eyJ1IjoiZ3dhcnJlbm4iLCJhIjoiY2p4d294Z2xhMGh4czNub2N1c202dnNvdCJ9.iRGx2PURnTzXBHgRIH2zKg';

const plot = async () => {

  // Mapping
  const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v10',
    center: [-77.030034, 38.901863],
    zoom: 11
  });

  map.on('load', function() {
    //loop through each geojson value
    for (var j = 0; j < data.length; j++) {
      map.addLayer({
        "id": data[j].properties.Name,
        "type": "line",
        "source": { 
          "type": "geojson",
          "data": data[j]
        },
        "layout": {
          "line-join": "round",
          "line-cap": "round"
        },
        "paint": {
          "line-color": "#FF9933",
          "line-width": 2,
          "line-opacity": .2
        }
      })
    } 
  });
}

plot()