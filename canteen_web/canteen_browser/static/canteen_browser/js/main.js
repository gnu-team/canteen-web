// Main
// Constants
var GEORGIA_TECH_LOC = { lat: 33.779, lng: -84.398 };
var GEORGIA_TECH_ZOOM = 15;
var REPORT_TYPES = [
    'Bottled',
    'Well',
    'Stream',
    'Lake',
    'Spring',
    'Other'
];
var REPORT_CONDITIONS = [
    'Waste',
    'Treatable-Clear',
    'Treatable-Muddy',
    'Potable'
];

// Global variables
var drawnMap = active == 'map';
var map = null;

// Callback invoked by the Google Maps api js once it's loaded
function initMap() {
    map = new google.maps.Map($('#map')[0], {
        zoom: GEORGIA_TECH_ZOOM,
        center: GEORGIA_TECH_LOC
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

// If we initially load a screen other than map (e.g., reports), the
// template on the server side will set #map (the root Google Map
// container) to `display: none'. The Google Maps API seems to interpret
// this as drawing a 0px by 0px map. So when we make the map visible for
// the first time, only a blank gray screen is shown. To fix this, send
// a resize event to the Google Maps API and re-center the map.
function forceMapRedraw() {
    if (map != null) {
        drawnMap = true;
        google.maps.event.trigger(map, 'resize');
        map.setCenter(GEORGIA_TECH_LOC);
    }
}

function navigateTo(screen) {
    var oldNav = $('#nav-' + active);
    oldNav.removeClass('active');
    var newNav = $('#nav-' + screen);
    newNav.addClass('active');

    var oldContent = $('#' + active);
    oldContent.addClass('inactive');
    var newContent = $('#' + screen);
    newContent.removeClass('inactive');

    var newPath = ROOT_PATH;
    if (screen != ROOT_SCREEN) {
        newPath += screen + '/';
    }
    history.pushState({ screen: screen }, 'Screen ' + screen, newPath);

    // Hack to make the Google Map show up properly when it wasn't the
    // first screen loaded (see comment above forceMapRedraw() for more
    // info)
    if (screen == 'map' && !drawnMap) {
        forceMapRedraw();
    }

    active = screen;
}

function prettyDate(val) {
    return new Date(val).toString();
}

function addTableCol(row, val) {
    var entry = $('<td>');
    entry.text(val);
    row.append(entry);
}

function repopulateReportsTable() {
    var tbody = $('#reports tbody');
    tbody.empty();

    for (var i = 0; i < reports.length; i++) {
        var report = reports[i];

        var row = $('<tr>');
        addTableCol(row, report.id);
        addTableCol(row, prettyDate(report.date));
        addTableCol(row, REPORT_TYPES[report.type]);
        addTableCol(row, REPORT_CONDITIONS[report.condition]);
        addTableCol(row, report.creator_name);
        addTableCol(row, report.description);

        tbody.append(row);
    }
}

$(function () {
    ['map', 'reports'].forEach(function (val, i, arr) {
        $('#nav-' + val + ' a').on('click', function () {
            navigateTo(val);
            return false;
        });
    });

    $(window).on('popstate', function (e) {
        navigateTo(e.originalEvent.state.screen);
    });

    repopulateReportsTable();
});
