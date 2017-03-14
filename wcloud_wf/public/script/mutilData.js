function sendMessInfo(){
  var target=document.getElementById('pop_mesInfo');
  target.style.display="";
  document.getElementById("back").style.display="";
}

$("#cancleMes").live('click',function(event){
    $("#pop_mesInfo").hide();
    document.getElementById("back").style.display="none";
});
function fakeCallInfo(){
  var target=document.getElementById('pop_fakeCall');
  target.style.display="";
  document.getElementById("back").style.display="";

}

$("#cancleCall").live('click',function(event){
    $("#pop_fakeCall").hide();
    document.getElementById("back").style.display="none";
});
function addWhite(){
}