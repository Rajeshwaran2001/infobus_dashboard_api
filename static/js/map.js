

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
// Get the element whose class needs to be changed
const elementToChange = document.querySelector('.contain');

// Add event listener to each checkbox
checkboxes.forEach(function(checkbox) {
  checkbox.addEventListener('change', function() {
    if (this.checked) {

      // Clear any existing update interval
      clearInterval(updateInterval);

      // Start the update interval
      updateInterval = setInterval(fetchData, 20000);

      checkedValues.push(this.value);
      console.log(checkedValues);

      fetchData();

      // Show the map container
      document.querySelector('.map-container').style.display = 'block';

      // Change the class of the element
      elementToChange.classList.remove('col-lg-12', 'mb-md-0', 'mb-4');
      elementToChange.classList.add('col-lg-6', 'mb-md-0', 'mb-4');

    } else {
      const uncheckedBus = this.getAttribute('data-bus');
      checkedValues = checkedValues.filter(value => value !== this.value);
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

//  Fetch Api
function fetchData() {
  fetch('https://track.siliconharvest.net/get_status.php')
    .then(function(response) {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Network response was not ok');
      }
    })
    .then(function(data) {
      // console.log(data);
      // Filter out data with city: "Testing"
      const filteredData = data.filter((item) => item.city !== "Testing");
      // Filter out data that doesn't match the checkedValues
      const newPositions = filteredData.filter((item) => checkedValues.includes(item.bus_no))
                                .map((item) => {
                                  const [latitude, longitude] = item.position.split(",");
                                  return { bus_no: item.bus_no, latitude, longitude, route_name: item.route_name,
      date_time: item.date_time };
                                });
      console.log(newPositions);

      // Remove existing markers from the map
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
      label: {text: position.bus_no, color:"red", fontSize: "10px"},
      icon: {
        url: window.imageURL,
        scaledSize: new google.maps.Size(50, 50)
    }
    });

    // Create the info window content
    const infoWindowContent = `
      <div class="info-window">
        <h3> ${position.bus_no}</h3>
        <p>${position.route_name}</p>
        <p>${position.date_time}</p>
      </div>
    `;


    // Create the info window and attach it to the marker
    const infoWindow = new google.maps.InfoWindow({
      content: infoWindowContent,
    });

    marker.addListener('click', () => {
      infoWindow.open(map, marker);
    });

    markers.push(marker);
  }

        // Fit the map to the bounds of the markers, but only if there are multiple markers
        if (markers.length > 1) {
          const bounds = new google.maps.LatLngBounds();
          for (const marker of markers) {
            bounds.extend(marker.getPosition());
          }
          map.fitBounds(bounds);
        } else {
          // If there's only one marker, set the center and zoom level of the map based on that marker
          const position = markers[0].getPosition();
          map.setCenter(position);
          map.setZoom(15);
        }
      } else {
        console.error("No positions found.");
      }
    })
    .catch(function(error) {
      console.error('There was a problem with the fetch operation:', error);
    });
}
