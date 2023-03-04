const districtDataElement = document.getElementById('district-data');
const districts = districtDataElement.getAttribute('data-districts').split(',');
//console.log(districts);

 // Declare a variable to store the interval ID
let updateInterval;

// Get all checkboxes with the "log-checkboxes" class
const checkboxes = document.querySelectorAll('.log-checkboxes');

// Initialize an empty array to store the checked checkbox values
let checkedValues = [];

let map;

// Initialize the map
function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 14,
    center: { lat: 9.939093, lng: 78.121719 }
  });
}
  window.onload = function() {
  // Load the Google Maps API
  var script = document.createElement('script');
  script.src = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyDbDh-8jCf6_K3ncfVCFpvBxu_Du4J5iy8&callback=initMap';
  document.body.appendChild(script);
};

// Get the element whose class needs to be changed
const elementToChange = document.querySelector('.contain');

// Add event listener to each checkbox
checkboxes.forEach(checkbox => {
  checkbox.addEventListener('change', () => {
    if (checkbox.checked) {

      // Clear any existing update interval
      clearInterval(updateInterval);

      // Start the update interval
      updateInterval = setInterval(fetchData, 20000);

      checkedValues.push(checkbox.value);
      console.log(checkedValues);

      fetchData(districts);

      // Show the map container
      document.querySelector('.map-container').style.display = 'block';

      // Change the class of the element
      elementToChange.classList.remove('col-lg-12', 'mb-md-0', 'mb-4');
      elementToChange.classList.add('col-lg-6', 'mb-md-0', 'mb-4');

    } else {
      const uncheckedBus = checkbox.getAttribute('data-bus');
      checkedValues = checkedValues.filter(value => value !== checkbox.value);
      console.log(checkedValues);

      // Remove the unchecked marker from the map
      markers = markers.filter(marker => {
        if (marker instanceof google.maps.Marker && marker.getTitle() === uncheckedBus) {
          marker.setMap(null);
          return false;
        }
        return true;
      });

      // Clear the update interval when all checkboxes are unchecked
      if (checkedValues.length === 0) {
        clearInterval(updateInterval);

        // Hide the map container
        document.querySelector('.map-container').style.display = 'none';

        // Change the class of the element
        elementToChange.classList.remove('col-lg-6', 'mb-md-0', 'mb-4');
        elementToChange.classList.add('col-lg-12', 'mb-md-0', 'mb-4');
      }
    }
  });
});

let markers = [];

async function fetchData(districts) {
  const urls = [
    'https://track.siliconharvest.net/get_status.php',
    'https://delta.busads.in/get_status.php',
    'https://tvl.busads.in/get_status.php',
  ];

  try {
    const responses = await Promise.all(urls.map(url => fetch(url)));
    const data = await Promise.all(responses.map(response => response.json()));
    const allData = data.flat();
    //console.log('Districts:', districts);
const filteredData = allData.filter(item => item.city !== 'Testing' &&
    (Array.isArray(districts) ? districts.includes(item.city) : false));
//console.log('Filtered Data:', filteredData);
    const newPositions = filteredData.filter(item => checkedValues.includes(item.bus_no))
      .map(item => {
        const [latitude, longitude] = item.position.split(',');
        return { bus_no: item.bus_no, latitude, longitude, station: item.station, date_time: item.date_time };
      });
    console.log(newPositions);
    //console.log(data)

    markers.forEach(marker => {
      if (marker instanceof google.maps.Marker) {
        marker.setMap(null);
      }
    });
    markers = [];

    if (newPositions.length > 0) {
      for (const position of newPositions) {
        const marker = new google.maps.Marker({
          position: { lat: parseFloat(position.latitude), lng: parseFloat(position.longitude) },
          map,
          title: position.bus_no,
          label: { text: position.bus_no, color: 'red', fontSize: '10px' },
          icon: {
            url: window.imageURL,
            scaledSize: new google.maps.Size(50, 50),
          },
        });

        const infoWindowContent = `
          <div class="info-window">
            <h3> ${position.bus_no}</h3>
            <p>${position.station}</p>
            <p>${position.date_time}</p>
          </div>
        `;

        const infoWindow = new google.maps.InfoWindow({
          content: infoWindowContent,
        });

        marker.addListener('click', () => {
          infoWindow.open(map, marker);
        });

        markers.push(marker);
      }

      if (markers.length > 1) {
        const bounds = new google.maps.LatLngBounds();
        for (const marker of markers) {
          bounds.extend(marker.getPosition());
        }
        map.fitBounds(bounds);
      } else if (markers.length === 1) {
        const position = markers[0].getPosition();
        if (map) {
          map.setCenter(position);
          map.setZoom(15);
        }
      } else {
        console.error('No positions found.');
      }
    }
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
}
