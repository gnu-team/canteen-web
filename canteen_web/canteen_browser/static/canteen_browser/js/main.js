// Main
var GEORGIA_TECH_LAT = 33.779;
var GEORGIA_TECH_LONG = -84.398;
var GEORGIA_TECH_ZOOM = 15;

// Callback invoked by the Google Maps api js once it's loaded
function initMap() {
    var map = new google.maps.Map($('#map')[0], {
        zoom: GEORGIA_TECH_ZOOM,
        center: { lat: GEORGIA_TECH_LAT, lng: GEORGIA_TECH_LONG }
    });

    for (var i = 0; i < reports.length; i++) {
        var report = reports[i];
        new google.maps.Marker({
            position: { lat: report.latitude, lng: report.longitude },
            icon: REPORT_ICON,
            map: map
        });
    }
}

function addCol(row, val) {
    var entry = $('<td>');
    entry.text(val);
    row.append(entry);
}

$(function () {
    var tbody = $('#reports tbody');
    tbody.empty();

    for (var i = 0; i < reports.length; i++) {
        var report = reports[i];

        var row = $('<tr>');
        addCol(row, report.id);
        addCol(row, report.description);

        tbody.append(row);
    }
});
