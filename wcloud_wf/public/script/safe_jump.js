var timeFly=180000;   //5秒
var activeDt=new Date();

$(document).keypress(function(){
    reTime();
});
$(document).mousedown(function(){
    reTime();
});
$(document).mousemove(function(){
    reTime();
});

setInterval('checkTime()',1000);

function reTime(){
    activeDt=new Date();
}
function checkTime(){
    var dt=new Date();
    if ((dt - activeDt) > timeFly) {
        logoutRe();
    }
}
function logoutRe(){
    var sid=$.cookie("org_session_id");
    var obj={
        _path:'/a/wp/org/logout',
        _methods:'post',
        param:{
            sid:sid
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        if(rt==0){
            loadingStatus("正在退出...",0);
            $.cookie("org_session_id",null);
            $.cookie("configStatus",null);
            location.href="/f_org_login";
        }else{
            loadingStatus("操作失败!",0);
        }
    },"正在退出...");
}
