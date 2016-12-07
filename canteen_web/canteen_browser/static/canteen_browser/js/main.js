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
var historyReportState = {
    latitude: null,
    longitude: null,
    year: null,
    isVirus: true,
};
var latLongState = {
    latitude: null,
    longitude: null
};
var addReportMgr = null;
var addPurityMgr = null;

function titleFor(screen) {
    return screen.charAt(0).toUpperCase() + screen.replace('_', ' ').slice(1);
}

function reportSummary(type, report, showDesc) {
    var result = prettyID(type, report.id);

    // (Source) report
    if (type == 'S') {
        result += ': ' + REPORT_CONDITIONS[report.condition] + ' ' + REPORT_TYPES[report.type];
    // Purity report
    } else if (type == 'P') {
        result += ': ' + PURITY_REPORT_CONDITIONS[report.condition];
    }

    if (showDesc && report.description)
        result += ': ' + report.description;

    return result;
}

function drawReports(map, reports, icon, type, showHistoryBtn) {
    for (var i = 0; i < reports.length; i++) {
        var report = reports[i];
        var marker = new google.maps.Marker({
            position: { lat: report.latitude, lng: report.longitude },
            icon: icon,
            map: map,
            title: reportSummary(type, report, true)
        });

        // Hack to escape HTML in description
        var safeDesc = $('<span />').text(report.description).html();
        var infoWindow = new google.maps.InfoWindow({
            content: '<strong>' + reportSummary(type, report, false) +
                     '</strong><br>' + report.latitude + ', ' +
                     report.longitude + '<p>' + safeDesc + '</p>' +
                     (showHistoryBtn? makeHistoryButton(report) : '')
        });

        // bind() is necessary to prevent the handler from referencing a
        // infoWindow or marker in a later loop iteration
        marker.addListener('click', function (infoWindow, marker) {
            infoWindow.open(map, marker);
        }.bind(this, infoWindow, marker));

        markers.push(marker);
    }
}

function setupMapEntry(subId, mgr) {
    $('#map-menu-' + subId).on('click', function () {
        hideMapMenu();
        mgr.show(latLongState.latitude, latLongState.longitude);
    });
}

function setupMapMenu() {
    setupMapEntry('report', addReportMgr);
    setupMapEntry('purity', addPurityMgr);
}

function hideMapMenu() {
    $('#map-menu').addClass('inactive');
}

function showMapMenu(x, y) {
    var menu = $('#map-menu');

    menu.removeClass('inactive');
    menu.css({
        left: x + 'px',
        top: y + 'px'
    });
}

function repopulateMapMarkers() {
    // Remove all existing markers
    while (markers.length > 0) {
        markers.pop().setMap(null);
    }

    drawReports(map, reports, REPORT_ICON, 'S', false);

    if (typeof purity_reports !== 'undefined')
        drawReports(map, purity_reports, PURITY_REPORT_ICON, 'P', true);
}

// Callback invoked by the Google Maps api js once it's loaded
function initMap() {
    map = new google.maps.Map($('#map')[0], {
        zoom: GEORGIA_TECH_ZOOM,
        center: GEORGIA_TECH_LOC
    });

    google.maps.event.addListener(map, 'rightclick', function (e) {
        latLongState.latitude = e.latLng.lat();
        latLongState.longitude = e.latLng.lng();
        showMapMenu(e.pixel.x, e.pixel.y);
    });
    google.maps.event.addListener(map, 'click', hideMapMenu);
    google.maps.event.addListener(map, 'dragstart', hideMapMenu);

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

function avg(values) {
    var sum = 0;
    var i = 0;

    while (values.length > 0) {
        sum += values.pop();
        i++;
    }

    return sum / i;
}

function averagePurityDuplicates(reports) {
    var lastMonth = -1;
    var virusVals = [];
    var contamVals = [];
    var virusData = new Array(12).fill(null);
    var contamData = new Array(12).fill(null);

    for (var i = 0; i <= reports.length; i++) {
        var report = null;
        var month = -1;

        if (i < reports.length) {
            report = reports[i];
            month = new Date(report.date).getMonth();
        }

        if (month != lastMonth && lastMonth != -1) {
            virusData[lastMonth] = avg(virusVals);
            contamData[lastMonth] = avg(contamVals);
        }

        if (i < reports.length) {
            lastMonth = month;

            virusVals.push(report.virusPPM);
            contamVals.push(report.contaminantPPM);
        }
    }

    return [virusData, contamData];
}

function drawHistoryChart(isVirus, reports, year) {
    var both = averagePurityDuplicates(reports);
    var data = isVirus? both[0] : both[1];

    var canvas = $('#historyReport-chart');
    var chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November',
                     'December'],
            datasets: [
                {
                    data: data,
                    spanGaps: true
                }
            ]
        },
        options: {
            legend: {
                display: false
            }
        }
    });
}

function fixHistoryReportTabs() {
    var virusTab = $('#historyReport-tab-virus');
    var contamTab = $('#historyReport-tab-contam');

    if (historyReportState.isVirus) {
        virusTab.addClass('active');
        contamTab.removeClass('active');
    } else {
        contamTab.addClass('active');
        virusTab.removeClass('active');
    }
}

function redrawHistoryReport() {
    var s = historyReportState;
    var path = NEARBY_PURITY_REPORT_ENDPOINT + s.latitude + ',' + s.longitude +
               '/?startDate=' + s.year + '-01-01' + '&endDate=' + s.year + '-12-31';

    $.ajax(path, {
        method: 'GET',
        success: function (data) {
            $('#historyReport-year').val(s.year);
            fixHistoryReportTabs();
            drawHistoryChart(s.isVirus, data, s.year);
        }
    });
}

function setupHistoryReportModal() {
    $('#historyReport-tab-virus').on('click', function () {
        historyReportState.isVirus = true;
        redrawHistoryReport();
    });
    $('#historyReport-tab-contam').on('click', function () {
        historyReportState.isVirus = false;
        redrawHistoryReport();
    });
    $('#historyReport-year').on('input', function () {
        historyReportState.year = parseInt($('#historyReport-year').val()),
        redrawHistoryReport();
    });
}

function AddModalManager(id, fields, endpoint, method, callback) {
    this.id = id;
    this.fields = fields;
    this.endpoint = endpoint;
    this.method = method;
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
        method: that.method,
        data: JSON.stringify(blob),
        success: function () {
            if (that.callback != null) {
                that.callback();
            }
            that.closeAddReport();
        },
        error: function (xhr, status, httpError) {
            that.handleAddReportError(xhr, status, httpError);
        }
    });
}

AddModalManager.prototype.show = function (lat, long) {
    this.get('latitude').val(lat);
    this.get('longitude').val(long);
    this.get('modal').modal('show');
}

function ProfileModalManager(id, fields, endpoint) {
    this.addMgr = new AddModalManager(id, fields, endpoint, 'PATCH', null);
    var that = this;

    this.addMgr.get('modal').on('show.bs.modal', function () {
        $.ajax(that.addMgr.endpoint, {
            method: 'GET',
            success: function (data) {
                that.addMgr.forEachField(function (field) {
                    that.addMgr.get(field).val(data[field]);
                });
            }
        });
    });
}

function prettyID(type, num) {
    // http://stackoverflow.com/a/20460414/321301
    return type + '-' + ('0000' + num).slice(-4);
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
        addTableCol(row, prettyID('S', report.id));
        addTableCol(row, prettyDate(report.date));
        addTableCol(row, REPORT_TYPES[report.type]);
        addTableCol(row, REPORT_CONDITIONS[report.condition]);
        addTableCol(row, report.creator_name);
        addTableCol(row, report.description);

        tbody.append(row);
    }
}

function historyButtonClicked(lat, long, year) {
    historyReportState.latitude = lat;
    historyReportState.longitude = long;
    historyReportState.year = year;

    $('#historyReport-modal').modal('show');
    redrawHistoryReport();
}

function makeHistoryButton(report) {
    var lat = report.latitude;
    var long = report.longitude;
    var year = new Date(report.date).getFullYear();

    return '<button type="button" class="btn btn-default" aria-label="Purity History" title="Purity History" onclick="historyButtonClicked(' + lat + ', ' + long + ', ' + year + ')"><span class="glyphicon glyphicon-stats" aria-hidden="true"></span></button>';
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
        addTableCol(row, prettyID('P', report.id));
        addTableCol(row, prettyDate(report.date));
        addTableCol(row, PURITY_REPORT_CONDITIONS[report.condition]);
        addTableCol(row, report.virusPPM);
        addTableCol(row, report.contaminantPPM);
        addTableCol(row, report.creator_name);
        addTableCol(row, report.description);

        var historyBtn = $(makeHistoryButton(report));
        row.append($('<td>').append(historyBtn));

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

    addReportMgr = new AddModalManager('#addReport',
                                       ADD_REPORT_FIELDS,
                                       ADD_REPORT_ENDPOINT,
                                       'POST', refreshReports);
    addPurityMgr = new AddModalManager('#addPurityReport',
                                       ADD_PURITY_REPORT_FIELDS,
                                       ADD_PURITY_REPORT_ENDPOINT,
                                       'POST', refreshPurityReports);
    new ProfileModalManager('#editProfile', PROFILE_FIELDS, PROFILE_ENDPOINT);

    setupHistoryReportModal();
    setupMapMenu();

    repopulateReportsTable();
    repopulatePurityReportsTable();
});
