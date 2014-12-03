

var attempt = 3;
function validate(){
var username = document.getElementById("username").value;
var password = document.getElementById("password").value;
if ( username == "alex" && password == "america670"){
alert ("Login successfully");
window.location = "success.html";
return false;
}
else{
attempt = attempt - 1;
alert("You have "+attempt+" attempts left");

if( attempt === 0){
document.getElementById("username").disabled = true;
document.getElementById("password").disabled = true;
document.getElementById("submit").disabled = true;
return false;
}
}
}

