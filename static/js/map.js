let positions = [];
 console.log(positions)

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
      //console.log(data);
      // Filter out data with city: "Testing"
      const filteredData = data.filter((item) => item.city !== "Testing");
      // Filter out data that doesn't match the checkedValues
      positions = filteredData.filter((item) => checkedValues.includes(item.bus_no))
                                .map((item) => {
                                  const [latitude, longitude] = item.position.split(",");
                                  return { bus_no: item.bus_no, latitude, longitude };
                                });
      console.log(positions);
      // Call the initMap function here
        initMap();
    })
    .catch(function(error) {
      console.error('There was a problem with the fetch operation:', error);
    });
}

function initMap() {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 17,
  });

  if (positions.length > 0 && !isNaN(positions[0].latitude) && !isNaN(positions[0].longitude)) {
    map.setCenter({ lat: parseFloat(positions[0].latitude), lng: parseFloat(positions[0].longitude) });
  } else {
    console.error("No valid positions found.");
    return;
  }

  if (positions.length > 0) {
    for (const position of positions) {
      if (!isNaN(position.latitude) && !isNaN(position.longitude)) {
        const marker = new google.maps.Marker({
          position: { lat: parseFloat(position.latitude), lng: parseFloat(position.longitude) },
          map,
          title: position.bus_no,
        });
      }
    }
  } else {
    console.error("No positions found.");
  }
}
    // Get all checkboxes with the "log-checkboxes" class
  const checkboxes = document.querySelectorAll('.log-checkboxes');

    // Initialize an empty array to store the checked checkbox values
let checkedValues = [];

  // Add event listener to each checkbox
  checkboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
      if (this.checked)
        console.log(this.value)
        checkedValues.push(this.value);
      console.log(checkedValues)
        if (checkbox.checked) {
            fetchData();
            //initMap();
        } else {
          result.textContent = '';
        }
      });
  });
