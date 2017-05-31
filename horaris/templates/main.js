/*jshint esversion: 6 */

var facusURL = "{% url 'facus' %}";
var cuatrisURL = "{% url 'listq' %}";
var carrerasURL = "{% url 'listcarr' %}";
var asignaturasURL = "{% url 'listassig' %}";


var asignaturas = {};
var assig_TOT = {};

function emptyopt(){
  return   "<option value='' disabled selected>Elige</option>";
}

function emptyLi(){
  return "<li class=\"collection-item\">Aún no has añadido ninguna asignatura</li>";
}

function genLi(key,list){
  list.append(`<li class="collection-item" asID="${asignaturas[key]}"><div>${key}<a href="#!" class="secondary-content"><i class="material-icons red-text">delete</i></a></div></li>`);
  var li = list.find("[asID='"+asignaturas[key]+"']");
  li.find('a').click(function(){
  var p = $(this).parent();
  var t = p.children().remove().end().text();
  delete asignaturas[t];
  updateAssigList();
  });
}

function updateCarreras(){
  var id = $("#facultad").val();
  updateSelect("#cuatri", cuatrisURL + "?f="+id);
  updateSelect("#carrera", carrerasURL + "?f="+id);
}

function updateAssignatura(){
  var cuatri = $("#cuatri").val();
  if(cuatri !== null){
    var carrera = $("#carrera").val();
    if(carrera !== null){
      $.getJSON(asignaturasURL+"?c="+carrera+"&q="+cuatri, function(data){
        var mydict = {};
        assig_TOT = data;
        for(var key in data){
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

function updateSelect(id, url){
  var me = $(id);
  me.empty();
  me.append(emptyopt());
  console.log("Updating "+id);
  $.getJSON(url, function(data){
    for(var key in data){
      me.append(`<option value="${data[key]}">${key}</option>`);
    }
    me.removeAttr("disabled");
    me.material_select();
  });
}

function updateAssigList(){
  var list = $("#assigList");
  list.empty();
  if(Object.keys(asignaturas).length === 0) list.append(emptyLi);
  else{
    for(var key in asignaturas){
      genLi(key,list);
    }
  }
}

function genform(){
  var form= $('#form_assig');

  updateSelect("#facultad",facusURL);
  $("#facultad").change(updateCarreras);
  $("#carrera").change(updateAssignatura);
  $("#cuatri").change(updateAssignatura);

  $("select").material_select();
}


function genHorario(){
  if(Object.keys(asignaturas).length === 0) alert("Has de añadir alguna asignatura!");
  else{
    $(".horloader").removeClass("hide");
    $(".btn_holder").hide();
    var txt = $('#loading_txt');
    txt.text('Conectando al servidor...');
    ws = new WebSocket('wss://'+window.location.host+'/');

    // Send data when websocket is opened
    ws.onopen = function() {
      txt.text('Enviando datos');
      ws.send(JSON.stringify(asignaturas));
    };

    ws.onmessage = function(message) {
      console.log(message.data);
      if($(".indeterminate").length) {
        $(".indeterminate").addClass("determinate");
        $(".indeterminate").removeClass("indeterminate");
      }
      data = JSON.parse(message.data);
      $(".determinate").attr("style","width: "+data.progress.toString()+"%");
      txt.text(data.text);
    };
  }
}


$(document).ready(function() {
  // $('select').material_select();
  // $('#calendar').fullCalendar({
  //   editable: false,
  //   handleWindowResize: true,
  //   weekends: false, // Hide weekends
  //   defaultView: 'agendaWeek', // Only show week view
  //   header: false, // Hide buttons/titles
  //   minTime: '07:30:00', // Start time for the calendar
  //   maxTime: '22:00:00', // End time for the calendar
  //   columnFormat: {
  //       week: 'ddd' // Only show day of the week names
  //   },
  //   displayEventTime: true,
  //   allDayText: 'Online/TBD'
  // });
  genform();
  updateAssigList();

  $("#btn_gen").click(genHorario);

  $("#form_assig").submit(function( event ) {
    console.log("JALR");
    var name = $("#asignatura").val();
    if(assig_TOT[name] === undefined){
      alert("La asignatura no existe");
    }
    else{
      asignaturas[name] = assig_TOT[name];
      updateAssigList();
    }
    event.preventDefault();
  });
});
