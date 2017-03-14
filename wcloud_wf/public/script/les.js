(function les(){
	$(document.body).addClass("lgp");
	if(!!$.cookie("session_id")){
		location.href='/f_per_device';
	}
})();