/**
 * Created by arron_rose on 2016/12/7.
 */
$(document).ready(function () {
    //var para=UrlParm.parm("param");
    //alert(para);
    function parseUrl(){
        var Ohref=window.location.href;
        var arrhref=Ohref.split("?param=");
        return arrhref[1];
    }
    var arr = parseUrl();
    selectuid=arr.split(",");
    console.log(selectuid);



    sid="wjz";
    //var wjz = new WebSocket("ws://111.204.189.58:6001/ws/"+sid);
    var wjz = new WebSocket("ws://111.204.189.34:6001/ws/"+sid);
    wjz.onopen = function() {
        console.log("open wjz websocket successful");
    };
    wjz.onmessage = function(evt) {
        var data=evt.data;

        showphones(data);
        //$("#show").append(data + "</br>");
    };
    wjz.onclose = function(evt) {
        console.log("WebSocketClosed!");
        console.log(evt);
    };
    wjz.onerror = function(evt) {
        console.log("WebSocketError!");
    };



    sid="jcm";
    //var jcm = new WebSocket("ws://111.204.189.58:6001/ws/"+sid);
    var jcm = new WebSocket("ws://111.204.189.34:6001/ws/"+sid);
    jcm.onopen = function() {
        console.log("open jcm websocket successful");
    };
    jcm.onmessage = function(evt) {
        var data=evt.data;
        console.log(data);
        showalarms(data);
    };
    jcm.onclose = function(evt) {
        console.log("WebSocketClosed!");
        console.log(evt);
    };
    jcm.onerror = function(evt) {
        console.log("WebSocketError!");
    };


    $(".jscroll").mCustomScrollbar({
        updateOnContentResize: true
    });

});


function showphones(data) {

    console.log(data);
    var text=data;
    num=text.search(/text/);
    //datas={"uid": "4334", "bsphone_time": 1481771923, "bsphone_IMSI": 460078105542579, "bsphone_uid": "", "bsphone_IMEI": "", "bsphone_standard": "gsm"}
    datas=text.substring(num+7,text.length-2);
    console.log("text 的主要内容：")
    console.log(datas);
    all=JSON.parse(datas);
    for(j=0;j<selectuid.length;j++){
        if(selectuid[j]== all.uid){
            showrightdownlist(all);
            showleftdownlist(all);
        }
    }
}
var a=0;
function showrightdownlist(all){

    if(all['phone_status']=="0"){
        var strs="已管控";
    }else{
        var strs="已退出";
    }
    a++;
    var xuhao=a;
    var txt;
    txt="";
    txt+='<tr class="'+all['uid']+'" id="'+all['bsphone_IMSI']+'">';
    txt+='<td><span class="checkbox checkbox_uncheck" ></span></td>';
    txt+='<td id="'+xuhao+'">'+xuhao+'</td>';
    txt+='</td><td id="'+all['uid']+'">'+all['uid']+'</td>';
    txt+='<td class="phone_IMSI">'+all['bsphone_IMSI']+'</td>';
    //txt+='<td class="phone_number">'+all['bsphone_uid']+'</td>';
    txt+='<td class="phone_standard">'+all['bsphone_standard']+'</td>';
    txt+='<td class="phone_time">'+all['bsphone_time']+'</td>';
    txt+='<td class="phone_status">'+strs+'</td>';

    txt+='</tr>';
    $("#wjzD tbody").append(txt);
    $("#shebeiWD").mCustomScrollbar("update");
}
function showleftdownlist(all){
    uid=all.uid;
    obj={
        _path:"/a/wp/org/control_tree_info",
        _methods:"get",
        param: {

            uid: uid
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        console.log(rt);
        console.log(all);
        console.log(all[0]['uid']);
        if (rt != 0) {
            loadingStatus("显示错误！", 0);
        } else {
            document.getElementById('wTurnOnTime').innerHTML =all[0]['last_time'];
            document.getElementById('wGroupDev').innerHTML =all[0]['uid'];
            document.getElementById('wPosDe').innerHTML =all[0]['position'];


        }
    });
}
function showalarms(data){

    console.log(data);
    var text=data;
    num=text.search(/text/);
    datas=text.substring(num+7,text.length-2);

    console.log(datas);
    all=JSON.parse(datas);
    //setTimeout(shutdown(all.uid),5000000000000000);
    setTimeout(function(){
        uid=all.uid;
        obj={
            _path:"/a/wp/user/shutdown",
            _methods:"post",
            param: {
                uid: uid
            }
        };
        ajaxReq(obj,function(data){
        // 暂时无返回
            console.log("shutdown ok")
        })
    },3600000);
    console.log(1);
    for(j=0;j<selectuid.length;j++){
        if(selectuid[j]== all.uid){
            showrightuplist(all);
            showleftuplist(all);
        }
    }
}

function showleftuplist(all){
    uid=all.uid;
    obj={
        _path:"/a/wp/org/control_tree_info",
        _methods:"get",
        param: {

            uid: uid
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("显示错误", 0);
        } else {
            document.getElementById('jTurnOnTime').innerHTML =all[0]['last_time'];
            document.getElementById('jGroupDevId').innerHTML =all[0]['uid'];
            document.getElementById('jPosDe').innerHTML =all[0]['position'];



        }
    });

}
b=0;
c=0;
function showrightuplist(all){
    b++;
    var xuhao=c+1;
    var txt;
    if(all['sg_position']!="0"){
        txt="";
        txt+='<tr class="'+all['uid']+'" >';
        //txt+='<td id="'+xuhao+'">'+xuhao+'</td>';
        txt+='<td id="xuhao">'+xuhao+'</td>';
        txt+='<td class="sg_uid">'+all['uid']+'</td>';
        txt+='<td class="sg_time">'+all['sg_time']+'</td>';
        txt+='<td class="sg_postion">'+all['sg_position']+'</td>';
        txt+='</tr>';
        //document.getElementById('PassNum').innerHTML =b;
        ////if(all['sg_position'] !=="0"){
        ////    c++;
        ////}
        c++;
        //document.getElementById('AlterNum').innerHTML =c;
        //$("#jcmD tbody").append(txt);
        //$("#shebeiJD").mCustomScrollbar("update");
    }
    document.getElementById('PassNum').innerHTML =b;
    //if(all['sg_position'] !=="0"){
    //    c++;
    //}

    document.getElementById('AlterNum').innerHTML =c;
    $("#jcmD tbody").append(txt);
    $("#shebeiJD").mCustomScrollbar("update");

}


$("#cselect_page").live("click",function(event){
    if(event.target.className=="checkbox checkbox_uncheck"){
        event.target.className="checkbox checkbox_checked";
        $("#wjzD tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
    }else {
        event.target.className = "checkbox checkbox_uncheck";
        $("#wjzD tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    }
});
$("#wjzD tbody tr .checkbox").live("click",function(event){
    console.log(event.target.className);
    if(event.target.className=="checkbox checkbox_uncheck"){
        event.target.className="checkbox checkbox_checked";
        //$("#wjzD tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
        console.log(event.target.parentNode.parentNode.childNodes[1].textContent);//ȡ�õ���imsi��
    }else {
        event.target.className = "checkbox checkbox_uncheck";
    }
});

$("#sendMes").live('click',function(event){
    event.preventDefault();
    number=$("#purlMes_num").val().toString();
    sms=$("#purlMes").val();
    arr=document.getElementsByClassName("checkbox");
    for(i=0;i<arr.length;i++){
        if(arr[i].className=="checkbox checkbox_checked") {
            var uid = arr[i].parentNode.parentNode.className;
            var imsi = arr[i].parentNode.parentNode.id;
            imsis=imsi.toString();
            obj = {
                _path: "/a/wp/user/modmsg",
                _methods: "post",
                param: {

                    uid: uid, // uid 伪基站设备基站号
                    imsi: imsis, // imsi 手机imsi号
                    sms: sms,// sms 手机发送的短信内容
                    number:number,//number 伪装的手机号码
                    cmd:"send_msg",// cmd 发送短信的指令
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("短信发送成功！",0);
                }else{
                    loadingStatus("短信发送失败!",0);
                }
            },"短信正在发送中...")
        }
    }
});

$("#sendCall").live('click',function(event){
    event.preventDefault();
    number=$("#purlCall").val().toString();
    arr=document.getElementsByClassName("checkbox");
    for(i=0;i<arr.length;i++){
        if(arr[i].className=="checkbox checkbox_checked") {
            var uid = arr[i].parentNode.parentNode.className;
            var imsi = arr[i].parentNode.parentNode.id;
            imsis=imsi.toString();
            obj = {
                _path: "/a/wp/user/callphone",
                _methods: "post",
                param: {

                    uid: uid, // uid 伪基站设备号
                    imsi: imsis, // imsi 手机imsi号
                    number:number,//number 伪装的手机号
                    cmd:"call_phone",// cmd 伪装电话通信的指令
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("伪装通信成功!",0);
                }else{
                    loadingStatus("伪装通信失败!",0);
                }
            },"正在通信中...")
        }
    }
});

$("#AddWhite").live('click',function(){
    number=$("#purlCall").val().toString();
    arr=document.getElementsByClassName("checkbox");
    for(i=0;i<arr.length;i++){
        if(arr[i].className=="checkbox checkbox_checked") {
            var uid = arr[i].parentNode.parentNode.className;
            var imsi = arr[i].parentNode.parentNode.id;
            imsis=imsi.toString();
            obj = {
                _path: "/a/wp/user/modwhitelist",
                _methods: "post",
                param: {

                    uid: uid, // uid 伪基站设备号
                    imsi: imsis, // imsi 手机imsi号
                    cmd:"change_whitelist",// cmd 添加白名单指令
                    change:"1",//1 表示添加到白名单
                }
            };
            ajaxReq(obj,function(data){
                var rt=data.rt;
                if(rt==0){
                    loadingStatus("添加白名单成功!",0);
                }else{
                    loadingStatus("添加白名单失败!",0);
                }
            },"正在添加白名单中...")
        }
    }
});

$("#cancleCall").click(function(event) {
    $("#pop_fakeCall").close();
});
$("#cancleMes").click(function(event) {
    $("#pop_mesInfo").close();
});
