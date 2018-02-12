/*jshint esversion: 6 */

// Coses de ser un template de django, ho emple amb les url correctes
var facusURL = "{% url 'facus' %}";
var cuatrisURL = "{% url 'listq' %}";
var carrerasURL = "{% url 'listcarr' %}";
var asignaturasURL = "{% url 'listassig' %}";


var asignaturas = {};
var assig_TOT = {};
var actual = 0;
var horarios = [[]];

function emptyopt() {
  return "<option value='' disabled selected>Tria</option>";
}

function emptyLi() {
  return "<li class=\"collection-item\">Encara no has afegit cap assignatura</li>";
}

function genLi(key, list) {
  list.append(`<li class="collection-item" asID="${asignaturas[key]}"><div>${key}<a href="#!" class="secondary-content"><i class="material-icons red-text">delete</i></a></div></li>`);
  var li = list.find("[asID='" + asignaturas[key] + "']");
  li.find('a').click(function () {
    var p = $(this).parent();
    var t = p.children().remove().end().text();
    delete asignaturas[t];
    updateAssigList();
  });
}

function updateCarreras() {
  var id = $("#facultad").val();
  updateSelect("#cuatri", cuatrisURL + "?f=" + id);
  updateSelect("#carrera", carrerasURL + "?f=" + id);
}

function updateAssignatura() {
  var cuatri = $("#cuatri").val();
  if (cuatri !== null) {
    var carrera = $("#carrera").val();
    if (carrera !== null) {
      $.getJSON(asignaturasURL + "?c=" + carrera + "&q=" + cuatri, function (data) {
        var mydict = {};
        assig_TOT = data;
        for (var key in data) {
          mydict[key] = null;
        }
        $('#asignatura').autocomplete({
          data: mydict,
          limit: 20, // The max amount of results that can be shown at once. Default: Infinity.
          minLength: 1, // The minimum length of the input for the autocomplete to start. Default: 1.
        });
        $('#asignatura').removeAttr("disabled");
      });
    }
  }
}

function updateSelect(id, url) {
  var me = $(id);
  me.empty();
  me.append(emptyopt());
  console.log("Updating " + id);
  $.getJSON(url, function (data) {
    for (var key in data) {
      me.append(`<option value="${data[key]}">${key}</option>`);
    }
    me.removeAttr("disabled");
    me.material_select();
  });
}

function updateAssigList() {
  var list = $("#assigList");
  list.empty();
  if (Object.keys(asignaturas).length === 0) list.append(emptyLi);
  else {
    for (var key in asignaturas) {
      genLi(key, list);
    }
  }
}

function genform() {
  var form = $('#form_assig');

  updateSelect("#facultad", facusURL);
  $("#facultad").change(updateCarreras);
  $("#carrera").change(updateAssignatura);
  $("#cuatri").change(updateAssignatura);

  $("select").material_select();
}

function renderCal() {

  $("#calendar").fullCalendar("removeEvents");
  $("#calendar").fullCalendar("renderEvents", horarios[actual]);
  //$(".calholder").show();
  var n = actual + 1;
  $("#cal_txt").text(n.toString() + "/" + horarios.length.toString());

}

function genHorario() {
  if (Object.keys(asignaturas).length === 0) alert("Has d'afegir alguna assignatura!");
  else if ($("#hora_inici").prop('checked') && $("#time_start").val() != "") alert("Hora d'inici incorrecta");
  else if ($("#hora_fi").prop('checked') && $("#time_end").val() != "") alert("Hora de finalització incorrecta");
  else {
    $(".horloader").removeClass("hide");
    $(".horloader").show();
    $(".btn_holder").hide();
    //$(".calholder").hide();
    var txt = $('#loading_txt');
    txt.text('Conectando al servidor...');

    //Llista de filtres amb estat
    filterList = {};
    filterList["solapaments"] = $("#solapaments").prop('checked');
    filterList["dinar"] = $("#puc_dinar").prop('checked');
    filterList["inici"] = $("#hora_inici").prop('checked');
    filterList["fi"] = $("#hora_inici").prop('checked');

    fData = {};
    fData["inici"] = $("#time_start").val();
    fData["fi"] = $("#time_end").val();

    filters = { "list": filterList, "data": fData };


    // Fix for https connections
    if (window.location.protocol == "https:") ws = new WebSocket('wss://' + window.location.host + '/');
    else ws = new WebSocket('ws://' + window.location.host + '/');

    // Send data when websocket is opened
    ws.onopen = function () {
      txt.text('Enviando datos');
      ws.send(JSON.stringify({ "assignatures": asignaturas, "filters": filters }));
    };

    ws.onmessage = function (message) {
      console.log(message.data);
      if ($(".indeterminate").length) {
        $(".indeterminate").addClass("determinate");
        $(".indeterminate").removeClass("indeterminate");
      }
      data = JSON.parse(message.data);
      if (!data.completed) {
        $(".determinate").attr("style", "width: " + data.progress.toString() + "%");
        txt.text(data.text);
        if (data.progress == 100) $(".btn_holder").show();
      } else {
        horarios = data.horaris;
        actual = 0;
        $("#bt_next").show();
        $("#bt_prev").hide();
        $("#modal-horaris").modal("open");
        //$("#bt_prev").hide();
        $(".horloader").hide();
        $(".btn_holder").show();
      }
    };
  }
}


$(document).ready(function () {
  // $('select').material_select();
  $('#calendar').fullCalendar({
    editable: false,
    handleWindowResize: true,
    weekends: false, // Hide weekends
    defaultView: 'agendaWeek', // Only show week view
    header: false, // Hide buttons/titles
    allDaySlot: false,
    minTime: '08:00:00', // Start time for the calendar
    maxTime: '21:00:00', // End time for the calendar
    columnFormat: 'dddd',
    displayEventTime: true,
    height: 'auto',
    firstDay: 1
  });
  //$(".calholder").hide();
  genform();
  updateAssigList();

  //init modals
  $('.modal').modal();
  $('#modal-horaris').modal({
    ready: function (modal, trigger) {
      renderCal(); // La primera no la fa be i cal fer una segona passada
      renderCal();
    }
  })

  //Init Collapsibles
  $('.collapsible').collapsible();
  //Init date pickers
  $('.timepicker').pickatime({
    twelvehour: false, // Use AM/PM or 24-hour format
    donetext: 'OK', // text for done-button
    cleartext: 'Esborrar', // text for clear-button
    canceltext: 'Sortir', // Text for cancel-button
  });

  $("#btn_gen").click(genHorario);


  $("#bt_next").click(function (event) {
    if (actual + 1 < horarios.length) {
      actual++;
      $("#bt_prev").show();
      if (actual + 1 == horarios.length) {
        $("#bt_next").hide();
      }
      renderCal();
    }
  });
  $("#bt_prev").click(function (event) {
    if (actual > 0) {
      actual--;
      $("#bt_next").show();
      if (actual == 0) {
        $("#bt_prev").hide();
      }
      renderCal();
    }
  });


  $("#form_assig").submit(function (event) {
    console.log("JALR");
    var name = $("#asignatura").val();
    $("#asignatura").val("");
    $("#asignatura").next().removeClass("active");
    if (assig_TOT[name] === undefined) {
      alert("L'assignatura no existeix");
    } else {
      asignaturas[name] = assig_TOT[name];
      updateAssigList();
    }
    event.preventDefault();
  });
});
