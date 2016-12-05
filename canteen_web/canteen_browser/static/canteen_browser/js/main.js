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
var PURITY_REPORT_CONDITIONS = [
    'Safe',
    'Treatable',
    'Unsafe'
];

// Global variables
var markers = [];
var drawnMap = active == 'map';
var map = null;

function titleFor(screen) {
    return screen.charAt(0).toUpperCase() + screen.replace('_', ' ').slice(1);
}

function drawReports(map, reports, icon) {
    for (var i = 0; i < reports.length; i++) {
        var report = reports[i];
        markers.push(new google.maps.Marker({
            position: { lat: report.latitude, lng: report.longitude },
            icon: icon,
            map: map
        }));
    }
}

function repopulateMapMarkers() {
    // Remove all existing markers
    while (markers.length > 0) {
        markers.pop().setMap(null);
    }

    drawReports(map, reports, REPORT_ICON);

    if (typeof purity_reports !== 'undefined')
        drawReports(map, purity_reports, PURITY_REPORT_ICON);
}

// Callback invoked by the Google Maps api js once it's loaded
function initMap() {
    map = new google.maps.Map($('#map')[0], {
        zoom: GEORGIA_TECH_ZOOM,
        center: GEORGIA_TECH_LOC
    });

    repopulateMapMarkers();
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

    // Fix the title
    document.title = document.title.replace(titleFor(active), titleFor(screen));

    // Hack to make the Google Map show up properly when it wasn't the
    // first screen loaded (see comment above forceMapRedraw() for more
    // info)
    if (screen == 'map' && !drawnMap) {
        forceMapRedraw();
    }

    active = screen;
}

function AddModalManager(id, fields, endpoint, callback) {
    this.id = id;
    this.fields = fields;
    this.endpoint = endpoint;
    this.callback = callback;

    // Register handler for save button
    var that = this;
    this.get('save').on('click', function() { that.addReport(); });
}

// Get a child element by ID
AddModalManager.prototype.get = function (subId) {
    return $(this.id + '-' + subId);
}

AddModalManager.prototype.forEachField = function (f) {
    var that = this;
    Object.keys(this.fields).forEach(function (element, index, arr) {
        f.call(that, element, index, arr);
    });
}

AddModalManager.prototype.closeAddReport = function () {
    this.get('modal').modal('hide');

    // Blank out fields
    this.forEachField(function (field, filter) {
        var input = this.get(field);
        input.val('');
        // Undo error state of the wrapping form-group if present
        input.parent().removeClass('has-error');
    });
}

AddModalManager.prototype.handleAddReportError = function (xhr, status, httpError) {
    var data = xhr.responseJSON;

    var detailHelp = this.get('help');
    if (data.hasOwnProperty('detail')) {
        var error = data[field];
        detailHelp.text(error);
        detailHelp.removeClass('inactive');
    } else {
        detailHelp.addClass('inactive');
    }

    this.forEachField(function (field) {
        var formGroup = this.get(field).parent();
        var help = this.get('help-' + field);
        if (data.hasOwnProperty(field)) {
            var errors = data[field];
            // Set error state of wrapping form-group
            formGroup.addClass('has-error');
            // Show error message
            help.text(errors.join('; '));
            help.removeClass('inactive');
        } else {
            formGroup.removeClass('has-error');
            help.text('');
            help.addClass('inactive');
        }
    });
}

AddModalManager.prototype.addReport = function () {
    var blob = {};

    this.forEachField(function (field) {
        var filter = this.fields[field];
        var val = this.get(field).val();
        if (filter != null) {
            val = filter(val);
        }
        blob[field] = val;
    });

    var that = this;
    $.ajax(this.endpoint, {
        method: 'POST',
        data: JSON.stringify(blob),
        success: function () {
            that.callback();
            that.closeAddReport();
        },
        error: function (xhr, status, httpError) {
            that.handleAddReportError(xhr, status, httpError);
        }
    });
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

function repopulatePurityReportsTable() {
    var tbody = $('#purity_reports tbody');

    // If the purity reports screen wasn't written by the template
    // (i.e., if the user doesn't have sufficient permissions to view
    //  purity reports), give up now.
    if (tbody.length == 0)
        return;

    tbody.empty();

    for (var i = 0; i < purity_reports.length; i++) {
        var report = purity_reports[i];

        var row = $('<tr>');
        addTableCol(row, report.id);
        addTableCol(row, prettyDate(report.date));
        addTableCol(row, PURITY_REPORT_CONDITIONS[report.condition]);
        addTableCol(row, report.virusPPM);
        addTableCol(row, report.contaminantPPM);
        addTableCol(row, report.creator_name);
        addTableCol(row, report.description);

        tbody.append(row);
    }
}

function refreshReports() {
    $.ajax(ADD_REPORT_ENDPOINT, {
        method: 'GET',
        success: function (data, status, xhr) {
            reports = data;
            repopulateReportsTable();
            repopulateMapMarkers();
        }
    });
}

function refreshPurityReports() {
    $.ajax(ADD_PURITY_REPORT_ENDPOINT, {
        method: 'GET',
        success: function (data, status, xhr) {
            purity_reports = data;
            repopulatePurityReportsTable();
            repopulateMapMarkers();
        }
    });
}

$.ajaxSetup({
    // Send, expect JSON
    dataType: 'json',
    contentType: 'application/json; charset=UTF-8',

    // Send the CSRF token with every request
    // From: https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
        }
    }
});

$(function () {
    ['map', 'reports', 'purity_reports'].forEach(function (val, i, arr) {
        $('#nav-' + val + ' a').on('click', function () {
            navigateTo(val);
            return false;
        });
    });

    $(window).on('popstate', function (e) {
        navigateTo(e.originalEvent.state.screen);
    });

    new AddModalManager('#addReport', ADD_REPORT_FIELDS, ADD_REPORT_ENDPOINT,
                                      refreshReports);
    new AddModalManager('#addPurityReport', ADD_PURITY_REPORT_FIELDS,
                                            ADD_PURITY_REPORT_ENDPOINT,
                                            refreshPurityReports);

    repopulateReportsTable();
    repopulatePurityReportsTable();
});
