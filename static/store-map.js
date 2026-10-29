function openStoreMap() {
  /* Hängt die Supermarkt-Fahnen an die Karte, damit sie beim Verschieben mitwandern. */
  var mapElement = document.getElementById("store-map");
  var markerRoot = document.getElementById("store-markers");
  if (!mapElement || !markerRoot || typeof L === "undefined") {
    return;
  }

  document.addEventListener("click", function (event) {
    var flag = event.target.closest(".store-flag");
    if (!flag) {
      return;
    }
    var open = flag.classList.contains("is-open");
    document.querySelectorAll(".store-flag.is-open").forEach(function (other) {
      other.classList.remove("is-open");
    });
    if (!open) {
      flag.classList.add("is-open");
    }
  }, true);

  var latitude = Number(mapElement.dataset.lat);
  var longitude = Number(mapElement.dataset.lng);
  var zoom = Number(mapElement.dataset.zoom) || 12;
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return;
  }

  var map = L.map(mapElement, { scrollWheelZoom: true, zoomControl: true }).setView([latitude, longitude], zoom);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  markerRoot.hidden = false;
  markerRoot.style.position = "absolute";
  markerRoot.style.left = "-10000px";
  markerRoot.querySelectorAll(".store-flag").forEach(function (flag) {
    var pointLatitude = Number(flag.dataset.lat);
    var pointLongitude = Number(flag.dataset.lng);
    if (!Number.isFinite(pointLatitude) || !Number.isFinite(pointLongitude)) {
      return;
    }
    var bounds = flag.getBoundingClientRect();
    var width = Math.ceil(bounds.width) || 80;
    var height = Math.ceil(bounds.height) || 56;
    L.marker([pointLatitude, pointLongitude], {
      icon: L.divIcon({
        className: "store-marker",
        html: flag,
        iconSize: [width, height],
        iconAnchor: [2, height]
      }),
      keyboard: false
    }).addTo(map);
  });
  markerRoot.remove();
  mapElement.storeMap = map;
}

openStoreMap();
