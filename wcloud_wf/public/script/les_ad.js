(function les(){
	if(!!$.cookie("org_session_id")){
		if(!!$.cookie("configStatus")){
			location.href='/f_org_home';
		}else{
			location.href='/f_org_setLDAP';
		}
	}
})();