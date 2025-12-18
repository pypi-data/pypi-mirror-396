var testsuiteJSON = {};

testsuiteJSON.parse = function (file){ 
  var request = new XMLHttpRequest();
  request.open("GET", file, false);
  request.send(null);
  var record = JSON.parse(request.responseText);
  return record;
}

testsuiteJSON.contains = function(obj, key, value){
  var str=JSON.stringify(obj)
  var m = str.search(key+"\":\""+value);
  var n = str.search(key+"\":"+value);
  return( n!=-1 || m!=-1)
}

testsuiteJSON.occurences = function(string, subString, allowOverlapping) {

    string += "";
    subString += "";
    if (subString.length <= 0) return (string.length + 1);

    var n = 0,
        pos = 0,
        step = allowOverlapping ? 1 : subString.length;

    while (true) {
        pos = string.indexOf(subString, pos);
        if (pos >= 0) {
            ++n;
            pos += step;
        } else break;
    }
    return n;
}

testsuiteJSON.containSum = function(obj, key, value){
  var sum=0
  var str=JSON.stringify(obj)
  var c1=(key+"\":\""+value)
  var c2=(key+"\":"+value);
  var count = testsuiteJSON.occurences(str, c1) + testsuiteJSON.occurences(str, c2)
  return count
}

testsuiteJSON.setUrl = function (name, page, param, sort=0, tooltip=""){
  var paramList="?";
  for (i in param){
    paramList=paramList+i+"="+param[i]+"&"
  }
  hoover=""
  if (tooltip !=""){
    hoover=" data-toggle=\"tooltip\" title=\""+tooltip+"\""
  }
  paramList = paramList.slice(0, -1)
  link="<a href=\""+page+paramList+"\""+hoover+">"+name+"</a>"
  if (sort==0){
    return link
  }else{
    return "<div sort=\""+sort+"\">"+link
  }
}

testsuiteJSON.getParameter = function(variable) {
   var query = window.location.search.substring(1);
   var vars = query.split("&");
   for (var i=0;i<vars.length;i++) {
           var pair = vars[i].split("=");
           if(pair[0] == variable){return pair[1];}
   }
   return(false);
};

testsuiteJSON.concatenate = function(obj, sep=" ") {
  var str="";
  for (i in obj){
    str+=obj[i]+sep;
  }
  if (str.length > 0){
    str = str.slice(0, -sep.length);
  }
  return str;
}


testsuiteJSON.upFirst = function(string) 
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

testsuiteJSON.mailToName = function(obj, sep=" ") {
  for (i in obj){
    var str=obj[i]
    try{
      obj[i]=obj[i].split("@")
      var l=obj[i][0].split(".")
      obj[i]=testsuiteJSON.upFirst(l[0]) +" "+l[1].charAt(0).toUpperCase()+"."
    }
    catch(err){
      obj[i]=str
    }
  }
  return obj;
}

testsuiteJSON.sizeOf = function(obj) {
  var size=0
  for (i in obj){
    size++
  }
  return size;
}

testsuiteJSON.popUp = function(text, popUpText, id){
 var str="<div class=\"popup\" onclick=\"testsuiteJSON.popUpFunction(" + id + ")\">" + text + "<span class=\"popuptext\" id=\""+id+"\">"+popUpText+"</span></div>"
  return str
}

testsuiteJSON.popUpFunction = function(id){
  var popup = document.getElementById(id);
  popup.classList.toggle("show");
}



testsuiteJSON.OK = "<img src=\"img/png/success.png\" alt=\"OK\" height=\"24\" width=\"24\">"
testsuiteJSON.KO = "<img src=\"img/png/failed.png\" alt=\"KO\" height=\"24\" width=\"24\">"
testsuiteJSON.WARNING = "<img src=\"img/png/warning.png\" alt=\"WARNING\" height=\"24\" width=\"24\">"
testsuiteJSON.SKIPPED = "<img src=\"img/png/skipped.png\" alt=\"SKIPPED\" height=\"24\" width=\"24\">"
testsuiteJSON.TOL = "<img src=\"img/png/tolerance.png\" alt=\"TOL\" height=\"24\" width=\"24\">"
testsuiteJSON.TIME = "<img src=\"img/png/timeout.png\" alt=\"TIME\" height=\"24\" width=\"24\">"

testsuiteJSON.SYS_KO = "<img src=\"img/png/canceled.png\" alt=\"SYS\" height=\"24\" width=\"24\">"
testsuiteJSON.SYS_BINDING = "<img src=\"img/png/created.png\" alt=\"SYS\" height=\"24\" width=\"24\">"
testsuiteJSON.SYS_WEIGHT = "<img src=\"img/png/created.png\" alt=\"SYS\" height=\"24\" width=\"24\">"

testsuiteJSON.OK_BLACK = "<img src=\"img/png/success_black.png\" alt=\"OK\" height=\"24\" width=\"24\">"
testsuiteJSON.KO_BLACK = "<img src=\"img/png/failed_black.png\" alt=\"KO\" height=\"24\" width=\"24\">"
testsuiteJSON.WARNING_BLACK = "<img src=\"img/png/warning_black.png\" alt=\"WARNING\" height=\"24\" width=\"24\">"

testsuiteJSON.KO_GREEN = "<img src=\"img/png/failed_green.png\" alt=\"KO\" height=\"24\" width=\"24\">"
testsuiteJSON.WARNING_GREEN = "<img src=\"img/png/warning_green.png\" alt=\"WARNING\" height=\"24\" width=\"24\">"

testsuiteJSON.FILE_CONFIG = "<img src=\"img/png/file_config.png\" alt=\"FILE\" height=\"24\" width=\"24\">"
testsuiteJSON.FILE_OK = "<img src=\"img/png/file_ok.png\" alt=\"FILE\" height=\"24\" width=\"24\">"
testsuiteJSON.FILE_KO = "<img src=\"img/png/file_ko.png\" alt=\"FILE\" height=\"24\" width=\"24\">"
testsuiteJSON.FILE_CLOUD = "<img src=\"img/png/file_cloud.png\" alt=\"FILE\" height=\"24\" width=\"24\">"

testsuiteJSON.LOGO = "<img src=\"img/png/squidient_logo.png\" alt=\"FILE\" height=\"48\" width=\"48\">"

testsuiteJSON.reports = "../reports/"
testsuiteJSON.builds = testsuiteJSON.reports+"builds/"
testsuiteJSON.tests = testsuiteJSON.reports+"tests/"
testsuiteJSON.cc = testsuiteJSON.reports+"cc/"
testsuiteJSON.benchmark_builds = testsuiteJSON.reports+"benchmark_builds/"
testsuiteJSON.benchmark_tests = testsuiteJSON.reports+"benchmark_tests/"
testsuiteJSON.cc_dir = testsuiteJSON.cc+"CodeCoverage/"
