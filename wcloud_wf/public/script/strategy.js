var start_time = $("#start_time");
var end_time = $("#end_time");
var desc = $("#desc");
var location_j = $("#location_j");
var location_w = $("#location_w");
var radius = $("#radius");
var baseStationID = $("#baseStationID");
var camera = $("#camera");
//var bluetooth = $("#bluetooth");
var wifi = $("#wifi");
var tape = $("#tape");
var gps = $("#gps");
var mobiledata = $("#mobiledata");
var usb_connect = $("#usb_connect");
var usb_debug = $("#usb_debug");
var stra_fast_choice = $("#stra_fast_choice");
var groups;

//+++ 20150629 加入强制控制逻辑
var forceConfig = document.getElementById("forceControl");
function forceControlChange(){
    if(forceConfig.className=="checkbox checkbox_uncheck"){
        //将值设置为空和禁用
        start_time.val('');
        end_time.val('');
        location_j.val('');
        location_w.val('');
        baseStationID.val('');
        radius.val('');
        //禁用所有设备
        controlDevices("jy");
        //禁止对于策略选项进行更改
        disableInput(true);
    }else{
        //解禁所有设备
        controlDevices("fjy");
        defaultInputs();
        disableInput(false);
    }

}
function controlDevices(cmd){
    camera.val("c"+cmd)
    //bluetooth.val('b'+cmd);
    tape.val('t'+cmd);
    gps.val('g'+cmd);
    wifi.val('w'+cmd);
    mobiledata.val('m'+cmd);
    usb_connect.val('uc'+cmd);
    usb_debug.val('ud'+cmd);
}
//+++20150630 修改初始化时间格式
function defaultInputs(){
    var mydate = new Date();
    var start = getFriendlyString(mydate);
    var tomorrow = getAnotherDay(mydate,1);
    var end = getFriendlyString(tomorrow);
    document.getElementById('start_time').value=start;
    document.getElementById('end_time').value=end;
    document.getElementById('location_j').value="113.351021";
    document.getElementById('location_w').value="23.131864";
    document.getElementById('radius').value="1000";
    document.getElementById('desc').value="广州市联通广场";
    document.getElementById("strategy_con").style.display="block";

    choiceBaseStation();
}
//+++20150630 获得友好的时间格式
//输入mydate是今天的日期格式
function getFriendlyString(mydate){
    var year = mydate.getFullYear();
    var month ='00'+ (mydate.getMonth()+1);
    var date ='00'+ mydate.getDate()
    var str = year+"-"+month.substr(-2)+"-"+date.substr(-2)+" 00:00";
//    var end  = year+"-"+month.substr(-2)+"-"+(parseInt(date.substr(-2))+1)+" 00:00";
    return str;
}

//20150630 获得与输入时间相隔几天的一个时间
//输入参数mydate是日期格式的今天，dates是和今天相差的天数
function getAnotherDay(mydate,dates){
    var nowTime = mydate.getTime();
    var oneDayMillSec = 1*24*60*60*1000;
    var anotherDayMillSec = nowTime + dates*oneDayMillSec;
    var anotherDay = new Date(anotherDayMillSec);
    return anotherDay;
}
//+++20150629 禁用和解禁填充值
//config 取bool值，true为禁用，false为非禁用
function disableInput(config){
    start_time.attr("disabled",config);
    end_time.attr("disabled",config);
    location_j.attr("disabled",config);
    location_w.attr("disabled",config);
    baseStationID.attr("disabled",config);
    radius.attr("disabled",config);
//  +++20150827 摄像头和录音功能默认禁用，不能修改
//    camera.attr("disabled",config);
    //bluetooth.attr("disabled",config);
//    tape.attr("disabled",config);
    gps.attr("disabled",config);
    wifi.attr("disabled",config);
    mobiledata.attr("disabled",config);
    usb_connect.attr("disabled",config);
    usb_debug.attr("disabled",config);
    stra_fast_choice.attr("disabled",config);
}

$("#celveBn").live('click',function(event) {
    event.preventDefault;
    var val=$("#strategy_con #strategy_N #celveBn").html();
    if(val=="策略下发"){
        var path = '/a/wp/user/send_strategy';
        var status1="策略下发中...";
        var status2="策略配置失败!";
        var status3="当前策略作用人群中存在用户不在线，为确保策略下发，请使用短信下发策略！";
    }

    //sms send 20150408
    if(val=="短信下发"){
        var path = '/a/wp/user/send_strategy_sms';
        var status1="策略下发中...";
        var status2="策略配置失败!";
    }
    /**************/

    var id = getStrategyID();
    var oldid = '';

    if(val=="确定修改"){
        id = document.getElementById('start_time').className;
        path = '/a/wp/user/modify_strategy';
        status1="修改策略指令下发中...";
        status2="下发修改策略信息命令失败!";
        status3="当前策略作用人群中存在用户不在线，不能执行修改操作，可使用短信重新下发策略！";
    }
    var force =0;
    //各种判断
    if(forceConfig.className=="checkbox checkbox_uncheck"){
        //判定结束时间是否已经过期/是否有效
        if(end_time.val()){
            var str=end_time.val().replace(/-/g,'/'); //将2014-06-16 08:00 转化为2014/06/16 08:00
            var date=new Date(str);     //构造一个日期型数据  输入格式必须是2014/06/16 08:00
            var endt = date.getTime();  //获取date的ms数
            var newt = new Date().getTime(); //获取当前时间的ms数
            var qian_time = newt - endt;
            var jutime=(parseInt(endt)>100);
            if(! jutime){
                alert("您输入的策略结束时间有误，请重新输入！");
                return;
            }
            if (qian_time>=0)
            {
                alert("策略结束时间无效，请重新输入！");
                return;
            }
        }else{
            alert("请输入策略结束时间！")
            return;
        }
        //判定开始时间是否有效
        if(start_time.val()){
            var str2=start_time.val().replace(/-/g,'/'); //将2014-06-16 08:00 转化为2014/06/16 08:00
            var date2=new Date(str2);     //构造一个日期型数据  输入格式必须是2014/06/16 08:00
            var startt = date2.getTime();  //获取date的ms数
            var qian_time2 = startt - endt;
            var jutime2=(parseInt(startt)>100);
            if(! jutime2){
                alert("您输入的策略开始时间有误，请重新输入！");
                return;
            }
            if (qian_time2>=0)
            {
                alert("策略时间区间无效，请重新输入！");
                return;
            }
        }else{
            alert("请输入策略开始时间！")
            return;
        }
        //判断描述是否字符过长
        if(desc.val().length>15){
            alert("您输入的策略描述过长，请输入少于15个字！")
            return;
        }
        //判断半径是否合法
        if(isNaN(radius.val())){
            alert("您输入的半径有误，请重新输入！");
            return;
        }
    }else{
        force = 1;
    }
    groups = getUsers();

    //+++ 20150603 策略作用基站若为选择，则置空
    var baseStaId=baseStationID.val();
    if(baseStationID.val()=="请选择基站"){
        baseStaId='';
    }

    //将描述从汉字改为拼音
    //var desc_val=ConvertPinyin(desc.val());

    if(groups.length==0){
        alert("请选择要下发策略的用户");
    }else{
        var users = JSON.stringify(groups);
        var desc_list = getUserDesc();
	    var userdesc = JSON.stringify(desc_list);
        console.log(userdesc);
        var session_id  = $.cookie("org_session_id");
        //event.preventDefault(); //阻止表单提交。
        start_time.removeClass("errMsn"); //如果有错误提示，取消提示
        end_time.removeClass("errMsn");
        location_j.removeClass("errMsn");
        location_w.removeClass("errMsn");
        radius.removeClass("errMsn");
        baseStationID.removeClass("errMsn");
        var bluetooth = "bjy";
        if(wifi.val()=="wfjy"){
            bluetooth = "bfjy";
        }else{
            bluetooth = "bjy"
        }
        var obj = {
            _path: path,
            _methods: 'post',
            param: {
                start: start_time.val(),
                end: end_time.val(),
                desc:desc.val(),   //desc_val,
                lon: location_j.val(),
                lat: location_w.val(),
                radius: radius.val(),
                baseStationID: baseStaId,
                camera: camera.val(),
                //+++改20150803 将wifi和蓝牙的功能合并，但是数据结构不变
                bluetooth: bluetooth,
                wifi: wifi.val(),
                tape: tape.val(),
                gps: gps.val(),
                mobiledata: mobiledata.val(),
                usb_connect: usb_connect.val(),
                usb_debug: usb_debug.val(),
                users:users,
                userdesc:userdesc,
                sid: session_id,
                id:id,
                //+++0629加入强制管控字段
                force:force
            }
        };
        if(val=="策略下发"||val=="短信下发"){
            ajaxReq(obj, function(data) {
                var rt = data.rt;
                var offline_exist = data.offline_exist;
                if (rt === 0) {
                    var info='NewStrategy:'+id;
                    if(offline_exist==1){
                        setTimeout(deal_users(session_id,[],'NewStrategy:'+id),2000);
                    }else{
                        //+++ 20150616 策略下发反馈
                        setTimeout(function(){check_strategy_result(session_id,info);},7000);
                    }
                }else if(rt === 59){
                alert(status3);
            }else if(rt === 61){
                alert("当前策略作用人群中存在用户未激活设备，请重新操作！");
            }else{
                loadingStatus(status2, 0);
                alert(status2);
                check_strategy_result(session_id,info);
            }
        },"策略下发中…");
        }else if(val=="确定修改"){
            ajaxReq(obj, function(data) {
                var rt = data.rt;
                if (rt === 0) {
                    //+++20150916 查看是否存在离线用户并提示
                    var offline_exist = data.offline_exist;
                    var info='ModStrategy:'+id;
                    console.log("修改策略时存在离线用户"+offline_exist);
                    if(offline_exist==1){
                        //存在离线用户
                        setTimeout(deal_users(session_id,[],'ModStrategy:'+id),3000);
                    }else{
                        //不存在离线用户的也可以在多线程中完成推送，这样前台可以将查看的时间缩短一点但是也需要查看在线的是否取完了
                        loadingStatus(status1, 1);
                        //因为后台的不存在离线的用户推送逻辑也是多线程完成的，因此可以在更短的时间内去查看是否取完指令
                        setTimeout(function(){check_modify_stra_result(session_id,info);},3000);
                    }
                }else if(rt === 59){
                    alert(status3);
                }else if(rt === 61){
                    alert("当前策略作用人群中存在用户未激活设备，请重新操作！");
                }else{
                    loadingStatus(status2, 0);
                    alert(status2);
                    check_modify_stra_result(session_id,info);
                }
            },'正在进行操作');
        }
        var n = document.getElementById("strategy_con");
        n.style.display = "none";
        clearAll();
        disableInput(false);
    }
});

//+++ 20150701 for check modify_strategy result
function check_modify_stra_result(sid,info){
    var obj={
        _path: '/a/wp/user/check_modify_stra_result',
        _methods: 'get',
        param: {
            sid: sid,
            info:info
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var left_users=data.left_users;
        if(rt==0){
            if(left_users.length==0){
                loadingStatus("策略已全部被修改接收!",0);
                alert("策略已全部被成功修改!");
                location.replace(location.href);
            }else{
                loadingStatus("存在用户未成功修改策略!",0);
                deal_users(sid,left_users,info);
            }
        }
    },"正在修改管控策略...");
}
//+++ 20150616 for check send_strategy result
function check_strategy_result(sid,info){
    var obj={
        _path: '/a/wp/user/re_send_strategy',
        _methods: 'get',
        param: {
            sid: sid,
            info:info
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var users=data.users;
        if(rt==0){
            if(users.length==0){
                loadingStatus("策略已全部被成功接收!",0);
                alert("策略已全部被成功接收!");
                location.replace(location.href);
            }else{
                loadingStatus("存在用户未成功接收策略!",0);
                deal_users(sid,users,info);
            }
        }
    },"正在执行管控指令...");
}
function deal_users(sid,users,info){
    var type = info.split(':')[0];
    var users_json=JSON.stringify(users);
    //+++ 20150910 通过users的数量判别是修改逻辑之后的还是以前的逻辑
    if(type =="NewStrategy"){
        //短信下发策略
        if(confirm("存在用户未成功收到策略，是否一键短信下发？" +
            "(提示：若点击确定，策略将以短信形式下发至这些设备。若取消，则策略指令不再对这些设备发送！)"))
        {
            var obj={
                _path: '/a/wp/user/send_strategy_by_sms',
                _methods: 'post',
                param: {
                    sid: sid,
                    users: users_json, //测试设备。
                    info: info
                }
            };
            //最后看是否能发送成功
//        setTimeout(function(){check_cmd_result(sid,cmd);},30000);
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("短信下发策略成功!",0);
                    alert("短信下发策略成功!");
                    location.replace(location.href);
                }else{
                    loadingStatus("短信下发策略失败,请重试!",0);
                    alert("短信下发策略失败，请重试！");
                    deal_users(sid,users,info);
                }
            },"正在发送短信...");
        }
        else{
            //清空re cmd dev list
            var obj={
                _path: '/a/wp/user/del_re_stra_users',
                _methods: 'get',
                param: {
                    sid: sid,
                    info:info
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("取消执行下发策略成功!",0);
                    alert("取消执行下发策略成功!");
                    location.replace(location.href);
                }else{
                    loadingStatus("取消执行下发策略失败!",0);
                }
            },"正在取消执行下发策略指令...");
        }
    }else if(type=="ModStrategy"){
        //短信下发策略
        if(confirm("存在用户未成功收到修改策略指令，是否一键短信下发？" +
            "(提示：若点击确定，指令将以短信形式下发至这些设备。若取消，则修改策略指令不再对这些设备发送！)"))
        {
            var obj={
                _path: '/a/wp/user/modify_strategy_by_sms',
                _methods: 'post',
                param: {
                    sid: sid,
                    //users: users_json, //测试设备。
                    info: info
                }
            };
            //最后看是否能发送成功
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    //这两个提示不重复么
                    loadingStatus("短信下发修改策略指令成功!",0);
                    alert("短信下发修改策略指令成功!");
                    location.replace(location.href);
                }else{
                    //这两个提示不重复么
                    loadingStatus("短信下发策略失败,请重试!",0);
                    alert("短信下发策略失败，请重试！");
                    deal_users(sid,users,info);
                }
            },"正在发送短信...");
        }
        else{
            //清空re cmd dev list
            var obj={
                _path: '/a/wp/user/del_modify_stra_users',
                _methods: 'get',
                param: {
                    sid: sid,
                    info:info
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("取消执行修改策略成功!",0);
                    alert("取消执行修改策略成功!");
                    location.replace(location.href);
                }else{
                    loadingStatus("取消执行修改策略失败!",0);
                }
            },"正在取消执行修改策略指令...");
        }
    }else if(type=="DelStrategy"){
        if(confirm("存在用户未成功删除策略，是否一键短信下发删除？" +
            "(提示：若点击确定，删除策略指令将以短信形式下发至这些设备。若取消，则策略指令不再对这些设备发送！)"))
        {
            var obj={
                _path: '/a/wp/user/del_strategy_by_sms',
                _methods: 'post',
                param: {
                    sid: sid,
                    info: info
                }
            };
            //最后看是否能发送成功
//        setTimeout(function(){check_del_result(sid,info);},30000);
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    alert("短信下发删除策略指令成功，发送完短信后会自动删除策略!",0);
                    //+++20150923 等管理员收到短信发送确认之后再弹出提示
//                    alert("短信下发删除策略指令成功!");
//                    location.replace(location.href);
                }else{
                    loadingStatus("短信网关调用不成功，请重试!",0);
                    alert("短信网关调用不成功，请重试!");
                    deal_users(sid,[],info);
                }
            },"正在发送短信...");
        }
        else{
            //清空re cmd dev list
            var obj={
                _path: '/a/wp/user/replace_stra_users',
                _methods: 'get',
                param: {
                    sid: sid,
                    info:info
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("取消执行删除策略指令成功!",0);
                    alert("取消执行删除策略指令成功!");
                    location.replace(location.href);
                }else{
                    //基本不会出现
                    loadingStatus("取消执行删除策略指令失败!",0);
                    alert("取消执行删除策略指令失败，请重试!");
                    deal_users(sid,[],info);
                }
            },"正在取消执行删除策略指令...");
        }
    }

}

$(document).ready(function() {
  $("#stnew").click(function(){
      $("#strategy_con #strategy_N #celveBn").html("策略下发");
      defaultInputs();
  })

  //sms send strategy 20150408
  $("#stsms").click(function(){
      $("#strategy_con #strategy_N #celveBn").html("短信下发");
      defaultInputs();
  })
  /********************/
});

function choiceBaseStation(){
    $("#strategy_con #strategy_N #baseStationID").empty();
    $("#strategy_con #strategy_N #baseStationID").append("<option value='请选择基站'>请选择基站</option>");
    //从配置文件中读取到策略作用基站baseStation(plmn-abc#plme-def...)和基站名baseStationID
    var baseStationID = '';
    var baseStation='';
    var obj = {
        _path:'/a/wp/org/get_all_baseStation',
        _methods: 'get',
        param: {
            sid:$.cookie("org_session_id"),
            baseSec:"中科院"
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt==0) {
            baseStaionInfo=data.baseStationInfo;

            $.map(baseStaionInfo,function(val,key){
                baseStationID=val;
                baseStation=key;
                $("#strategy_con #strategy_N #baseStationID").append("<option value='"+baseStationID+"'>"+baseStation+"</option>");
            });
       }
        else{
            loadingStatus('基站获取失败',0);
        }
    });
}

$("#exitBn").live('click',function(event) {
    var n = document.getElementById("strategy_con");
    document.getElementById('end_time').className="false";
    n.style.display = "none";
    clearAll();
    choiceBaseStation();
    disableInput(false);
    $("#stra_fast_choice").hide();
    $("#stra_fast_choice").attr("name","hide");
    $("#stra_fast_choice").val("请选择预置策略");
});
//策略选择全部的按钮
$("#stxzqb").live("click",function(event){
    if($("#stB tbody tr").children("td").length==0){
        alert("没有可选择的策略信息！！!");//jquery搜索标签并对标签进行操作的过程基本上都是用的函数
    }
    else{
        $("#stB tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
    }
});
//策略空出选择的按钮
$("#stkcxz").live("click",function(event){
    $("#stB tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
});
//修改当前策略
$("#stfix").click(function(){
    var count=0;
    var strategy_id="";
    $("#stB tbody tr .checkbox").each(function(index,element){
        var cb = element.className;
        if(cb=="checkbox checkbox_checked"){
            count++;
            strategy_id = element.parentNode.parentNode.className;
        }
    });
    if(count>1)
    {
        alert("每次只能修改一条策略！！！");
        return false;
    }
    else if (count==0)
    {
        alert("请选择一条需要修改的策略信息！！");
        return false;
    }
    else if(count==1)
    {
        modifystrategy(strategy_id);
    }
});

//function showusers(){
//    var strategy_id = element.parentNode.parentNode.className;
//    var obj={
//        _path:"/a/wp/user/get_strategy_by_id",
//        _methods:"post",
//        param:{
//            sid:$.cookie("org_session_id"),
//            id:strategy_id
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt=data.rt;
//        var strategy = data.strategy;
//        if(rt == 0)
//        {
//            loadingStatus("获取策略作用人员详情成功!",0);
//            var users = strategy.users;
//
//
//        }else{
//            loadingStatus("获取策略作用人员详情失败!",0);
//        }
//    },"正在获取策略作用人员详情...");
//}
//删除选中策略
var popd=$("#strpopd");
$("#strategy_g #stdel").click(function(event){
    var strategy_ids=[];
    if($("#stB tbody tr .checkbox_checked").length==0){
        alert("请选择要删除的策略");
    }else{
        var id=event.target.id;
        var href="#";
            if(id=="stdel"){
                href="#shanchu";
            }
        popd.attr("href",href);
        popd.click();
    }
});
//删除策略
$("#delStr").submit(function(event){
    event.preventDefault();
    $("#shanchu").dialog("close");
    var strategy_ids = [];
    var qx=0;
    var admin_del=[];
    $("#stB tbody tr .checkbox_checked").each(function(index,element){
        var strategy_id = element.parentNode.parentNode.className;
        if($("#stB tbody ."+strategy_id).attr("value")==0){
            qx=qx+1;
            var that=$("#stB tbody ."+strategy_id+" .strategy_id").html();
            admin_del.push(that);
        }
        strategy_ids.push(strategy_id);
    });
    if(qx>0){
        alert("策略"+admin_del+"涉及到其他单位，您无权限删除，请重新选择策略！");
        return;
    }
    strategy_ids=JSON.stringify(strategy_ids);
    delstrategy(strategy_ids,2);
})
//否定删除策略
$("#bDel").click(function(event) {
    $("#shanchu").dialog("close");
});

//+++20150409 sms del stra
$("#strategy_g #smsdel").click(function(event){
    var strategy_ids=[];
    if($("#stB tbody tr .checkbox_checked").length==0){
        alert("请选择要删除的策略");
    }else{
        var id=event.target.id;
        var href="";
        switch(id){
            case "smsdel":
                href="#smsshanchu";
                break;
            default:
                href="#";
        }
        popd.attr("href",href);
        popd.click();
    }
});
//删除策略
$("#smsdelStr").submit(function(event){
    event.preventDefault();
    $("#smsshanchu").dialog("close");

    var strategy_ids = [];
    var qx=0;
    var admin_del=[];
    $("#stB tbody tr .checkbox_checked").each(function(index,element){
        var strategy_id = element.parentNode.parentNode.className;
        if($("#stB tbody ."+strategy_id).attr("value")==0){
            qx=qx+1;
            var that=$("#stB tbody ."+strategy_id+" .strategy_id").html();
            admin_del.push(that);
        }
        strategy_ids.push(strategy_id);
    });
    if(qx>0){
        alert("策略"+admin_del+"涉及到其他单位，您无权限删除，请重新选择策略！");
        return;
    }
    strategy_ids=JSON.stringify(strategy_ids);
    delstrategysms(strategy_ids);
})
//否定删除策略
$("#bDelsms").click(function(event) {
    $("#smsshanchu").dialog("close");
});

function delstrategysms(strategy_ids)
{
    var obj={
        _path:"/a/wp/user/del_strategy_sms",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            ids:strategy_ids
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        if(rt == 0)
        {
            loadingStatus("删除策略配置信息成功!",0);
            alert("删除策略配置信息成功!");
            setTimeout(function(){location.replace(location.href);},2000);
        }else{
            loadingStatus("删除策略配置信息失败!",0);
            alert("调用短信网关失败，请重试!");
        }
    },"正在删除策略配置信息...");
}
/***********************/

function sendDevCmdcon(cmd,flog,res){
    var org_session_id = $.cookie("org_session_id");
    var arr=check_dev_id();
    for(var i=0,len=arr.length;i<len;i++){
        var dev_id=arr[i];
        pf(org_session_id,dev_id,function(){
            var obj={
                _path: '/a/wp/user/send_cmd_and_rs',
                _methods: 'post',
                param:{
                    sid:org_session_id,
                    dev_id:dev_id,
                    cmd:cmd,
                    flog:flog,
                    res:res
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("指令强制执行成功！",0);
                }else{
                    loadingStatus("指令强制执行失败！",0);
                }
            },"正在发送该指令...");
        });
    }
}

function clearAll(){
    $("#strategy_con input").val("");
    //+++20150730 不要清除用户的选中状态
    //$("#strategy_con .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    document.getElementById("camera").options[0].selected=true;
    document.getElementById('wifi').options[0].selected=true;
    document.getElementById('tape').options[0].selected=true;
    document.getElementById('gps').options[0].selected=true;
    document.getElementById('mobiledata').options[0].selected=true;
    document.getElementById('usb_connect').options[0].selected=true;
    document.getElementById('usb_debug').options[0].selected=true;
    //+++ 20150929 将强制管控选项置空
    $("#forceControl").attr("class","checkbox checkbox_uncheck");
    $("#stra_fast_choice").hide();
    $("#stra_fast_choice").attr("name","hide");
    $("#stra_fast_choice").val("请选择预置策略");
    $("#delPreStra").hide();
    $("#addPreStra").hide();
}

function getUsers(){
    //获取树中所有被选中的用户，以树的形式存入数据库
    var users = new Array();
    var spans = $("#yic .checkbox_checked");
    //获取所有被选中的checkbox
    //取得用户的部门属性进行排序，然后就可以打包成最后的形态
    //获取未排序之前的所有用户
    if(spans.length==0){
        users = [];
        return users;
    }else{
        users.push("选择了");
    }
//    for(var i=0;i<spans.length;i++){
//        if(spans[i].id.substring(0,2)=='ou'){continue;}
//        else{
//            var sdn = spans[i].id;
//            var uid = spans[i].title;
//            var dn = spans[i].id.substring(3);
//            //获取所有选中用户的部门属性
//            var departmentId = '';
//            departmentId = sdn.substring(sdn.indexOf("ou"));
//            //获取所有用户姓名所在的a
//            var a = document.getElementsByName(sdn)[0];
//            var username = a.innerHTML;
//            var user = {'username':username,'departmentId':departmentId,'uid':uid};
//            users.push(user);
//        }
//    }
//    //对用户数组按部门属性排序
//    var i = users.length-1;
//    while(i){
//        for(var j=0;j<i;j++){
//            if(users[j]['departmentId']>users[j+1]['departmentId']){
//                var temp = users[j];
//                users[j] = users[j+1];
//                users[j+1] = temp;
//            }
//        }
//        i--;
//    }
//    //最终user的封装
//    var groups = new Array();
//    for(var i=0;i<users.length;){
//        var group = {'name':'','users':[]};
//        group['name'] = users[i].departmentId;
//        for(var j=i;j<users.length;j++){
//            var temp = j;
//            if(users[j]['departmentId']==users[i]['departmentId']){
//                group.users.push({'username':users[j]['username'],'uid':users[j]['uid']});
//            }else{
//                i=j;
//                groups.push(group);
//                break;
//            }
//            if(j==users.length-1){
//                i=j+1;
//                groups.push(group);
//            }
//
//        }
//    }
    return users;
}


//+++20150730 获取用户策略描述
function getUserDesc(){
    //获取所有被选中的checkbox
    var rootdiv = $("#strategy_con #yic div[id]");
    var userdesc = [];
    var descTree = getOuSelectedStatus(rootdiv.attr("id"));
    console.log(descTree);
    if(descTree.desc=="全部"){
        userdesc.push({"name":descTree.name,"desc":descTree.desc});
        return userdesc;
    }else{
        var rootname = descTree.name;
        if(descTree.ous){
            var ous = descTree.ous;
            for(var i=0;i<ous.length;i++){
                var item = ous[i];
                console.log(item['name']);
                if(item['desc']!="无"){
                    userdesc.push({"name":rootname+"/"+item['name'],"desc":item['desc']});
                }
            }
            //+++20150929 加入没有子群组的策略下发的情况
        }else{
            userdesc.push({"name":descTree.name,"desc":descTree.desc});
        }
        return userdesc;
    }
}

function getOuSelectedStatus(div_id){
    var div = $("div[id='"+div_id+"']");
    var content = div.html();
    var span = $("span[id='ou:"+div_id+"']");
    if(content==""&&span.attr("class")=="checkbox checkbox_checked"){
        return {"name":div_id.split(',')[0].split('=')[1],"desc":"全部","result":true};
    }else if(content==""&&span.attr("class")=="checkbox checkbox_uncheck"){
        return {"name":div_id.split(',')[0].split('=')[1],"desc":"无","result":false};
    }else {
        var li_length = div.children("li").length;
        if (li_length > 0) {
            var desc = "全部";
            var usersall = true;
            for (var i = 0; i < li_length; i++) {
                var sonli = div.children("li")[i];
                var sonspan = sonli.childNodes[0];
                if (sonspan.className == "checkbox checkbox_uncheck") {
                    desc = "部分";
                    usersall = false;
                }
            }

            return {"name": div_id.split(',')[0].split('=')[1], "desc": desc, "result": usersall};
        } else {
            var div_length = div.children("div").length;
            var all = true;
            var sonous = new Array();
            for (var j = 0; j < div_length; j++) {
                var sondiv = div.children("div")[j];
                if (sondiv.id != "") {
                    var sonou = getOuSelectedStatus(sondiv.id);
                    sonous.push(sonou);
                    all = all & sonou.result;
                }
            }
            if (all) {
                return {"name": div_id.split(',')[0].split('=')[1], "desc": "全部", "result": all,"ous":sonous};
            } else {
                return {"name": div_id.split(',')[0].split('=')[1], "desc": "部分", "result": all,"ous":sonous};
            }
        }
    }
}


function getStrategyID(){
    var myDate = new Date();
    var mytime=myDate.getTime();
    return ''+mytime;
}

function delstrategy(strategy_ids)
{
    //区分每行最后的删除和多个删除，由于strategy_ids的不同
    var type=arguments[1]?arguments[1]:1;
    if(type==1){   //string to array_string
        console.log($("#stB tbody ."+strategy_ids).attr("value"));
        if($("#stB tbody ."+strategy_ids).attr("value")==0){
            alert("您无权限删除该策略，请联系相关管理员删除！！");
            return;
        }
        var str=[];
        str.push(strategy_ids);
        if (str!=[]){
            strategy_ids=JSON.stringify(str);
        }
    }
    var obj={
        _path:"/a/wp/user/del_strategy",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            ids:strategy_ids
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var info='DelStrategy:'+strategy_ids;
        if(rt == 0)
        {
            var offline_exist = data.offline_exist;
            if(offline_exist==1){
                deal_users($.cookie("org_session_id"),[],info);
            }else{
                loadingStatus("删除策略配置信息指令下发中...",1);
                setTimeout(function(){check_del_result($.cookie("org_session_id"),info);},2000);
            }
        }else if(rt==59){
            alert("当前策略作用人群中存在用户不在线，为确保策略删除，请使用短信删除策略！");
        }else{
            if(confirm("由于网络原因，指令下发失败，是否继续尝试短信发送？")){
                check_del_result($.cookie("org_session_id"),info);
            }else{
                loadingStatus("删除策略配置信息指令已取消！",0);
                alert("删除策略配置信息指令已取消!");
            }
        }
    },"正在删除策略配置信息...");
}
//+++ 20150618 for check del_strategy result
function check_del_result(sid,info){
    var obj={
        _path: '/a/wp/user/re_del_strategy',
        _methods: 'get',
        param: {
            sid: sid,
            info:info
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var re=data.re;
        if(rt==0){
            if(re==0){
                loadingStatus("策略已全部被成功删除!",0);
                alert("策略已全部被成功删除!");
                location.replace(location.href);
            }else{
                loadingStatus("存在用户未删除策略!",0);
                //+++ 20150916 三个处理函数合并
                deal_users(sid,[],info);
            }
        }
    },"正在执行管控指令...");
}


function modifystrategy(strategy_id){
    //+++20151024首先查看该用户是不是有权限更改该条策略
    var isadmin = $("tr[class='"+strategy_id+"']").attr("value");
    if(isadmin==0){
        alert("您无权限修改此条策略，请联系相关管理员修改！！");
    }else{
        clearAll();
        choiceBaseStation();
        $("#strategy_con #strategy_N #celveBn").html("确定修改");
        var users=[];
        var obj={
            _path:"/a/wp/user/get_strategy_by_id",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                strategy_id:strategy_id
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            var strategy=data.strategy;
            if(rt == 0)
            {
                var userdesc = strategy['userdesc'];
                loadingStatus("获取策略配置信息成功!",0);
                //判断当前用户是否有权限修改或删除该策略
                var udesc=[];
                for(i=0;i<userdesc.length;i++){
                    var name=userdesc[i].name;
                    udesc.push(name.split("/")[0]);
                }
                var ou_number=unique(udesc).length;

                if(ou_number>1 && $.cookie("userid")!='admin')
                {
                    document.getElementById('end_time').className="true";
                    alert("该策略涉及到其他单位，您无权限修改该策略！");
                    $("#strategy_con").css("display","none");
                }
                else
                {
                    document.getElementById('end_time').className="false";
                }
                users = strategy['users'];
                loadusers(users);
                if(strategy['force']==1){
                    forceConfig.className = "checkbox checkbox_checked";
                    //将值设置为空和禁用
                    start_time.val('');
                    end_time.val('');
                    location_j.val('');
                    location_w.val('');
                    baseStationID.val('');
                    radius.val('');
                    //禁用所有设备
                    controlDevices("jy");
                    disableInput(true);
                    alert("本条为严格管控策略，禁止修改！如有必要，请删除后重新下发。");
                    $("#strategy_con").css("display","none");
                    disableInput(false);
                }else{
                    forceConfig.className = "checkbox checkbox_uncheck";
                    document.getElementById('start_time').value=strategy['start'];
                    document.getElementById('start_time').className=strategy_id;
                    document.getElementById('end_time').value=strategy['end'];
                    if(strategy['lon']!="")
                        document.getElementById('location_j').value=strategy['lon'];
                    if(strategy['lat']!="")
                        document.getElementById('location_w').value=strategy['lat'];
                    if(strategy['radius']!="")
                        document.getElementById('radius').value=strategy['radius'];

                    document.getElementById('camera').value=strategy['camera'];
                    //document.getElementById('bluetooth').value=strategy['bluetooth'];
                    document.getElementById('wifi').value=strategy['wifi'];
                    document.getElementById('tape').value=strategy['tape'];
                    document.getElementById('gps').value=strategy['gps'];
                    document.getElementById('mobiledata').value=strategy['mobiledata'];
                    document.getElementById('usb_connect').value=strategy['usb_connect'];
                    document.getElementById('usb_debug').value=strategy['usb_debug'];
                }
                if(strategy['desc']!="")
                    document.getElementById('desc').value=strategy['desc'];

            }else{
                loadingStatus("获取策略配置信息失败!",0);
            }
        },"正在获取策略配置信息...");
        document.getElementById("strategy_con").style.display="block";
    }
}
//+++ 20150707
function unique(arr) {
    var result = [], hash = {};
    for (var i = 0, elem; (elem = arr[i]) != null; i++) {
        if (!hash[elem]) {
            result.push(elem);
            hash[elem] = true;
        }
    }
    return result;
}
/*********/
function loadusers(users){
    //现在user的存储格式是udn+数组下所有第一级用户的信息
    //users{[{"name":udn,"users":["username":cn,"uid":uid]}]}
    //document.getElementById(divs[1].id);
    //思路是这样的，将获取到的用户信息进行遍历，进行组织dn的匹配--进行组织下一级用户dn的拼接匹配
    //获取管理员的管理权限
    var sid=$.cookie("org_session_id");
    var obj={
        _path:"/a/wp/org/org_info",
        _methods:"get",
        param:{
            sid:sid
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        if(rt==0){
            var adminqx = data.org_right;
            console.log(adminqx);
//            alert(adminqx);
            var rg = new RegExp('.*'+adminqx+'.*');
            //如果策略是作用于多个单位的，则只加载该管理员所在单位的作用人群
            for(var i=0;i<users.length;i++){
                var ou = users[i];
                var oudn = ou['name'];
//                alert(oudn);
                if(adminqx != "所有用户" && (!rg.test(oudn)))
                {
//                    alert(rg.test(oudn));
                    continue;
                }
                var div = document.getElementById(oudn);
                div.parentNode.style.display="block";
                div.style.display="block";
                var sonusers = ou['users'];
                for(var j=0;j<sonusers.length;j++){
                    var cn = sonusers[j].username;
                    var span = $("span[id='us:cn="+cn+","+oudn+"']");
                    //var span = document.getElementById(sdn);
                    span.attr("class","checkbox checkbox_checked");
                }
            }
        }else{
            loadingStatus("未能获取到管理员权限！",0);
        }
    },"");
}

function showusers(element){
    var strategy_id = element.parentNode.parentNode.className;
    var obj={
        _path:"/a/wp/user/get_strategy_by_id",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            strategy_id:strategy_id
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var strategy = data.strategy;
        if(rt == 0)
        {
            loadingStatus("获取策略作用人员详情成功!",0);
            var users = strategy.users;
            var html = "";
            html+="作用人群如下：\n";
            for(var i=0;i<users.length;i++){
                var oudn = users[i]['name'];
                var department = '';
                var fenjie = oudn.split(',');
                for(var k=fenjie.length-1;k>=0;k--){
                    if(fenjie[k].substring(0,2)=='ou'){
                        department+=fenjie[k].substring(3)+'/';
                    }
                }
                department = department.substring(0,department.length-1);
                html+=department+':';
                var sonusers = users[i]['users'];
                //+++20150801 由于作用用户长度过长导致前台无法完全显示，增加显示用户限制100人
                var showLength = sonusers.length;
                if(sonusers.length>10){
                    showLength = 10;
                }
                for(var j=0;j<showLength;j++){
                    html+=sonusers[j]['username']+',';
                }
                if(sonusers.length>100){
                    html+='……';
                }
                html+='\n';
            }
            alert(html);

        }else{
            loadingStatus("获取策略作用人员详情失败!",0);
        }
    },"正在获取策略作用人员详情...");
}
//时间控件

//------------------ 样式定义 ---------------------------//

//功能按钮同样样式
var s_tiannet_turn_base = "height:30px; line-height:20px; font-size:9px; color:white; border:0px solid #CCCCCC; cursor:hand; background-color:#2650A6;";

//翻年、月等的按钮

var s_tiannet_turn = "width:28px;" + s_tiannet_turn_base;

//关闭、清空等按钮样式

var s_tiannet_turn2 = "width:22px;" + s_tiannet_turn_base;

//年选择下拉框

var s_tiannet_select = "width:64px;display:none;";

//月、时、分选择下拉框

var s_tiannet_select2 = "width:46px;display:none;";

//日期选择控件体的样式

var s_tiannet_body = "background-color:#2650A6;display:none;z-index:1;position:absolute;border-left:1px solid #000;border-top:1px solid #000;border-right:1px solid #000;border-bottom:1px solid #000;";

//显示日的td的样式

var s_tiannet_day = "width:21px;height:20px;background-color:#D8F0FC;font-size:10pt;";

//字体样式

var s_tiannet_font = "color:#FFCC00;font-size:9pt;cursor:hand;";

//链接的样式

var s_tiannet_link = "text-decoration:none;font-size:9pt;color:#2650A6;";

//横线

var s_tiannet_line = "border-bottom:1px solid #6699CC";

//------------------ 变量定义 ---------------------------//

var tiannetYearSt = 2014;//可选择的开始年份

var tiannetYearEnd = 2050;//可选择的结束年份

var tiannetDateNow = new Date();

var tiannetYear = tiannetDateNow.getFullYear(); //定义年的变量的初始值

var tiannetMonth = tiannetDateNow.getMonth()+1; //定义月的变量的初始值

var tiannetDay = tiannetDateNow.getDate();

var tiannetHour = 8;//tiannetDateNow.getHours();

var tiannetMinute = 0;//tiannetDateNow.getMinutes();

var tiannetArrDay=new Array(42); //定义写日期的数组

var tiannetDateSplit = "-"; //日期的分隔符号

var tiannetDateTimeSplit = " "; //日期与时间之间的分隔符

var tiannetTimeSplit = ":"; //时间的分隔符号

var tiannetOutObject; //接收日期时间的对象

var arrTiannetHide = new Array();//被强制隐藏的标签

var m_bolShowHour = false;//是否显示小时

var m_bolShowMinute = false;//是否显示分钟

var m_aMonHead = new Array(12); //定义阳历中每个月的最大天数

m_aMonHead[0] = 31; m_aMonHead[1] = 28; m_aMonHead[2] = 31; m_aMonHead[3] = 30; m_aMonHead[4] = 31; m_aMonHead[5] = 30; m_aMonHead[6] = 31; m_aMonHead[7] = 31; m_aMonHead[8] = 30; m_aMonHead[9] = 31; m_aMonHead[10] = 30; m_aMonHead[11] = 31;

// ---------------------- 用户可调用的函数 -----------------------------//

//用户主调函数－只选择日期

function setDay(obj){

    tiannetOutObject = obj;

//如果标签中有值，则将日期初始化为当前值

    var strValue = tiannetTrim(tiannetOutObject.value);

    if( strValue != "" ){

        tiannetInitDate(strValue);

    }

    tiannetPopCalendar();

}

//用户主调函数－选择日期和小时

function setDayH(obj){

    tiannetOutObject = obj;

    m_bolShowHour = true;

//如果标签中有值，则将日期和小时初始化为当前值

    var strValue = tiannetTrim(tiannetOutObject.value);

    if( strValue != "" ){

        tiannetInitDate(strValue.substring(0,10));

        var hour = strValue.substring(11,13);

        if( hour < 10 ) tiannetHour = hour.substring(1,2);

    }

    tiannetPopCalendar();

}

//用户主调函数－选择日期和小时及分钟

function setDayHM(obj){

    tiannetOutObject = obj;

    m_bolShowHour = true;

    m_bolShowMinute = true;

//如果标签中有值，则将日期和小时及分钟初始化为当前值

    var strValue = tiannetTrim(tiannetOutObject.value);

    if( strValue != "" ){

        tiannetInitDate(strValue.substring(0,10));

        var time = strValue.substring(11,16);

        var arr = time.split(tiannetTimeSplit);

        tiannetHour = arr[0];

        tiannetMinute = arr[1];

        if( tiannetHour < 10 ) tiannetHour = tiannetHour.substring(1,2);

        if( tiannetMinute < 10 ) tiannetMinute = tiannetMinute.substring(1,2);

    }

    tiannetPopCalendar();

}

function setDayHM2(obj){

    tiannetOutObject = obj;

    m_bolShowHour = true;

    m_bolShowMinute = true;

//如果标签中有值，则将日期和小时及分钟初始化为当前值

    var strValue = tiannetTrim(tiannetOutObject.value);

    if( strValue != "" ){

        tiannetInitDate(strValue.substring(0,10));

        var time = strValue.substring(11,16);

        var arr = time.split(tiannetTimeSplit);

        tiannetHour = arr[0];

        tiannetMinute = arr[1];

        if( tiannetHour < 10 ) tiannetHour = tiannetHour.substring(1,2);

        if( tiannetMinute < 10 ) tiannetMinute = tiannetMinute.substring(1,2);

    }

    tiannetPopCalendar();

}

//设置开始日期和结束日期

function setYearPeriod(intDateBeg,intDateEnd){

    tiannetYearSt = intDateBeg;

    tiannetYearEnd = intDateEnd;

}

//设置日期分隔符。默认为"-"

function setDateSplit(strDateSplit){

    tiannetDateSplit = strDateSplit;

}

//设置日期与时间之间的分隔符。默认为" "

function setDateTimeSplit(strDateTimeSplit){

    tiannetDateTimeSplit = strDateTimeSplit;

}

//设置时间分隔符。默认为":"

function setTimeSplit(strTimeSplit){

    tiannetTimeSplit = strTimeSplit;

}

//设置分隔符

function setSplit(strDateSplit,strDateTimeSplit,strTimeSplit){

    tiannetDateSplit(strDateSplit);

    tiannetDateTimeSplit(strDateTimeSplit);

    tiannetTimeSplit(strTimeSplit);

}

//设置默认的日期。格式为：YYYY-MM-DD

function setDefaultDate(strDate){

    tiannetYear = strDate.substring(0,4);

    tiannetMonth = strDate.substring(5,7);

    tiannetDay = strDate.substring(8,10);

}

//设置默认的时间。格式为：HH24:MI

function setDefaultTime(strTime){

    tiannetHour = strTime.substring(0,2);

    tiannetMinute = strTime.substring(3,5);

}

//------------------ begin 页面显示部分 ---------------------------//

var weekName = new Array("日","一","二","三","四","五","六");

document.write('<div id="divTiannetDate" style="'+s_tiannet_body+'" >');

document.write('<div align="center" id="divTiannetDateText" Author="tiannet" style="padding-top:2px;">');

document.write('<span id="tiannetYearHead" Author="tiannet" style="'+s_tiannet_font+'" '+ 'onclick="spanYearCEvent();"> 年</span>');

document.write('<select id="selTianYear" style="'+s_tiannet_select+'" Author="tiannet" '+ ' onChange="tiannetYear=this.value;tiannetSetDay(tiannetYear,tiannetMonth);document.all.tiannetYearHead.style.display=\'\';'+ 'this.style.display=\'none\';">');

for(var i=tiannetYearSt;i <= tiannetYearEnd;i ++){

    document.writeln('<option value="' + i + '">' + i + '年</option>');

}

document.write('</select>');

document.write('<span id="tiannetMonthHead" Author="tiannet" style="'+s_tiannet_font+'" '+ 'onclick="spanMonthCEvent();"> 月</span>');

document.write('<select id="selTianMonth" style="'+s_tiannet_select2+'" Author="tiannet" '+ 'onChange="tiannetMonth=this.value;tiannetSetDay(tiannetYear,tiannetMonth);document.all.tiannetMonthHead.style.display=\'\';'+ 'this.style.display=\'none\';">');

for(var i=1;i <= 12;i ++){

    document.writeln('<option value="' + i + '">' + i + '月</option>');

}

document.write('</select>');

document.write('<span id="tiannetHourHead" Author="tiannet" style="'+s_tiannet_font+'display:none;" '+ 'onclick="spanHourCEvent();"> 时</span>');

document.write('<select id="selTianHour" style="'+s_tiannet_select2+'display:none;" Author="tiannet" '+ 'onChange="tiannetHour=this.value;tiannetWriteHead();document.all.tiannetHourHead.style.display=\'\';' + 'this.style.display=\'none\';">');

for(var i=0;i <= 23;i ++){

    document.writeln('<option value="' + i + '">' + i + '时</option>');

}

document.write('</select>');

document.write('<span id="tiannetMinuteHead" Author="tiannet" style="'+s_tiannet_font+'display:none;" '+ 'onclick="spanMinuteCEvent();"> 分</span>');

document.write('<select id="selTianMinute" style="'+s_tiannet_select2+'display:none;" Author="tiannet" '+ ' onChange="tiannetMinute=this.value;tiannetWriteHead();document.all.tiannetMinuteHead.style.display=\'\';'+ 'this.style.display=\'none\';">');

for(var i=0;i <= 59;i ++){

    document.writeln('<option value="' + i + '">' + i + '分</option>');

}

document.write('</select>');

document.write('</div>');

//输出一条横线

document.write('<div style="'+s_tiannet_line+'"></div>');

document.write('<div align="center" id="divTiannetTurn" style="border:0;" Author="tiannet">');

document.write('<input type="button" style="'+s_tiannet_turn+'" value="年↑" title="上一年" onClick="tiannetPrevYear();">');

document.write('<input type="button" style="'+s_tiannet_turn+'" value="年↓" title="下一年" onClick="tiannetNextYear();"> ');

document.write('<input type="button" style="'+s_tiannet_turn+'" value="月↑" title="上一月" onClick="tiannetPrevMonth();">');

document.write('<input type="button" style="'+s_tiannet_turn+'" value="月↓" title="下一月" onClick="tiannetNextMonth();">');

document.write('</div>');

//输出一条横线

document.write('<div style="'+s_tiannet_line+'"></div>');

document.write('<table border=0 cellspacing=0 cellpadding=0 bgcolor=white onselectstart="return false">');

document.write(' <tr style="background-color:#2650A6;font-size:10pt;color:white;height:22px;" Author="tiannet">');

for(var i =0;i < weekName.length;i ++){

//输出星期

    document.write('<td width="21px" align="center" Author="tiannet">' + weekName[i] + '</td>');

}

document.write(' </tr>');

document.write('</table>');

//输出天的选择

document.write('<table border=0 cellspacing=1 cellpadding=0 bgcolor=white onselectstart="return false">');

var n = 0;

for (var i=0;i<5;i++) {

    document.write (' <tr align=center id="trTiannetDay' + i + '" >');

    for (var j=0;j<7;j++){

        document.write('<td align="center" id="tdTiannetDay' + n + '" '+ 'onClick="tiannetDay=this.innerText;tiannetSetValue(true);" '+' style="' + s_tiannet_day + '"> </td>');

        n ++;

    }

    document.write (' </tr>');

}

document.write (' <tr align=center id="trTiannetDay5" >');

document.write('<td align="center" id="tdTiannetDay35" onClick="tiannetDay=this.innerText;tiannetSetValue(true);" ' +' style="' + s_tiannet_day + '"> </td>');

document.write('<td align="center" id="tdTiannetDay36" onClick="tiannetDay=this.innerText;tiannetSetValue(true);" ' +' style="' + s_tiannet_day + '"> </td>');

document.write('<td align="right" colspan="5"><a href="javascript:tiannetClear();" style="' + s_tiannet_link + '">清空</a>'+ ' <a href="javascript:tiannetHideControl();" style="' + s_tiannet_link + '">关闭</a>' + ' <a href="javascript:tiannetSetValue(true);" style="' + s_tiannet_link + '">确定</a> ' + '</td>');

document.write (' </tr>');

document.write('</table>');

document.write('</div>');

//------------------ 显示日期时间的span标签响应事件 ---------------------------//

//单击年份span标签响应

function spanYearCEvent(){

    hideElementsById(new Array("selTianYear","tiannetMonthHead"),false);

    if(m_bolShowHour) hideElementsById(new Array("tiannetHourHead"),false);

    if(m_bolShowMinute) hideElementsById(new Array("tiannetMinuteHead"),false);

    hideElementsById(new Array("tiannetYearHead","selTianMonth","selTianHour","selTianMinute"),true);

}

//单击月份span标签响应

function spanMonthCEvent(){

    hideElementsById(new Array("selTianMonth","tiannetYearHead"),false);

    if(m_bolShowHour) hideElementsById(new Array("tiannetHourHead"),false);

    if(m_bolShowMinute) hideElementsById(new Array("tiannetMinuteHead"),false);

    hideElementsById(new Array("tiannetMonthHead","selTianYear","selTianHour","selTianMinute"),true);

}

//单击小时span标签响应

function spanHourCEvent(){

    hideElementsById(new Array("tiannetYearHead","tiannetMonthHead"),false);

    if(m_bolShowHour) hideElementsById(new Array("selTianHour"),false);

    if(m_bolShowMinute) hideElementsById(new Array("tiannetMinuteHead"),false);

    hideElementsById(new Array("tiannetHourHead","selTianYear","selTianMonth","selTianMinute"),true);

}

//单击分钟span标签响应

function spanMinuteCEvent(){

    hideElementsById(new Array("tiannetYearHead","tiannetMonthHead"),false);

    if(m_bolShowHour) hideElementsById(new Array("tiannetHourHead"),false);

    if(m_bolShowMinute) hideElementsById(new Array("selTianMinute"),false);

    hideElementsById(new Array("tiannetMinuteHead","selTianYear","selTianMonth","selTianHour"),true);

}

//根据标签id隐藏或显示标签

function hideElementsById(arrId,bolHide){

    var strDisplay = "";

    if(bolHide) strDisplay = "none";

    for(var i = 0;i < arrId.length;i ++){

        var obj = document.getElementById(arrId[i]);

        obj.style.display = strDisplay;

    }

}

//------------------ end 显示日期时间的span标签响应事件 ---------------------------//

//判断某年是否为闰年

function isPinYear(year){

    var bolRet = false;

    if (0==year%4&&((year%100!=0)||(year%400==0))) {

        bolRet = true;

    }

    return bolRet;

}

//得到一个月的天数，闰年为29天

function getMonthCount(year,month){

    var c=m_aMonHead[month-1];

    if((month==2)&&isPinYear(year)) c++;

    return c;

}

//重新设置当前的日。主要是防止在翻年、翻月时，当前日大于当月的最大日

function setRealDayCount() {

    if( tiannetDay > getMonthCount(tiannetYear,tiannetMonth) ) {

//如果当前的日大于当月的最大日，则取当月最大日

        tiannetDay = getMonthCount(tiannetYear,tiannetMonth);

    }

}

//在个位数前加零

function addZero(value){

    if(value < 10 ){

        value = "0" + value;

    }

    return value;

}

//取出空格

function tiannetTrim(str) {

    return str.replace(/(^\s*)|(\s*$)/g,"");

}

//为select创建一个option

function createOption(objSelect,value,text){

    var option = document.createElement("OPTION");

    option.value = value;

    option.text = text;

    objSelect.options.add(option);

}

//往前翻 Year

function tiannetPrevYear() {

    if(tiannetYear > 999 && tiannetYear <10000){tiannetYear--;}

    else{alert("年份超出范围（1000-9999）！");}

    tiannetSetDay(tiannetYear,tiannetMonth);

//如果年份小于允许的最小年份，则创建对应的option

    if( tiannetYear < tiannetYearSt ) {

        tiannetYearSt = tiannetYear;

        createOption(document.all.selTianYear,tiannetYear,tiannetYear + "年");

    }

    checkSelect(document.all.selTianYear,tiannetYear);

    tiannetWriteHead();

}

//往后翻 Year

function tiannetNextYear() {

    if(tiannetYear > 999 && tiannetYear <10000){tiannetYear++;}

    else{alert("年份超出范围（1000-9999）！");return;}

    tiannetSetDay(tiannetYear,tiannetMonth);

//如果年份超过允许的最大年份，则创建对应的option

    if( tiannetYear > tiannetYearEnd ) {

        tiannetYearEnd = tiannetYear;

        createOption(document.all.selTianYear,tiannetYear,tiannetYear + "年");

    }

    checkSelect(document.all.selTianYear,tiannetYear);

    tiannetWriteHead();

}

//选择今天

function tiannetToday() {

    tiannetYear = tiannetDateNow.getFullYear();

    tiannetMonth = tiannetDateNow.getMonth()+1;

    tiannetDay = tiannetDateNow.getDate();

    tiannetSetValue(true);

//tiannetSetDay(tiannetYear,tiannetMonth);

//selectObject();

}

//往前翻月份

function tiannetPrevMonth() {

    if(tiannetMonth>1){tiannetMonth--}else{tiannetYear--;tiannetMonth=12;}

    tiannetSetDay(tiannetYear,tiannetMonth);

    checkSelect(document.all.selTianMonth,tiannetMonth);

    tiannetWriteHead();

}

//往后翻月份

function tiannetNextMonth() {

    if(tiannetMonth==12){tiannetYear++;tiannetMonth=1}else{tiannetMonth++}

    tiannetSetDay(tiannetYear,tiannetMonth);

    checkSelect(document.all.selTianMonth,tiannetMonth);

    tiannetWriteHead();

}

//向span标签中写入年、月、时、分等数据

function tiannetWriteHead(){

    document.all.tiannetYearHead.innerText = tiannetYear + "年";

    document.all.tiannetMonthHead.innerText = tiannetMonth + "月";

    if( m_bolShowHour ) document.all.tiannetHourHead.innerText = " "+tiannetHour + "时";

    if( m_bolShowMinute ) document.all.tiannetMinuteHead.innerText = tiannetMinute + "分";

    tiannetSetValue(false);//给文本框赋值，但不隐藏本控件

}

//设置显示天

function tiannetSetDay(yy,mm) {

    setRealDayCount();//设置当月真实的日

    tiannetWriteHead();

    var strDateFont1 = "", strDateFont2 = "" //处理日期显示的风格

    for (var i = 0; i < 37; i++){tiannetArrDay[i]=""}; //将显示框的内容全部清空

    var day1 = 1;

    var firstday = new Date(yy,mm-1,1).getDay(); //某月第一天的星期几

    for (var i = firstday; day1 < getMonthCount(yy,mm)+1; i++){

        tiannetArrDay[i]=day1;day1++;

    }

    for (var i = 0; i < 37; i++){

        var da = eval("document.all.tdTiannetDay"+i) //书写新的一个月的日期星期排列

        if (tiannetArrDay[i]!="") {

//判断是否为周末，如果是周末，则改为红色字体

            if(i % 7 == 0 || (i+1) % 7 == 0){

                strDateFont1 = "<font color=#f0000>"

                strDateFont2 = "</font>"

            } else {

                strDateFont1 = "";

                strDateFont2 = ""

            }

            da.innerHTML = strDateFont1 + tiannetArrDay[i] + strDateFont2;

//如果是当前选择的天，则改变颜色

            if(tiannetArrDay[i] == tiannetDay ) {

                da.style.backgroundColor = "#CCCCCC";

            } else {

                da.style.backgroundColor = "#EFEFEF";

            }

            da.style.cursor="hand"

        } else {

            da.innerHTML="";da.style.backgroundColor="";da.style.cursor="default"

        }

    }//end for

    tiannetSetValue(false);//给文本框赋值，但不隐藏本控件

}//end function tiannetSetDay

//根据option的值选中option

function checkSelect(objSelect,selectValue) {

    var count = parseInt(objSelect.length);

    if( selectValue < 10 && selectValue.toString().length == 2) {

        selectValue = selectValue.substring(1,2);

    }

    for(var i = 0;i < count;i ++){

        if(objSelect.options[i].value == selectValue){

            objSelect.selectedIndex = i;

            break;

        }

    }

}

//选中年、月、时、分等下拉框

function selectObject(){

//如果年份小于允许的最小年份，则创建对应的option

    if( tiannetYear < tiannetYearSt ) {

        for( var i = tiannetYear;i < tiannetYearSt;i ++ ){

            createOption(document.all.selTianYear,i,i + "年");

        }

        tiannetYearSt = tiannetYear;

    }

//如果年份超过允许的最大年份，则创建对应的option

    if( tiannetYear > tiannetYearEnd ) {

        for( var i = tiannetYearEnd+1;i <= tiannetYear;i ++ ){

            createOption(document.all.selTianYear,i,i + "年");

        }

        tiannetYearEnd = tiannetYear;

    }

    checkSelect(document.all.selTianYear,tiannetYear);

    checkSelect(document.all.selTianMonth,tiannetMonth);

    if( m_bolShowHour ) checkSelect(document.all.selTianHour,tiannetHour);

    if( m_bolShowMinute ) checkSelect(document.all.selTianMinute,tiannetMinute);

}

//给接受日期时间的控件赋值

//参数bolHideControl - 是否隐藏控件

function tiannetSetValue(bolHideControl){

    var value = "";

    if( !tiannetDay || tiannetDay == "" ){

        tiannetOutObject.value = value;

        return;

    }

    var mm = tiannetMonth;

    var day = tiannetDay;

    if( mm < 10 && mm.toString().length == 1) mm = "0" + mm;

    if( day < 10 && day.toString().length == 1) day = "0" + day;

    value = tiannetYear + tiannetDateSplit + mm + tiannetDateSplit + day;

    if( m_bolShowHour ){

        var hour = tiannetHour;

        if( hour < 10 && hour.toString().length == 1 ) hour = "0" + hour;

        value += tiannetDateTimeSplit + hour;

    }

    if( m_bolShowMinute ){

        var minute = tiannetMinute;

        if( minute < 10 && minute.toString().length == 1 ) minute = "0" + minute;

        value += tiannetTimeSplit + minute;

    }

    tiannetOutObject.value = value;

    if( bolHideControl ) {

        tiannetHideControl();

    }

}
//是否显示时间

function showTime(){

    if( !m_bolShowHour && m_bolShowMinute){

        alert("如果要选择分钟，则必须可以选择小时！");

        return;

    }

    hideElementsById(new Array("tiannetHourHead","selTianHour","tiannetMinuteHead","selTianMinute"),true);

    if( m_bolShowHour ){

//显示小时

        hideElementsById(new Array("tiannetHourHead"),false);

    }

    if( m_bolShowMinute ){

//显示分钟

        hideElementsById(new Array("tiannetMinuteHead"),false);

    }

}

//弹出显示日历选择控件，以让用户选择

function tiannetPopCalendar(){

//隐藏下拉框，显示相对应的head

    hideElementsById(new Array("selTianYear","selTianMonth","selTianHour","selTianMinute"),true);

    hideElementsById(new Array("tiannetYearHead","tiannetMonthHead","tiannetHourHead","tiannetMinuteHead"),false);

    tiannetSetDay(tiannetYear,tiannetMonth);

    tiannetWriteHead();

    showTime();

    var dads = document.all.divTiannetDate.style;

    var iX, iY;

    var h = document.all.divTiannetDate.offsetHeight;

    var w = document.all.divTiannetDate.offsetWidth;

//计算left

    iX = tiannetOutObject.offsetLeft + 5;

    /*
     pw= parentobj.style.width+"px";
     iPX1 = parentobj.offsetLeft+"px";
     iPX2 = tiannetOutObject.offsetParent.offsetLeft+"px";
     alert(iPX1+iPX2+pw);
     */
    var parentobj1;
    parentobj1 = tiannetOutObject;
    while(parentobj1.offsetParent != null){
        parentobj1 = parentobj1.offsetParent;
        iX += parentobj1.offsetLeft;
    }

//计算top
    var parentobj2;
    iY = tiannetOutObject.offsetTop+tiannetOutObject.offsetHeight;
    parentobj2 = tiannetOutObject;
    while(parentobj2.offsetParent != null){
        parentobj2 = parentobj2.offsetParent;
        iY += parentobj2.offsetTop;
    }
/*
    if (tiannetOutObject.offsetTop + w > document.body.offsetHeight - 10 )

        iY = document.body.scrollTop + document.body.offsetHeight - w - 5 ;

    else

        iY = document.body.scrollTop +tiannetOutObject.offsetTop + 5;

    if (iY <0)

        iY=0;
*/
    //alert(iX+','+iY);

    dads.left = iX+"px";

    dads.top = iY+"px";

    tiannetShowControl();

    selectObject();

}

//隐藏日历控件(同时显示被强制隐藏的标签)

function tiannetHideControl(){

    document.all.divTiannetDate.style.display = "none";

    tiannetShowObject();

    arrTiannetHide = new Array();//将被隐藏的标签对象清空

}

//显示日历控件(同时隐藏会遮挡的标签)

function tiannetShowControl(){

    document.all.divTiannetDate.style.display = "";

    tiannetHideObject("SELECT");

    tiannetHideObject("OBJECT");

}

//根据标签名称隐藏标签。如会遮住控件的select，object

function tiannetHideObject(strTagName) {

    x = document.all.divTiannetDate.offsetLeft;

    y = document.all.divTiannetDate.offsetTop;

    h = document.all.divTiannetDate.offsetHeight;

    w = document.all.divTiannetDate.offsetWidth;

    for (var i = 0; i < document.all.tags(strTagName).length; i++)

    {

        var obj = document.all.tags(strTagName)[i];

        if (! obj || ! obj.offsetParent)

            continue;

// 获取元素对于BODY标记的相对坐标

        var objLeft = obj.offsetLeft;

        var objTop = obj.offsetTop;

        var objHeight = obj.offsetHeight;

        var objWidth = obj.offsetWidth;

        var objParent = obj.offsetParent;

        while (objParent.tagName.toUpperCase() != "BODY"){

            objLeft += objParent.offsetLeft;

            objTop += objParent.offsetTop;

            objParent = objParent.offsetParent;

        }

        var bolHide = true;

        if( obj.style.display == "none" || obj.style.visibility == "hidden" || obj.getAttribute("Author") == "tiannet" ){

            //如果标签本身就是隐藏的，则不需要再隐藏。如果是控件中的下拉框，也不用隐藏。

            bolHide = false;

        }

        if( ( (objLeft + objWidth) > x && (y + h + 20) > objTop && (objTop+objHeight) > y && objLeft < (x+w) ) && bolHide ){

            //arrTiannetHide.push(obj);//记录被隐藏的标签对象

            arrTiannetHide[arrTiannetHide.length] = obj;

            obj.style.visibility = "hidden";

        }

    }

}

//显示被隐藏的标签

function tiannetShowObject(){

    for(var i = 0;i < arrTiannetHide.length;i ++){

        arrTiannetHide[i].style.visibility = "";

    }

}

//初始化日期。

function tiannetInitDate(strDate){

    var arr = strDate.split(tiannetDateSplit);

    tiannetYear = arr[0];

    tiannetMonth = arr[1];

    tiannetDay = arr[2];

}

//清空

function tiannetClear(){

    tiannetOutObject.value = "";

    tiannetHideControl();

}

//任意点击时关闭该控件
document.onclick=function(){

    with(window.event.srcElement){

        if (tagName != "INPUT" && getAttribute("Author") != "tiannet")

            tiannetHideControl();

    }

}

//按ESC键关闭该控件

document.onkeypress = function(){

    if( event.keyCode == 27 ){

        tiannetHideControl();

    }

}

//触发地图控件
function showMap(o){
    var o = document.getElementById(o);
    o.style.display = "";
    var map = new BMap.Map("mapbody");
    var point = new BMap.Point(113.351021,23.131864);    // 创建点坐标
    var p_lng = document.getElementById('location_j').value;
    var p_lat = document.getElementById('location_w').value;
    if(p_lng&&p_lat)
    {
        var point1 = new BMap.Point(p_lng,p_lat);
        map.centerAndZoom(point1,15);
        var marker1 = new BMap.Marker(point1);
        map.addOverlay(marker1);
        marker1.enableDragging();
        var circle1 = new BMap.Circle(point1,document.getElementById('radius').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
        map.addOverlay(circle1);
        marker1.addEventListener("dragend", function(e){
            map.removeOverlay(circle1);
            document.getElementById('location_j').value = e.point.lng;
            document.getElementById('location_w').value = e.point.lat;
            circle1 = new BMap.Circle(e.point,document.getElementById('radius').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
            map.addOverlay(circle1);
        });
    }
    else
    {
        map.centerAndZoom(point,11);                   // 初始化地图,设置城市和地图级别。
    }
    map.addControl(new BMap.NavigationControl());  //添加默认缩放平移控件
    map.enableScrollWheelZoom();                 //设置鼠标滚轮缩放
    map.addControl(new BMap.ScaleControl());                    // 添加默认比例尺控件
    var map_location = document.getElementById('map_loc').value;
    var map_radis = document.getElementById('map_r').value;
    var markers = new Array();
    var circles = new Array();
    if(map_location!="")
    {
        if(map_radis!="")
        {
            map.removeOverlay(marker1);
            map.removeOverlay(circle1);
            var options = {
                onSearchComplete: function(results){
                    // 判断状态是否正确
                    if (local.getStatus() == BMAP_STATUS_SUCCESS){
                        for (var i = 0; i < results.getCurrentNumPois(); i ++){
                            map.centerAndZoom(results.getPoi(i).point, 16);
                            var marker = new BMap.Marker(results.getPoi(i).point);
                            map.addOverlay(marker);
                            marker.enableDragging();
                            markers[i]=marker;
                            var circle = new BMap.Circle(results.getPoi(i).point,document.getElementById('map_r').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
                            map.addOverlay(circle);
                            circles[i]=circle;
                            /*
                             var p = marker.getPosition();
                             document.getElementById('location_j').value = p.lng;
                             document.getElementById('location_w').value = p.lat;
                             document.getElementById('radius').value = document.getElementById('map_r').value;
                             marker.addEventListener("dragend", function(e){
                             smap.removeOverlay(circle);
                             document.getElementById('location_j').value = e.point.lng;
                             document.getElementById('location_w').value = e.point.lat;
                             circle = new BMap.Circle(e.point,document.getElementById('map_r').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
                             smap.addOverlay(circle);
                             document.getElementById('radius').value = document.getElementById('map_r').value;

                             });
                             */
                        }
                        if (i > 1)
                        {
                            for (var j=0;j < i;j++)
                            {
                                (function(){
                                    var index = j;
                                    markers[j].addEventListener("click", function(e){
                                        for (var k=0; k<i;k++)
                                        {
                                            if (k!=index)
                                            {
                                                map.removeOverlay(markers[k]);
                                                map.removeOverlay(circles[k]);
                                            }
                                        }
                                        document.getElementById('location_j').value = e.point.lng;
                                        document.getElementById('location_w').value = e.point.lat;
                                        document.getElementById('radius').value = document.getElementById('map_r').value;
                                    });
                                    markers[j].addEventListener("dragend", function(e){
                                        for (var k=0; k<i;k++)
                                        {
                                            if (k!=index)
                                            {
                                                map.removeOverlay(markers[k]);
                                                map.removeOverlay(circles[k]);
                                            }
                                        }
                                        map.removeOverlay(circles[index]);
                                        map.removeOverlay(circle);
                                        document.getElementById('location_j').value = e.point.lng;
                                        document.getElementById('location_w').value = e.point.lat;
                                        circle = new BMap.Circle(e.point,document.getElementById('map_r').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
                                        map.addOverlay(circle);
                                        document.getElementById('radius').value = document.getElementById('map_r').value;

                                    });
                                })();
                            }
                        }
                        else
                        {
                            var p = markers[0].getPosition();
                            document.getElementById('location_j').value = p.lng;
                            document.getElementById('location_w').value = p.lat;
                            document.getElementById('radius').value = document.getElementById('map_r').value;
                            markers[0].addEventListener("dragend", function(e){
                                map.removeOverlay(circles[0]);
                                map.removeOverlay(circle);
                                document.getElementById('location_j').value = e.point.lng;
                                document.getElementById('location_w').value = e.point.lat;
                                circle = new BMap.Circle(e.point,document.getElementById('map_r').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
                                map.addOverlay(circle);
                                document.getElementById('radius').value = document.getElementById('map_r').value;

                            });
                        }
                    }
                }
            };

            var local = new BMap.LocalSearch(map, options);
            local.search(map_location);

        }
        else
        {

            map.removeOverlay(marker1);
            map.removeOverlay(circle1);
               var options = {
                    onSearchComplete: function(results){
                        // 判断状态是否正确
                        if (local.getStatus() == BMAP_STATUS_SUCCESS){
                            for (var i = 0; i < results.getCurrentNumPois(); i ++){
                                map.centerAndZoom(results.getPoi(i).point, 16);
                                var marker = new BMap.Marker(results.getPoi(i).point);
                                map.addOverlay(marker);
                                marker.enableDragging();
                                markers[i]=marker;

                                /*
                                 var p = marker.getPosition();
                                 document.getElementById('location_j').value = p.lng;
                                 document.getElementById('location_w').value = p.lat;
                                 document.getElementById('radius').value = document.getElementById('map_r').value;
                                 marker.addEventListener("dragend", function(e){
                                 smap.removeOverlay(circle);
                                 document.getElementById('location_j').value = e.point.lng;
                                 document.getElementById('location_w').value = e.point.lat;
                                 circle = new BMap.Circle(e.point,document.getElementById('map_r').value,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
                                 smap.addOverlay(circle);
                                 document.getElementById('radius').value = document.getElementById('map_r').value;

                                 });
                                 */
                            }
                            if (i > 1)
                            {
                                for (var j=0;j < i;j++)
                                {
                                    (function(){
                                        var index = j;
                                        markers[j].addEventListener("click", function(e){
                                            for (var k=0; k<i;k++)
                                            {
                                                if (k!=index)
                                                {
                                                    map.removeOverlay(markers[k]);
                                                }
                                            }
                                            document.getElementById('location_j').value = e.point.lng;
                                            document.getElementById('location_w').value = e.point.lat;
                                        });
                                        markers[j].addEventListener("dragend", function(e){
                                            for (var k=0; k<i;k++)
                                            {
                                                if (k!=index)
                                                {
                                                    map.removeOverlay(markers[k]);
                                                    map.removeOverlay(circles[k]);
                                                }
                                            }
                                            map.removeOverlay(circles[index]);
                                            map.removeOverlay(circle);
                                            document.getElementById('location_j').value = e.point.lng;
                                            document.getElementById('location_w').value = e.point.lat;
                                        });
                                    })();
                                }
                            }
                            else
                            {
                                var p = markers[0].getPosition();
                                document.getElementById('location_j').value = p.lng;
                                document.getElementById('location_w').value = p.lat;
                                markers[0].addEventListener("dragend", function(e){
                                    map.removeOverlay(circles[0]);
                                    document.getElementById('location_j').value = e.point.lng;
                                    document.getElementById('location_w').value = e.point.lat;

                                });
                            }
                        }
                    }
                };
                var local = new BMap.LocalSearch(map, options);
                local.search(map_location);

        }
        /*
         var marker = new BMap.Marker(point);  // 创建标注
         smap.addOverlay(marker);              // 将标注添加到地图中
         marker.enableDragging();
         var p = marker.getPosition();       //获取marker的位置
         document.getElementById('map_j').value = p.lng;
         document.getElementById('map_w').value = p.lat;
         */

    }
}

function hide(o){
    document.getElementById('map_loc').value="";
    document.getElementById('map_r').value="";
    var o = document.getElementById(o);
    o.style.display = "none";

}

//+++ 20150506 预置策略
//激活预置策略选项
function showprestrategy(){
    if($("#stra_fast_choice").attr("name")=="hide"){
        $("#stra_fast_choice").show();
        $("#stra_fast_choice").attr("name","show")
        loadpreoption();
    }else{
        if($("#stra_fast_choice").val()=="请选择预置策略"){
            $("#stra_fast_choice").hide();
            $("#stra_fast_choice").attr("name","hide");
            $("#stra_fast_choice").val("请选择预置策略");
        }
    }
}
//加载预置策略选项
function loadpreoption(){
    $("#strategy_con #strategy_N #stra_fast_choice").empty();
    $("#strategy_con #strategy_N #stra_fast_choice").append("<option selected='selected'>请选择预置策略</option>")
    //从数据库读出所有预置的策略快照名称
    var obj = {
        _path:'/a/wp/org/get_all_preStra',
        _methods: 'get',
        param: {
            sid:$.cookie("org_session_id"),
            types:"preStra"
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt==0) {
            var preStraList=JSON.parse(data.preStraList);
            for (preStra in preStraList){
                $("#strategy_con #strategy_N #stra_fast_choice").append("<option value='"+preStraList[preStra].desc+"' style='color:blue'>"+preStraList[preStra].desc+"</option>")
            }
            $("#strategy_con #strategy_N #stra_fast_choice").append("<option value='addpre' style='color:red'>(新增预置策略)</option>")
        }
        else{
            loadingStatus('预置策略获取失败！',0);
        }
    });
}
//加载预置策略
function loadprestrategy(option){
    var desc=option.value;
    if (desc=="addpre"){
        $("#delPreStra").hide();
        $("#addPreStra").show();
        return;
    }else if (desc=="请选择预置策略"){
        $("#delPreStra").hide();
        $("#addPreStra").hide();
        return;
    }else{
        $("#strategy_con .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
        choiceBaseStation();
        $("#delPreStra").show();
        $("#addPreStra").hide();
        var users=[];
        var obj={
            _path:"/a/wp/org/get_strategy_by_desc",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                desc:desc
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            var strategy=data.strategy;
            if(rt == 0)
            {
                loadingStatus("加载预置策略成功!",0);
                if (strategy.length!=0){
                    if(strategy['lon']!="")
                        document.getElementById('location_j').value=strategy['lon'];
                    if(strategy['lat']!="")
                        document.getElementById('location_w').value=strategy['lat'];
                    if(strategy['radius']!="")
                        document.getElementById('radius').value=strategy['radius'];
                    document.getElementById('desc').value=desc;
                    document.getElementById('camera').value=strategy['camera'];
                    //document.getElementById('bluetooth').value=strategy['bluetooth'];
                    document.getElementById('wifi').value=strategy['wifi'];
                    document.getElementById('tape').value=strategy['tape'];
                    document.getElementById('gps').value=strategy['gps'];
                    document.getElementById('mobiledata').value=strategy['mobiledata'];
                    document.getElementById('usb_connect').value=strategy['usb_connect'];
                    document.getElementById('usb_debug').value=strategy['usb_debug'];
                }
            }else{
                loadingStatus("加载预置策略失败!",0);
            }
        },"正在加载预置策略...");
        document.getElementById("strategy_con").style.display="block";
    }
}
//+++ 20150507 删除预置策略
$("#delPreStra").click(function(){
    var desc=$("#stra_fast_choice").find("option:selected").text();
    var obj = {
        _path:'/a/wp/org/del_preStra',
        _methods: 'get',
        param: {
            sid:$.cookie("org_session_id"),
            desc:desc
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt==0) {
            loadingStatus('删除预置策略成功！',0);
            $("#stra_fast_choice").hide();
            $("#stra_fast_choice").attr("name","hide");
            $("#stra_fast_choice").val("请选择预置策略");
            $("#delPreStra").hide();
        }
        else{
            loadingStatus('删除预置策略失败！',0);
        }
    });
});
//+++ 20150507 新增预置策略
$("#addPreStra").click(function(){
    var id = getStrategyID();
    var start_time = $("#start_time");
    var end_time = $("#end_time");
    var desc = $("#desc");
    var location_j = $("#location_j");
    var location_w = $("#location_w");
    var radius = $("#radius");
    var baseStationID = $("#baseStationID");
    var camera = $("#camera");
    //var bluetooth = $("#bluetooth");
    var wifi = $("#wifi");
    var tape = $("#tape");
    var gps = $("#gps");
    var mobiledata = $("#mobiledata");
    var usb_connect = $("#usb_connect");
    var usb_debug = $("#usb_debug");
    //判断描述是否字符过长
    if(desc.val().length>15){
        alert("您输入的策略描述过长，请输入少于15个字！")
        return;
    }
    //判断半径是否合法
    if(isNaN(radius.val())){
        alert("您输入的半径有误，请重新输入！");
        return;
    }
    var users = JSON.stringify([]);
    var userdesc = JSON.stringify([]);
    var session_id  = $.cookie("org_session_id");
    //如果有错误提示，取消提示
    start_time.removeClass("errMsn");
    end_time.removeClass("errMsn");
    location_j.removeClass("errMsn");
    location_w.removeClass("errMsn");
    radius.removeClass("errMsn");
    baseStationID.removeClass("errMsn");
    var bluetooth = "bjy";
    if(wifi.val()=="wfjy"){
        bluetooth = "bfjy";
    }else{
        bluetooth = "bjy";
    }
    //+++ 20150506 添加预置策略
    var obj = {
        _path: '/a/wp/org/send_pre_strategy',
        _methods: 'post',
        param: {
            types:"preStra",   //添加预置策略
            start: start_time.val(),
            end: end_time.val(),
            desc:desc.val(),   //desc_val,
            lon: location_j.val(),
            lat: location_w.val(),
            radius: radius.val(),
            baseStationID: baseStationID.val(),
            camera: camera.val(),
            bluetooth: bluetooth,
            wifi: wifi.val(),
            tape: tape.val(),
            gps: gps.val(),
            mobiledata: mobiledata.val(),
            usb_connect: usb_connect.val(),
            usb_debug: usb_debug.val(),
            users:users,
            userdesc:userdesc,
            sid: session_id,
            id:id,
            //+++0629加入强制管控字段
            force:0
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt === 0) {
            loadingStatus("添加预置策略成功！", 0);
            $("#stra_fast_choice").hide();
            $("#stra_fast_choice").attr("name","hide");
            $("#stra_fast_choice").val("请选择预置策略");
            $("#addPreStra").hide();
        }else{
            loadingStatus("添加预置策略失败！", 0);
        }
    });
});

//+++ 20150528
function judge_wifi_data(obj){
    if(obj.value=="wjy"){
        document.getElementById("mobiledata").disabled=true;
    }else{
        document.getElementById("mobiledata").disabled=false;
    }
    if(obj.value=="mjy"){
        document.getElementById("wifi").disabled=true;
    }else{
        document.getElementById("wifi").disabled=false;
    }
}