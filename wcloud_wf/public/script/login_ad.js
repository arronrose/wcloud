var $login=$("#login");
var $logout=$("#logout");
var allUsers="";
//+++ 20150730
var userPerPageGlobal=50;
//+++ 20151026
var ldap_base_dn = "dc=test,dc=com";
var mod_user_info_ous = null;

try{
    /*弹出层的设置*/
    $(".dialog").each(function(index, element) {
        var $width = $(this).outerWidth(); //宽度默认300， 添加宽度。
        $(this).dialog({ //所有添加dialog类的元素都会变成弹出层 开始是隐藏的
            width: $width,
            autoOpen: false,
            modal: true,
            resizable: false//,
            //show: "scale"
        });
    });
    $(".cb").click(function(event) { /*所有添加cb类的元素都弹出他连接对应的模块*/
        var id = this.href.split("#")[1];
        id = "#" + id;
        $(id).dialog("open");
        return false;
    });
}catch(err){}

//实现登陆功能
$login.submit(function(event){
    event.preventDefault();
    var uidV=$("#uid").val();
    var pwV=$("#password").val();
    var capt= $("#captcha").val();
    var src=$("#yanz").attr("src")+'?'+Math.random();
    if(!verViod(uidV)){
        alert("用户名不能为空!");
        $("#yanz").attr("src",src);
        $("#uid").focus();
        return false;
    }else if(uidV.TextFilter()!=uidV){
        alert("用户名非法，请重新输入！");
        $("#yanz").attr("src",src);
        return false;
    }else if(!verViod(pwV)){
        alert("密码不能为空!");
        $("#yanz").attr("src",src);
        $("#password").focus();
        return false;
    }else if(!verViod(capt)){
        alert("验证码不能为空!");
        $("#yanz").attr("src",src);
        $("#captcha").focus();
        return false;
    }
    //+++ 20150804 判断验证码
    var session_id= $.cookie("capSession");
    //console.log(session_id);
    //验证码sha1加密
    var capt2=capt.toLocaleLowerCase();
    var encry_captcha=SHA1(capt2).toLocaleLowerCase();
    /***************/
    var obj={
        _path:"/a/wp/org/login",
        _methods:"post",
        param:{
            uid:uidV,
            pw:pwV,
            session_id:session_id,
            captcha:encry_captcha
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        var sid=data.sid;
        var config=data.is_config_ok;
	var loginType=data.loginType;
        console.log(loginType);
        //+++20151125 前台直接请求后端
        upload_ip($("#uid").val(),loginType+"login",rt);
        if(rt==0){
            //确保清空缓存
            sessionStorage.clear();
            //登陆成功之后，实现记住账号
            var saveUid=$("#saveUid");
            if(saveUid.hasClass("checkbox_checked")){
                $.cookie("uid",uidV,{ expires: 30 });
            }else if(saveUid.hasClass("checkbox_uncheck")){
                $.cookie("uid",null);
            }
            loadingStatus("正在跳转!",0);
            $.cookie("org_session_id",sid);
            $.cookie("configStatus",config);
            $.cookie("userid",uidV);
            $.cookie("loginType",loginType);
            if(config==0){
                location.href="/f_org_setLDAP";
            }else if(config==1) {
                if (loginType == 'master') {
                    location.href = "/f_org_master_list";
                } else if (loginType == 'admin') {
                    location.href = "/f_org_home";
                } else if (loginType == 'auditor') {
                    location.href = "/f_org_auditor_list";
                } else if (loginType == 'sa') {
                    location.href = "/f_org_sa_list";
                } else {
                    loadingStatus("登陆失败!", 0);
                }
            }
        }else if(rt==60){
            $("#yanz").attr("src",src);
            loadingStatus("验证码已过期!",0);
        }else if(rt==23){
            $("#yanz").attr("src",src);
            loadingStatus("验证码错误!",0);
        }else if(rt==2){
            $("#yanz").attr("src",src);
            loadingStatus("用户名或密码错误!",0);
        }else if(rt==17){
            $("#yanz").attr("src",src);
            loadingStatus("不存在的用户!",0);
        }else if(rt==62){
//            $("#yanz").attr("src",src);
//            loadingStatus("!",0);
            alert("系统维护中，请稍后登录");
        }
        else{
            $("#yanz").attr("src",src);
            loadingStatus("登陆失败!",0);
        }
    },"正在登陆...");
});
//+++ 20151125 登录成功之后向服务器端报告IP，或者真实登录的接口
function upload_ip(sid,action,rt){
    var timestamp = Date.parse(new Date());
    var time = parseInt(timestamp)/1000;
    var obj = {
        _path:"/a/wp/org/upload_ip",
        param:{
            admin: sid,
            action:action,
            time:time,
            result:rt
        }
    };
    sendAjaxRequest(obj,function(data){
        console.log(data);
    },"正在登陆");
}

function sendAjaxRequest(obj,func,str) {
    $.ajax({
        async: true,
        timeout: 60000,
        type: "post",
        url: "http://111.204.189.58:8082"+obj._path,
        data: obj.param,
        dataType: 'jsonp',
//        jsonpCallback:func,
        beforeSend: function (jqXHR) {
            if (!!str) {
                loadingStatus(str, 1);
            }
        },
        success: function (data) {
            var rt = data.rt;
            switch (rt) {
                case 4:
                case 6:
                case 8:
                    $.cookie("org_session_id", null);
                    $.cookie("configStatus", null);
                    location.href = "/";
                    break;
                default:
                    func(data);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            //console.log('解析对像:' + JSON.stringify(jqXHR));
        }
    });

}
//+++ 20150917 登陆过程完成之后订阅通道号为sid的一个pushserver上的通道
function connectToPushServer(sid){
    //console.log("connectToPushServer:"+sid);
    if(sid){
        window.ws = null;
        //var count = 1;
        //for(var i=0;i<200;i++){
        if ('WebSocket' in window) {
            window.ws = new WebSocket("ws://111.204.189.58:6001/ws/"+sid);
            //console.log("sub success,url is ws://www.secmobile.cn:8001/ws/"+sid);
            //console.log("时间是"+Date.parse(new Date()).toString());
        }
        else if ('MozWebSocket' in window)
            window.ws = new MozWebSocket("ws://111.204.189.58:6001/ws/"+sid);
        else
            console.log("not support");
        window.ws.onmessage = function (evt) {
            var message = evt.data;
            handle(message);
        };

        window.ws.onclose = function (evt) {
            //这个待改动，不能让用户看到连接
            //console.log("一个连接关闭了");
            //console.log("连接关闭时间是"+Date.parse(new Date()).toString());
            connectToPushServer($.cookie("org_session_id"));
        };
    }
}
//+++20150917 关闭页面时关闭连接
$(window).bind('unload', function () {
    //+++20150917 页面跳转的时候将连接关闭
    window.ws.close(1000);//1000是接口要求
});

//+++ 20150918 加载页面时维持连接
$(document).ready(function () {
    connectToPushServer($.cookie("org_session_id"));
});

function handle(message){
    //handle pushed messages
    //console.log(message);
    var messageJson = JSON.parse(message);
    //console.log(messageJson.text);
    var info = messageJson.text;
    //console.log("info is "+info);
    switch(info.split(":")[0]){
        case "cmd":
            var cmd = info.split(":")[1];
            var num = info.split(":")[2];
            if(num>0){
                deal_devs($.cookie("org_session_id"),[],cmd);
            }
            break;
        case "strategy":
            var operation = info.split(":")[1];
            if(operation=="DelStrategy"){
                var stra_str = info.split(":")[2];
                var stra_ids = [];

                if(stra_str==""){
                    loadingStatus("策略已全部被成功删除!",0);
                    alert("策略已全部被成功删除!");
                    location.replace(location.href);
                }else{
                    stra_ids = stra_str.split(",");
                    loadingStatus("存在用户未删除策略!",0);
                    var delinfo = "DelStrategy:"+JSON.stringify(stra_ids);
                    //console.log("delinfo"+delinfo);
                    //+++ 20150916 三个处理函数合并
                    deal_users($.cookie("org_session_id"),[],delinfo);
                }
            }else{
                var subinfo = info.substring(info.indexOf(":")+1);
                deal_users($.cookie("org_session_id"),[],subinfo);
            }
            break;
    }
}
//检测cookie中有没有uid字段，是否启用了记住账号的功能
(function checkuid(){
    if($.cookie("uid")){
        $("#uid").val($.cookie("uid"));
        $("#saveUid").removeClass("checkbox_uncheck").addClass("checkbox_checked");
    }
})();
//实现退出功能
$logout.click(function(event){
    event.preventDefault();
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
        //upload_ip($.cookie("userid"),loginType+"logout",rt);
        if(rt==0){
            loadingStatus("正在退出...",0);
            sessionStorage.clear();
            $.cookie('totalUsersNumber',0);
            $.cookie("org_session_id",null);
            $.cookie("configStatus",null);
            location.href="/";
        }else{
            loadingStatus("操作失败!",0);
        }
    },"正在退出...");
});
//获取公司信息
(function(){
    var href=location.href;
    if(href.indexOf('acc')>-1){
        acc();
    }else if(href.indexOf('setLDAP')>-1){
        setLDAP();
    }else if(href.indexOf('home')>-1){
        home(true);
        getlocs();
        //+++20150831 加入每个页面用户数量的说明
        $("#users_perpage").html("（每页"+userPerPageGlobal+"条）");
        //+++20150914 加入轮询获取设备状态线程
        newloopUp();
        mloadselect();
    }else if(href.indexOf('strategy')>-1){
        loadstrategys();
        home(false);
    }else if(href.indexOf('contacts')>-1){
        home(false);
        showTree();
    }else if(href.indexOf('statistics')>-1){
        home(false);
    }else if(href.indexOf('mapp')>-1){
        home(false);
    }else if(href.indexOf('trace')>-1){
        trace();
        judgeyemianqx();
    }else if(href.indexOf('master')>-1){   //+++从这里添加
        masterinit();
        masterhome();
    }else if(href.indexOf('admin_list')>-1){
        adminhome();
    }else if(href.indexOf('auditor')>-1){
        auditorinit();
        auditorhome();
    }else if(href.indexOf('auditor_list')>-1){
        auditorhome();
    }else if(href.indexOf('auditlog')>-1){
        loadauditorlog();
    }else if(href.indexOf('sa')>-1){
        sainit();
        sahome();
    }else if(href.indexOf('sa_list')>-1) {
        sahome();

    }else if(href.indexOf('control')>-1){
        controlhome();
    }
})();

function trace(){
    //创建地图
//    alert(1);
//    var map = new BMap.Map("trace_cr");
    var map1 = new BMap.Map("tracemap");//在地图容器中创建地图
//    alert(2);
    map1.addControl(new BMap.NavigationControl());  //添加默认缩放平移控件
    map1.enableScrollWheelZoom();                 //设置鼠标滚轮缩放
    map1.addControl(new BMap.ScaleControl());                    // 添加默认比例尺控件
    var point = new BMap.Point(116.220686,39.979471);
    map1.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中
    window.tracemap = map1;  //为轨迹地图创建一个全局变量
}


function acc(){
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
        //管理权限
        var admin_right;
        //通信权限
        var admin_txqx;
        //用户名
        var uid=$.cookie("userid");
        if(rt==0){
            loadingStatus("成功获取管理员信息！",0);
            admin_right = data.org_right;
            console.log(admin_right);
            admin_txqx = data.org_contact_ous;
            console.log(admin_txqx);
            admin_email=data.admin_email||"";
        }else{
            loadingStatus("未能获取到管理员信息!",0);
        }
        //显示管理员姓名
        setText($("#adName"),uid);
        //显示管理员-管理权限
        setText($("#adminqx"),get_oudn_name(admin_right));
        //$("#adminqx").attr("oudn",admin_right);
        ////显示管理员-通信权限
        setText($("#admintxqx"),get_ou_dn(admin_txqx));
        //$("#admintxqx").attr("oudn",admin_txqx);
	},"正在获取管理员信息!");
//	loadLogo();oudn
}
//上传操作
$("#forfile").click(function(event){
    $("#logtu").click();
});

$("#logtu").change(function(event){
	var val=$(this).val()
	if(!val) return false;
	$("#lsid").val($.cookie("org_session_id"));
	$("#leslogo").submit();
	loadingStatus("正在上传...",1);
	$("#forfile").attr("disabled",true);
});
//下载头像
function loadLogo(){
	$("#forfile").attr("disabled",false);
	var obj={
		_path:"/a/wp/org/logo",
		_methods:"get",
		param:{
			sid:$.cookie("org_session_id")
		}
	};
	ajaxReq(obj,function(data){
		if(data.rt==0){
			var type=data["img_type"];
			var b64=data["logo_base64"];
			var tou="";
			if(type=="jpg"){
				b64="data:image/jpg;base64,"+b64;
			}else if(type=="png"){
				b64="data:image/png;base64,"+b64;
			}
			if(!!b64){
				//var img=document.createElement("img");
				//img.src=b64;
				//document.body.appendChild(img);
				$(".kao").attr("src",b64);
			}
		}
	});
}
//图片类型错误时
function typeerr(){
	loadingStatus("上传图片类型错误!",0);
	$("#forfile").attr("disabled",false);
}

function waitL(data){
	$("#forfile").attr("disabled",false);
	var rt=data.rt;
	if(rt==0){
		loadingStatus("上传成功",0);
		loadLogo();
	}else{
		loadingStatus("上传失败",0);
	}
}

function setLDAP(){
	//获取ldap的用户配置信息
	var obj={
		_path:"/a/wp/org/ldap_config",
		_methods:"get",
		param:{
			sid:$.cookie("org_session_id")	
		}
	};
	ajaxReq(obj,function(data){
		var rt=data.rt;
		if(rt==0){
			loadingStatus("成功获取到LDAP配置信息!");
			for(var i in data){
				if(i=="rt"){
					continue;
				}
				var id="#"+i;
				$(id).val(data[i]);
			}
		}else{
			loadingStatus("未能获取到LDAP配置信息!")
		}
	},"正在获取LDAP配置信息!");
	checkConfig();
	$(".x").live("click",closeC);
	$("#qx").click(function(event){$("#setA").hide();});
	$("#manu").live("click",manuTongbu);
}
//手动同步
function manuTongbu(event){
	event.preventDefault();
	var org_session_id=$.cookie("org_session_id");
	var obj={
		_path:"/a/wp/org/ldap_sync",
		_methods:"post",
		param:{
			sid:org_session_id
		}
	};
	ajaxReq(obj,function(data){
		var rt=data.rt;
		if(rt==0){
			loadingStatus("同步成功!",0);
		}else{
			loadingStatus("同步失败!",0);
		}
	},"正在同步...");
}

function closeC(event){
	event.preventDefault();
	$(this).parent().parent().hide();
}
//检测ldap设置是否完成。
function checkConfig(){
	if(!!$.cookie("configStatus")){
		$("#sq").attr("disabled",false);
		$("#manu").attr("disabled",false);
		openLock();
	}else{
		$("#sq").attr("disabled",true);
		$("#manu").attr("disabled",true);
		$("#kaiguan").attr("disabled",true);
		$("#iterval").addClass("select_disabled");
	}
}
//解锁自动同步
function openLock(){
	var obj={
		_path:"/a/wp/org/ldap_sync_config",
		_methods:"get",
		param:{
			sid:$.cookie("org_session_id")
		}
	};
	ajaxReq(obj,function(data){
		var rt=data.rt;
		//console.log(data);
		if(rt==0){
			var cyc=data.ldap_sync_cycle;
			var day=24;
			var week=day*7;
			var tweek=week*2;
			var mon=day*30;
			var year=mon*12;
			var ch="";
			if(cyc>0){
				if(cyc>=year){
					ch="每年";
				}else if(cyc>=mon){
					ch="每个月";
				}else if(cyc>=tweek){
					ch="每两周";
				}else if(cyc>=week){
					ch="每周";
				}else if(cyc>=day){
					ch="每天"
				}
				$("#kaiguan").removeClass("jiaonang_disabled").addClass("jiaonang_open");
				$("#iterval").removeClass("select_disabled");
				$("#tm").html(ch);
			}else{
				$("#kaiguan").removeClass("jiaonang_open").addClass("jiaonang_disabled");
				$("#tm").html("选择同步时间");
			}

		}
	})
}
//是否自动同步选择
$("#kaiguan").click(function(event){
	//console.log($(this).attr("class"));
	var that=$(this);
	if(that.hasClass("jiaonang_open"))		//如果现在是打开状态，点击后应该是闭合状态。
	{
		$("#iterval").addClass("select_disabled");
	}else if(that.hasClass("jiaonang_close")){
		$("#iterval").removeClass("select_disabled");
	}
});
//+++20150729 每次页面切换时重置用户的选择情况
//点击每天或者没周之后，发送修改结果存储到服务器
$("#iterval .option").click(function(event){
	var txt=$(this).html();
	var cyc=0;
	switch(txt){
		case "每年":
		cyc=24*30*12;
		break;
		case "每个月":
		cyc=24*30;
		break;
		case "每两周":
		cyc=24*14;
		break;
		case "每周":
		cyc=24*7;
		break;
		case "每天":
		cyc=24;
		break;
		default:
		cyc=0;
	};
	var obj={
		_path:"/a/wp/org/ldap_sync_config",
		_methods:"post",
		param:{
			sid:$.cookie("org_session_id"),
			ldap_sync_cycle:cyc
		}
	};
	ajaxReq(obj,function(data){
		var rt=data.rt;
		//console.log(data);
		if(rt==0){
			loadingStatus("修改成功!",0);
		}else{
			loadingStatus("修改失败!",0);
		}
	},"正在修改同步频率...");
});
//点击授权按钮之后，获取所有用户
$("#sq").live("click",function(event){
	event.preventDefault();
	$("#setA").show();
	var obj={
		_path:"/a/wp/org/ldap_users",
		_methods:"get",
		param:{
			sid:$.cookie("org_session_id")
		}
	};
	ajaxReq(obj,function(data){
		var jrq=$("#pzz");
		var rq=$("tbody",jrq);
		rq.html("");
		var rt=data.rt;
		if(rt==0){
			var users=data['users'];
			var nau_users=data["nau_users"];
			var str='';
			for(var i=0,len=users.length;i<len;i++){
				str='';
				str+='<tr><td><span class="checkbox checkbox_checked"></span></td><td class="tc dev_id">';
				str+=users[i]['username'];
				str+='</td></tr>';
				rq.append(str);
				jrq.mCustomScrollbar("update");
			}
			for(var k=0,l=nau_users.length;k<l;k++){
				str='';
				str+='<tr><td><span class="checkbox checkbox_uncheck"></span></td><td class="tc dev_id">';
				str+=nau_users[k]['username'];
				str+='</td></tr>';
				rq.append(str);
				jrq.mCustomScrollbar("update");
			}
		}else{

		}
	});
});
//点击提交授权管理
$("#tj").live("click",function(event){
	var uids=[];
	var org_session_id=$.cookie("org_session_id");
	// $("#pzz tbody tr .checkbox_checked").each(function(index,element){
	// 	uids.push($(".dev_id",$(element).parent().parent()).html());
	// });
	var obj={
		_path:"/a/wp/org/ldap_users_allow_use",
		_methods:"post",
		param:{
			sid:org_session_id
			//uids:uids
		}
	};
	$("#pzz tbody tr .checkbox_checked").each(function(index,element){
		//uids.push($(".dev_id",$(element).parent().parent()).html());
		var key='uid'+index;
		obj.param[key]=$(".dev_id",$(element).parent().parent()).html();
	});
	ajaxReq(obj,function(data){
		var rt=data.rt;
		if(rt==0){
			loadingStatus("授权成功!",0);
			$("#setA").hide();
		}else{
			loadingStatus("授权失败!",0);
		}
	},"正在提交...")
});
//提交ldap的用户配置信息
$("#setldap").submit(function(event){
	event.preventDefault();
	var obj={
		_path:"/a/wp/org/ldap_config",
		_methods:"post",
		param:{
			sid:$.cookie("org_session_id")
		}
	};
	var input=$("#setldap input");
	for(var i=0,len=input.length;i<len;i++){
		if(input[i].type=="button"||input[i].type=="submit"||input[i].type=="reset"||!verViod(input[i].value)){
			continue;	//如果类型为button submit reset或者是空值，则调到下一个循环
		}
		var key=input[i].id;	//键等于id
		obj.param[key]=input[i].value;	//值等于
	}
	ajaxReq(obj,function(data){
		//console.log(obj);
		//console.log(data);
		if(data.rt==0){
			loadingStatus("提交成功!",0);
			$.cookie("configStatus",1)
		}else{
			loadingStatus("提交失败!",0);
			$.cookie("configStatus",0);
		}
		checkConfig();
	},"正在提交！");
});

function showson(title){
    alert(title);
    var obj={
        _path:"/a/wp/org/ldap_onelevel" ,
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            oudn:title
        }
    };

    ajaxReq(obj,function(data){
        var rt=data.rt;
        var ous=data.ous;

        var users = data.users;

        if (rt != 0) {
        } else {
            loadingStatus("成功获取群组信息！", 0);
            var div = document.getElementById(title);
            div.style.marginLeft = "20px";
            for (var i = 0, len = ous.length; i < len; i++) {
                var dn = ous[i]["dn"];

                var ou = ous[i]["ou"];
                var son = document.createElement("div");
                son.name = "ou";
                son.style.cursor = "pointer";
                son.title = dn;
                //son.attachEvent("onclick",showson("this.title"));
                //bindEvent(son,"click",showson(this.title));
                son.onclick = showson(this.title);

                var span = document.createElement("span");
                span.className = "checkbox checkbox_uncheck";

                var img = document.createElement("img");
                img.src="images/group.png";

                var a = document.createElement("a");
                a.innerHTML =  ou;

                var sonblock = document.createElement("div");
                div.id = dn;


                son.appendChild(span);
                son.appendChild(img);
                son.appendChild(a);
                div.appendChild(son);
                div.appendChild(sonblock);

            }
            for(var j=0;j<users.length;j++){
                var li = document.createElement("li");
                li.title = users[j]['uid'];


                var span = document.createElement("span");
                span.className = "checkbox checkbox_uncheck";

                var img = document.createElement("img");
                img.src = "images/unline.png";

                var a = document.createElement("a");
                a.innerHTML = users[j]['username'];
                //img.style.float = "left";
                li.appendChild(span);
                li.appendChild(img);
                li.appendChild(a);
                div.appendChild(li);
            }
            //if(div.style.display == "none"){
                div.style.display = "block";
            //}else{
            //    div.style.display = "none";
            //}

            $("#guanli").mCustomScrollbar("update");	//添加完成之后更新界面滚动。
        }
    },"正在获取用户信息!");
}

//***home()函数替换
function home(listen) {
    getData(listen);
    loadLogo();
    var userNumber = $.cookie('totalUsersNumber');
    if (userNumber) {
        setPage(userNumber, 1, userPerPageGlobal);   //显示第
    }
}
//+++0723 根据用户权限加载起始群组信息
function init(listen) {
    var obj = {
        _path: "/a/wp/org/ldap_get_ou_by_sid",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq1(obj, function (data) {
        var rt = data.rt;
        var rootdn = data.dn;
        //+++ 20150731 确保用户unchecked
        changeSelectedUsers("ou:"+rootdn, "del", "ou");
        var ou = rootdn.split(",")[0].split("=")[1];
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            loadingStatus("成功获取用户信息！", 0);
            var initNode = "";
            if (rootdn.split(",")[0].split("=")[0] == "dc") {
                ou = '所有用户';
            }
            initNode += '<div style="cursor:pointer" style="margin-left:20px">';
            initNode += '<span id="' + "ou:" + rootdn + '"class="checkbox checkbox_uncheck" onclick="checkForMainPage(this.id)"></span>';
            initNode += '<img src="images/group.png"/>';
            initNode += '<a href="javascript:;" title="' + rootdn + '" onclick="show(this.title)">';
            initNode += ou;
            initNode += '</a>';
            initNode += '</div>';
            initNode += '<div style="margin-left:20px;" id="' + rootdn + '">';

            $("#yic").html(initNode);
        }
    }, "正在获取用户信息!");
}


function getData(listen) {
    if (sessionStorage.allUsers == null) {
        getUserDataFromDB(listen);
    } else {
        if (listen) {
            getPageUsers(1);  //+++ 20150730 刷新页面重新加载home页面选中列表
        }
        var users = getUserDataFromCache(listen);
        $("#yic").html(users);	//添加用户数据
    }

}

function getUserDataFromDB(listen) {
    init(listen);
}

//+++20150729 将树的状态存入缓存中
//+++20150730 页面跳转前执行函数
$(window).bind('beforeunload', function () {
    //+++20160119不将数据统计界面的树存入内存中
//    if(location.href.indexOf("statistics")<=-1){
        var treeStatus = document.getElementById("ma_yic").innerHTML;
        sessionStorage.allUsers = treeStatus;
//    }
});

function getUserDataFromCache(listen) {
    var newcache;
    var cache = sessionStorage.allUsers;
    if (listen == false) {
        //如果不需要监听的话，在返回字符串之前将其中的check()函数的参数进行替换
        newcache = cache.replace(/true/g, "false");
    } else {
        newcache = cache.replace(/false/g, "true");
    }
    return newcache;
}

//***函数替换
function showsons(all, flag) {
    var html = "";
    loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['dn'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("ou:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div style="cursor:pointer">';
        html += '<span id="' + "ou:" + dn + '"class="' + checkStatus + '" onclick="checkForMainPage(this.id)"></span>';

        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="' + dn + '" onclick="show(this.title)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div style="margin-left:20px;" id="' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "us:" + users[j]['dn'] + '" class="' + checkStatus + '"  onclick="showuserdetailsForMainPage(this,this.title,this.id,' + listen + ')"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' + "us:" + users[j]['dn'] + '" title="' + users[j]['uid'] + '" href="javascript:;" onclick="showuserdetailsForMainPage(this,this.title,this.name,' + listen + ')">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}

function getSelectStatus(rootNode) {
    var status = $("#yic").innerHTML;
    alert(status);
    return status;
}

//+++ 20150723
//设置page信息，首次
function setPage(userNumber, page, userPerPage) {
    var userPerPage = userPerPage;
    var pageNumber = Math.ceil(userNumber / userPerPage);
    //for title
    var txt = "共0页，0条用户信息";
    //for page change
    if (userNumber != 0 && userNumber != null) {
        txt = "共" + pageNumber + "页，" + userNumber + "条用户信息";
    }
    $("#bottom_title").html(txt);
    $("#bottom_title").attr('value', pageNumber);
    $("#page_number").val(page);
    $("#page_number").attr('value', page);
}

//修改page信息 +++ 20150730
function modPage(page) {
    $("#page_number").val(page);
    $("#page_number").attr('value', page);
}

//获取某页用户，并展示
function getPageUsers(cur_page) {
    var sort_keys = getSortKeys();
    getSortedPageUsers(cur_page,sort_keys);
}

function getPageUsersqj(xialakuang,guanjianzi,cur_page) {
	var sort_keys = getSortKeys();
	getSortedPageUsersqj(xialakuang,guanjianzi,cur_page,sort_keys);
}

/*********************/
//首页
$("#first_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#page_number").val());
    if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }
    $("#page_number").val(1);
    //+++20150826 脚本触发页数变化
    $("#page_number").change();
});
//末页
$("#end_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#page_number").val());
    if (cur_page < 1) {
        return;
    } else if ($("#bottom_title").attr('value') == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }
    $("#page_number").val($("#bottom_title").attr('value'));
    //+++20150826 脚本触发页数变化
    $("#page_number").change();
});
//上一页
$("#pre_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#page_number").val());
	var xialakuang = document.getElementById("selecttype").value;
	var guanjianzi = document.getElementById("qjguolv").value;
	var sousuo = document.getElementById("sousuo").value;
	if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }
	//记住本页第一条的uid
	var last_user = $("#yglb tbody tr")[0].className;
	if(!!xialakuang && !!guanjianzi && sousuo=="1"){
		var obj = {
			_path: "/a/wp/org/search_all_users",
			_methods: "get",
			param: {
				sid: $.cookie("org_session_id"),
				page: cur_page-1,
//            last_user: last_user,
				size: userPerPageGlobal,      //需要加入页面用户数
				sort_keys: JSON.stringify(getSortKeys())
			}
		};
		ajaxReq(obj, function (data) {
			var users = data.users;
			var page = location.href;
			if (page.indexOf("home") > -1) {
				modPage(cur_page - 1);
				showUsersListqj(users.reverse(),xialakuang,guanjianzi);
			}
			//+++20150826 脚本触发页数变化
			$("#page_number").change();
		});
	}else{
		var obj = {
			_path: "/a/wp/org/get_page_users",
			_methods: "get",
			param: {
				sid: $.cookie("org_session_id"),
				page: cur_page-1,
//            last_user: last_user,
				size: userPerPageGlobal,      //需要加入页面用户数
				sort_keys: JSON.stringify(getSortKeys())
			}
		};
		ajaxReq(obj, function (data) {
			var users = data.users;
			var page = location.href;
			if (page.indexOf("home") > -1) {
				modPage(cur_page - 1);
				showUsersList(users.reverse());
			}
			//+++20150826 脚本触发页数变化
			$("#page_number").change();
		});
	}
});
//下一页
$("#next_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#page_number").val());
	var xialakuang = document.getElementById("selecttype").value;
	var guanjianzi = document.getElementById("qjguolv").value;
	var sousuo = document.getElementById("sousuo").value;
	if (cur_page < 1) {
        return;
    } else if ($("#bottom_title").attr('value') == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }
	//记住本页最后一条的uid
	var cur_user_number = $("#yglb tbody tr").length;
	var last_user = $("#yglb tbody tr")[cur_user_number - 1].className;
	if(!!xialakuang && !!guanjianzi && sousuo=="1"){
		var obj = {
			_path: "/a/wp/org/search_all_users",
			_methods: "get",
			param: {
				sid: $.cookie("org_session_id"),
				page: cur_page + 1,
//            last_user: last_user,
				size: userPerPageGlobal,      //需要加入页面用户数
				sort_keys: JSON.stringify(getSortKeys())
			}
		};
		ajaxReq(obj, function (data) {
			var users = data.users;
			var page = location.href;
			if (page.indexOf("home") > -1) {
				modPage(cur_page + 1);
				showUsersListqj(users,xialakuang,guanjianzi);
			}
			//+++20150826 脚本触发页数变化
			$("#page_number").change();
		});
	}else{
		var obj = {
			_path: "/a/wp/org/get_page_users",
			_methods: "get",
			param: {
				sid: $.cookie("org_session_id"),
				page: cur_page + 1,
//            last_user: last_user,
				size: userPerPageGlobal,      //需要加入页面用户数
				sort_keys: JSON.stringify(getSortKeys())
			}
		};
		ajaxReq(obj, function (data) {
			var users = data.users;
			var page = location.href;
			if (page.indexOf("home") > -1) {
				modPage(cur_page + 1);
				showUsersList(users);
			}
			//+++20150826 脚本触发页数变化
			$("#page_number").change();
		});
	}
});
//输入页数
function pageChange(cur_page) {
    changePageSelectStatus();
    var totalPages = $("#bottom_title").attr('value');
	var xialakuang = document.getElementById("selecttype").value;
	var guanjianzi = document.getElementById("qjguolv").value;
	var sousuo = document.getElementById("sousuo").value;
	if (totalPages < 1) {
        //+++20150824 如果用户不满1页，应显示成1页
        $("#page_number").val(0);
        return;
    }
    //判断当前输入页数是否合法,不合法则返回当前页
    if (isNaN(cur_page)) {
        loadingStatus("非法输入，请输入数字！");
        $("#page_number").focus();
        return;
    }
    //+++20150824 加入对于输入页数0的限制
    if (cur_page <= 0 || cur_page > totalPages) {
        loadingStatus("当前输入超出页数范围，请重新输入！");
        return;
    }
	if(!!xialakuang && !!guanjianzi && sousuo=="1"){
		getPageUsersqj(xialakuang,guanjianzi,cur_page);
	}else{
		getPageUsers(cur_page);
	}
};
//+++20150826 页数改变时修改全选当页span的状态
function changePageSelectStatus(){
    if($("#xzqb").attr("value")==1){
        $("#select_page").attr("class","checkbox checkbox_checked");
    }else{
        $("#select_page").attr("class","checkbox checkbox_uncheck");
    }
}

//+++ 20150729 左侧树列表展示函数
function showUser(key,status, username, imei, uid, title, ou, dev_id) {
    //根据数据重新加载
    var department = get_oudn_name(ou);

    //+++ 20150827 根据选择全部标志位的值确定span的选中情况
    var span_class = "checkbox checkbox_uncheck";
    if($("#xzqb").attr("value")==1){
        span_class = "checkbox checkbox_checked";
    }
    var txt;
    txt = "";
    txt += '<tr class="' + uid + '" value="'+key+'">';
    txt += '<td><span class="'+span_class+'"></span></td>';
    txt += '<td class="zhuangtai">' + status + '</td>';
    txt += '<td class="username" value="'+username+'">' + username + '</td>';
    txt += '<td class="imei" value="'+imei+'">' + imei + '</td>';
    txt += '<td class="Telephone" value="'+uid+'">' + uid + '</td>';
    txt += '<td class="title" value="'+title+'">' + title + '</td>';
    txt += '<td class="oudn" value="'+ou+'">' + department + '</td>';
    txt += '<td class="lastTime">获取中...</td>';
    txt += '<td class="dev_id">获取中...</td>';
    txt += '<td><img class="lock" alt="unlock" title="suoding" src="images/unlock.png" /></td></tr>';
    $("#yglb tbody").append(txt);
    $("#shebeiB").mCustomScrollbar("update");
    $(".zhuangtai").html('<img src="images/unonline.png" />状态获取中...');
}

function showUsersList(users) {
    //清除所有列表
    $("#yglb tbody tr").each(function (index, element) {
        $(element).remove();
    });
    $.each(users, function (index, element) {
        var user = element;
        var dev_id = "设备未激活";
        if (user['devs'].length > 0) {
            dev_id = user['devs'][0];
        }
        showUser(user['key'],user['status'], user['username'], dev_id, user['uid'], user['title'], user['oudn'], dev_id);
    });
    setTimeout(loopUpForOnce, 1000);
}

//-----------//
//***newloopup
function check(dn, listen) {
    //获取进行选择操作的checkbox,并将此群组下的所有checkbox的属性设置为选中
    //如果listen选项为真，才进行加载用户信息的操作
    var oudn = dn.substring(3);
    var span = document.getElementById(dn);
    var div = document.getElementById(oudn);  //获取群组所在的div
    var checkboxs = div.getElementsByTagName("span");
    for (var i = 0; i < checkboxs.length; i++) {
        var type = checkboxs[i].id.substring(0, 2);
        if (span.className == "checkbox checkbox_uncheck") {
            checkboxs[i].setAttribute("class", "checkbox checkbox_checked");

            //获取了由span id中加入的标识字段
            if (listen) {
                if (type == 'ou') {
                    continue;
                }
                if (type == 'us') {
                    hideinfo(checkboxs[i].title);
                    showuserinfo(checkboxs[i].title, checkboxs[i].id);
                }
            }
        } else {
            checkboxs[i].setAttribute("class", "checkbox checkbox_uncheck");
            if (listen) {
                if (type == 'us') {
                    hideinfo(checkboxs[i].title);
                }
            }

        }
    }
    if (listen) {
        setTimeout(loopUpForOnce, 2000);
    }
}

//+++ 20150724 为了不影响其他页面，主界面的事件响应函数需要改变
function checkForMainPage(dn) {
    //获取进行选择操作的checkbox,并将此群组下的所有checkbox的属性设置为选中
    //如果listen选项为真，才进行加载用户信息的操作

    var oudn = dn.substring(3);
    var span = document.getElementById(dn);
    var status = span.className;
    var changeTo = "";

    if (status == "checkbox checkbox_uncheck") {
        changeTo = "checkbox checkbox_checked";
        changeSelectedUsers(dn, "add", "ou");
    } else {
        changeTo = "checkbox checkbox_uncheck";
        changeSelectedUsers(dn, "del", "ou");
    }

    var div = document.getElementById(oudn);  //获取群组所在的div
    var checkboxs = div.getElementsByTagName("span");
    for (var i = 0; i < checkboxs.length; i++) {
        checkboxs[i].setAttribute("class", changeTo);
    }
}

// +++ 20150728 用户更改选择的节点
// 传入dn为被操作span的id
function changeSelectedUsers(dn, type, node) {
    if(location.href.indexOf("home")>-1){
        document.getElementById("selecttype").value="";
        document.getElementById("qjguolv").value="";
    }
    var id = "";
    if (node == "ou") {
        id = dn.substr(3);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            type: type,
            node: node,
            size: userPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq(obj, function (data) {
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        if (page.indexOf("home") > -1) {
            setPage(userNumber, cur_page, userPerPageGlobal);   //显示第一页
            showUsersList(users);
        }else if(page.indexOf("statistics") > -1){
            check_for_analysis(dn,node);
        }
    });
}
//+++20151026 加入只修改节点选中状态的函数，不返回第一页用户数据，节省流量
function changeSelectedNode(dn, type, node){
    var id = "";
    if (node == "ou") {
        id = dn.substr(3);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_node",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            type: type,
            node: node
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
    });
}

//+++20150729 用户节点checkbox在发生变化时做的操作
function showuserdetailsForMainPage($Element, uid, sdn, show) {
    if (($Element).tagName == "A")    //如果点击的是文字连接a
    {
        var sp = document.getElementById(sdn);   //获取id=sdn的object span
        if (sp.className == "checkbox checkbox_checked") {
            sp.setAttribute("class", "checkbox checkbox_uncheck");
            changeSelectedUsers(uid, "del", "user");
        }
        else {
            sp.setAttribute("class", "checkbox checkbox_checked");
            changeSelectedUsers(uid, "add", "user");
        }
    }
    if (($Element).tagName == "SPAN") {
        if (($Element).className == "checkbox checkbox_checked") {
            changeSelectedUsers(uid, "del", "user");
        } else {
            changeSelectedUsers(uid, "add", "user");
        }
    }
    //+++20150907 不用再手动更新，因为修改选中状态中已经调用了
//    if (show) {
//        newloopUp();
//    }

}

//***showuserdetails
function showuserdetails($Element, uid, sdn, show) {
    var jh = sdn.substr(0, 2);
    var dn = sdn.substr(3);
    var pnumber = '1000000000';
    if (($Element).tagName == "A")    //如果点击的是文字连接a
    {
        var sp = document.getElementById(sdn);   //获取id=sdn的object span
        if (sp.className == "checkbox checkbox_checked") {
            sp.setAttribute("class", "checkbox checkbox_uncheck");
            hideinfo(uid);
            return;
        }
        else {
            sp.setAttribute("class", "checkbox checkbox_checked");
        }
    }
    if (($Element).tagName == "SPAN" && ($Element).className == "checkbox checkbox_checked")   //如果点击的是span
    {
        hideinfo(uid);
        return;
    }
    if (show) {
        showinfo(uid, sdn, pnumber);
        loopUpForOnce();
    }

}

function showuserinfo(uid, sdn) {
    var jh = sdn.substr(0, 2);
    var dn = sdn.substr(3);
    var pnumber = '1000000000';
    // alert(dn);
    var sp = document.getElementById(sdn);   //获取id=dn的object span
    showinfo(uid, sdn, pnumber);
}

//***no  lookup
function showinfo(uid, sdn, pnumber) {
    //alert(sdn);
    //alert("showinfo");
    var a = document.getElementsByName(sdn)[0];
    var username = a.innerHTML;
    var job = a.className.split(':')[0];
    var email = a.className.split(':')[1];
    var department = get_oudn_name(sdn);

    var dev_id = '设备信息获取中...';
    var txt;
    txt = "";
    txt += '<tr class="' + uid + '">';
    //alert('uid:'+uid);
    txt += '<td><span class="checkbox checkbox_uncheck"></span>';
    txt += '</td><td class="zhuangtai"></td>';
    txt += '<td class="username">' + username + '</td>';
    txt += '<td class="Email">' + email + '</td><td class="Telephone">' + uid + '</td><td>' + job + '</td><td>' + department + '</td><td class="lastTime">在线时间</td>';
    txt += '<td class="dev_id">' + dev_id + '</td>';
    txt += '<td><img class="lock" alt="unlock" title="suoding" src="images/unlock.png" /></td></tr>';
    $("#yglb tbody").append(txt);
    $("#shebeiB").mCustomScrollbar("update");
    $(".zhuangtai").html('<img src="images/unonline.png" />状态获取中...');

}

function check_dev_id_and_user(Element) {
    var arr = [];
    var that;
    $("#yglb tbody tr .checkbox_checked").each(function (index, element) {
        var that = $(element).parent().parent();
        if ($(".dev_id", that).html() != 'undefined') {
            if ($(".username", that).html() != '')
                arr.push({"dev_id": $(".dev_id", that).attr("value"), "username": $(".username", that).html()});
            else
                arr.push({"dev_id": $(".dev_id", that).attr("value"), "username": "unknow"});
        }
    });
    //如果点击之前是未选中，则需要在arr中添加该项，反之则删除
    var parenttr = $(Element).parent().parent();
//    alert(Element.className);
    if (Element.tagName == "SPAN" && Element.className == "checkbox checkbox_uncheck")   //如果点击的是span
    {
//        alert($(".dev_id",parenttr).html());
        if ($(".dev_id", parenttr).html() != 'undefined') {
            if ($(".username", parenttr).html() != '')
                arr.push({"dev_id": $(".dev_id", parenttr).html(), "username": $(".username", parenttr).html()});
            else
                arr.push({"dev_id": $(".dev_id", parenttr).html(), "username": "unknow"});
        }
    }
    if (Element.tagName == "SPAN" && Element.className == "checkbox checkbox_checked") {
//        alert($(".dev_id",parenttr).html());
        for (var k = 0; k < arr.length; k++) {
            if (arr[k].dev_id == $(".dev_id", parenttr).html()) {
                arr.splice(k, 1);
                break;
            }
        }
    }
//    alert(JSON.stringify(arr));
    return arr;
}

function hideinfo(uid) {
    //解除勾选隐藏用户信息
    $("#yglb tbody tr").each(function (index, element) {
        var telephone = $(".Telephone", $(element)).html();
        if (telephone == uid) {
            $(element).remove();
        }
    });
}

//获取所有策略的作用范围和坐标 半径
function getlocs() {
    var obj = {
        _path: "/a/wp/user/get_strategys",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {

        var rt = data.rt;
        var strategys = data.strategys;
        if (rt != 0) {
            loadingStatus("策略加载失败！", 0);
        } else {
            strmarkerArr.splice(0, strmarkerArr.length);
            for (var i = 0; i < strategys.length; i++) {
                var k = i + 1
                var marker = {
                    title: "策略" + k,
                    desc: strategys[i].desc,
                    radius: strategys[i].radius,
                    start: strategys[i].start,
                    end: strategys[i].end,
                    point: {
                        lot: parseFloat(strategys[i].lon),
                        lat: parseFloat(strategys[i].lat)
                    },
                    isOpen: 1,
                    icon: {w: 25, h: 25, l: 45, t: 21, x: 6, lb: 5}
                };
                strmarkerArr.push(marker);
            }
        }
        addstrcircles();
    });

}

function loadstrategys() {
    var time0 = new Date().getTime();
    var obj = {
        _path: "/a/wp/user/get_strategys",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        var strategys = data.strategys;
        if (rt == 0) {
            loadingStatus("获取策略配置信息成功!", 0);
            for (var i = 0; i < strategys.length; i++) {
                showstrategyinfo(strategys[i], i + 1);
            }
        } else {
            loadingStatus("获取策略配置信息失败!", 0);
        }
    }, "正在获取策略配置信息...");
}

//用于展示策略内容
function showstrategycontent(element) {
    var strategy_id = element.parentNode.parentNode.className;
    var obj = {
        _path: "/a/wp/user/get_strategy_by_id",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id"),
            strategy_id: strategy_id
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        var strategy = data.strategy;
        if (rt == 0) {
            var wifi = "未设置";
            var camera = "未设置";
            var bluetooth = "未设置";
            var tape = "未设置";
            var gps = "未设置";
            var mobiledata = "未设置";
            var usb_connect = "未设置";
            var usb_debug = "未设置"
            if (strategy['wifi'] == "wfjy")
                var wifi = "非禁用";
            else if (strategy['wifi'] == "wjy")
                var wifi = "禁用";
            if (strategy['camera'] == "cfjy")
                var camera = "非禁用";
            else if (strategy['camera'] == "cjy")
                var camera = "禁用";
            if (strategy['bluetooth'] == "bfjy")
                var bluetooth = "非禁用";
            else if (strategy['bluetooth'] == "bjy")
                var bluetooth = "禁用";
            if (strategy['tape'] == "tfjy")
                var tape = "非禁用";
            else if (strategy['tape'] == "tjy")
                var tape = "禁用";
            if (strategy['gps'] == "gfjy")
                var gps = "非禁用";
            else if (strategy['gps'] == "gjy")
                var gps = "禁用";
            if (strategy['mobiledata'] == "mfjy")
                var mobiledata = "非禁用";
            else if (strategy['mobiledata'] == "mjy")
                var mobiledata = "禁用";
            if (strategy['usb_connect'] == "ucfjy")
                var usb_connect = "非禁用";
            else if (strategy['usb_connect'] == "ucjy")
                var usb_connect = "禁用";
            if (strategy['usb_debug'] == "udfjy")
                var usb_debug = "非禁用";
            else if (strategy['usb_debug'] == "udjy")
                var usb_debug = "禁用";

            var html = "";
            html = "策略如下：\n" + "camera:" + camera + ',' + "bluetooth:" + bluetooth + ',' + "wifi:" + wifi + ',' + '\n' + "录音:" + tape + ',' + "gps:" + gps + ',' + "移动数据:" + mobiledata + ',' + '\n' + "USB连接:" + usb_connect + ',' + "USB调试:" + usb_debug + '。';
            html += '\n';
            alert(html);
        } else {
            loadingStatus("获取策略内容失败!", 0);
        }
    }, "");
}

function showstrategyinfo(strategy, i) {
    var userdesc = strategy['userdesc'];
    var strategy_id = strategy['strategy_id'];
    //+++ 20150707 判断策略权限
    var isadmin = strategy['isadmin'];

    var wifi = "";
    var camera = "";
    var bluetooth = "";

    if (strategy['camera'] == "cfjy")
        var camera = "非禁用";
    else if (strategy['camera'] == "cjy")
        var camera = "禁用";
    if (strategy['bluetooth'] == "bfjy")
        var bluetooth = "非禁用";
    else if (strategy['bluetooth'] == "bjy")
        var bluetooth = "禁用";

    //策略内容
    var strategy_content = '';
    strategy_content += "camera:" + camera + "，..." + '<br/>';

    var temp = "";
    if (userdesc.length > 0) {
        //+++20150826在界面中不应显示test
        var name = userdesc[0]['name'];
        if(name.indexOf("test")>=0){
            if(name=="test"){
                name = "";
            }else{
                name = userdesc[0]['name'].substring(name.indexOf("test/")+5);
            }
        }
        temp += name + userdesc[0]['desc'] + '，...<br/>';
    }
//    for(var k=0;k<userdesc.length;k++)
//    {
//        alert(k);
//        alert(userdesc[k]['name']);
//        alert(userdesc[k]['desc']);
//        if(userdesc[k]['name']=="所有用户")
//            continue;
//        temp+=userdesc[k]['name']+userdesc[k]['desc']+'<br/>';
//    }
    var controller = "";
    if(strategy['auth']=='admin'){
        controller = "超级管理员";
    }else{
        controller = strategy['auth'].split(",")[strategy['auth'].split(",").length-1];
    }
    var txt;
    txt = "";
    txt += '<tr class="' + strategy_id + '" value=' + isadmin + '>';
    txt += '<td><span class="checkbox checkbox_uncheck"></span>';
    txt += '</td><td class="strategy_id">' + i + '</td>';
    txt += '<td>' + controller + '</td>';
    txt += '<td>' + strategy['start'] + '</td>';
    txt += '<td>' + strategy['end'] + '</td>';
    txt += '<td>' + strategy['desc'] + '</td>';
    txt += '<td><a onclick="showstrategycontent(this)" style="text-decoration: underline">' + strategy_content + '</a></td>';
    txt += '<td><a onclick="showusers(this)" style="text-decoration: underline">' + temp + '</a></td>';
    //+++20151024 如果管理员无权删除和修改，禁用快捷键
    if(isadmin==0){
        txt += '<td class="modify"><button disabled="disabled" class="' + strategy_id + '" style="padding:0;padding-left:4px;padding-right:4px;margin:4px;font: 16px/1.5em ' + "'微软雅黑'" + '" onclick="modifystrategy(this.className)">修改</button>' + '</td>';
        txt += '<td class="delete"><button disabled="disabled" class="' + strategy_id + '" style="padding:0;padding-left:4px;padding-right:4px;margin:4px;font: 16px/1.5em ' + "'微软雅黑'" + '" onclick="delstrategy(this.className)">删除</button>' + '</td>';
    }else{
        txt += '<td class="modify"><button class="' + strategy_id + '" style="padding:0;padding-left:4px;padding-right:4px;margin:4px;font: 16px/1.5em ' + "'微软雅黑'" + '" onclick="modifystrategy(this.className)">修改</button>' + '</td>';
        txt += '<td class="delete"><button class="' + strategy_id + '" style="padding:0;padding-left:4px;padding-right:4px;margin:4px;font: 16px/1.5em ' + "'微软雅黑'" + '" onclick="delstrategy(this.className)">删除</button>' + '</td>';
    }
    $("#stB tbody").append(txt);
    $(" #strategyB").mCustomScrollbar("update");
    // }else{
    //   loadingStatus("获取策略配置信息失败!",0);
    // }
}

//公共方法，每棵树都调用的控制展开闭合的方法
function show(title) {
//    alert("进入show");
//    alert("选择的oudn:"+title);
    var content = document.getElementById(title).innerHTML;
//    alert("content:"+content);
    var oudn = title;
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,title.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel",
            _methods: "get",
            param: {
                oudn: oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq(obj, function (data) {
            var rt = data.rt;
            if (rt != 0) {
                loadingStatus("获取用户信息失败！", 0);
            } else {
                loadingStatus("成功获取用户信息！", 0);
                var sons = showsons(data, true);
                document.getElementById(title).innerHTML = sons;	//添加一个账户
            }
        }, "正在获取用户信息!");
    } else {
        //控制群组的展开和闭合
        var div = document.getElementById(title);
        if (div.style.display == "none") {
            div.style.display = "block";
        }
        else {
            div.style.display = "none";
        }
    }
}

$().ready(function() {
    var obj = {
        _path: "/a/wp/org/auto_search_adm_by_sid",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var users = data.users;
        //console.log(users);

        $("#searchadm").autocomplete(users,{
            minChars: 1,
            max: 5,
            autoFill: false,
            mustMatch: false,
            matchContains: true,
            scrollHeight: 220,
            formatItem: function(data, i, total) {
                return data[0];
            },
            formatMatch: function(data, i, total) {
                return data[0];
            },
            formatResult: function(data) {
                return data[0];
            }
        });
    });
});

function search_adm() {
    clear_yglb_table();
    var t = document.getElementById('yic');
    var span = t.getElementsByTagName("span");
    for(var i=0;i<span.length;i++) {
        span[i].className = "checkbox checkbox_uncheck";
    }
    var input = document.getElementById("searchadm").value;
    if (input == '') {
        alert("请输入查询内容");
    } else if (input.TextFilter() != input) {
        alert("您输入了非法字符，请重新输入！");
    } else {
        var obj = {
            _path: "/a/wp/org/auto_selected_adm_by_sid",
            _methods: "get",
            param: {
                sid: $.cookie("org_session_id"),
                username: input
            }
        };

        ajaxReq(obj, function (data) {
            var rt = data.rt;
            var rootdn = data.dn;
			var count = data.count;
			var user_result =data.user;
			var block=0;
            //var user_oudn = data.user_oudn;
            //var user_uid = data.user_uid;
			
            if (rt != 0||count==0) {
                //loadingStatus("查询的用户不存在！", 0);
                alert("查询的用户不存在！");
            } else {
                //loadingStatus("成功获取用户信息！", 0);
		for(var m=0;m<count;m++){
			var user_oudn = user_result[m].user_oudn;
			var user_uid =user_result[m].user_id;
			var id = "us:cn=" + input + "," + user_oudn;
			var a = t.getElementsByTagName("a");
			
			for(var i=0;i<a.length;i++) {
				var t_a = a[i].title;
				if(t_a[t_a.length-1]=="m"){
					var diva = document.getElementById(t_a);
					if(user_oudn.indexOf(t_a) <= -1){
						if(block==0){
							diva.style.display = "none";
							block=1;
						}
								
					} else {

						diva.style.display = "block";
					}
					autoshow(t_a);
				}
			}
					
			autoshowuserdetailsForMainPage(user_uid, id);
			block=1;
					
						
		}
                
            }
        });
    }
}

function clear_yglb_table(){
    $("#yglb tbody").html("");
}

function autoshow(title) {
    var content = document.getElementById(title).innerHTML;
    var oudn = title;
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,title.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel",
            _methods: "get",
            param: {
                oudn: oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq1(obj, function (data) {
            var rt = data.rt;
            if (rt != 0) {
                //loadingStatus("获取用户信息失败！", 0);
            } else {
                //loadingStatus("成功获取用户信息！", 0);
                var sons = autoshowsons(data, true);
                document.getElementById(title).innerHTML = sons;	//添加一个账户
            }
        });
    }
}

function autoshowsons(all, flag) {
    var html = "";
    //loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['dn'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("ou:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div style="cursor:pointer">';
        html += '<span id="' + "ou:" + dn + '"class="' + checkStatus + '" onclick="checkForMainPage(this.id)"></span>';

        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="' + dn + '" onclick="show(this.title)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div style="margin-left:20px;" id="' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "us:" + users[j]['dn'] + '" class="' + checkStatus + '"  onclick="showuserdetailsForMainPage(this,this.title,this.id,' + listen + ')"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' + "us:" + users[j]['dn'] + '" title="' + users[j]['uid'] + '" href="javascript:;" onclick="showuserdetailsForMainPage(this,this.title,this.name,' + listen + ')">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}

function autoshowuserdetailsForMainPage(uid, sdn) {
    var sp = document.getElementById(sdn);
    sp.className = "checkbox checkbox_checked";
    changeSelectedUsers(uid, "add", "user");
}

//+++ 20150605 过滤特殊字符
String.prototype.TextFilter = function () {

//  +++20151103将过滤字符串中的中英文括号去掉，用于区分重名和管理员
    //var pattern = new RegExp (/[`~%!$@#^='"()?~！@#￥……&——‘”“'？*，,。.、<>]/);
   // +++20160908非法字符过滤，包括，全角，中文，英文。
    var pattern = new RegExp(/[`~!@#$%^&*()_+<>?:"{},.\/;'[\]！·￥……（）——：“《》？；‘。，”-]/);
    //var pattern = new RegExp("[~!@#$%^&*()_+{}|:<>?`-=[];,./']");
    var rs = "";
    for (var i = 0; i < this.length; i++) {
        rs += this.substr(i, 1).replace(pattern, '');
    }
    return rs;
}
//+++20150914 只用于更新一次在线状态的函数
function loopUpForOnce(){
    var uids = new Array();
    $("#yglb tbody tr").each(function () {
		var uid = $(".Telephone", this).parent().attr("class");
        uids.push(uid);
    });
    getDevsInfo(uids,1);
}
//***替换 loopup
function newloopUp() {
    var uids = new Array();
    $("#yglb tbody tr").each(function () {
		var uid = $(".Telephone", this).parent().attr("class");
		uids.push(uid);
    });
    //+++ 20151008 加入获取类型，1是获取一次，0是轮询
    getDevsInfo(uids,0);
    //+++ 20151008 该函数一直执行，来更新用户表中存储的设备状态
//    if ($("#yglb tbody tr").length != 0) {
        setTimeout(newloopUp, 300000);
//    }

}

//***列表统一请求状态
var _s = 1000;
var _m = _s * 60;
var _h = _m * 60;
var _d = _h * 24;
var _mon = _d * 30;
var _y = _mon * 12;

//+++20150914 改，检查现在表中的用户数，如果没有人就不发送请求，节省请求数
//+++ 20151008 加入type 字段区别一次获取和轮询获取
function getDevsInfo(uids,type) {
    if(type==0||(type==1&&uids.length!=0)){
        var org_session_id = $.cookie("org_session_id");
        var jsonuids = JSON.stringify(uids);
        var obj = {
            _path: '/a/wp/user/get_devs_info',
            _methods: 'get',
            param: {
                sid: org_session_id,
                uids: jsonuids,
                type: type
            }
        };
        ajaxReq(obj, function (data) {
            var rt = data.rt;
            var devs_info = data.devs_info;
            var trs = $("#yglb tbody tr");

            if (rt == 0) {
                function refresh(index, tr) {
                    (function (tr) {
                        var data = devs_info[index];
                        var status = data.status;
                        var lastupdate = data.last_update;
                        var online = data.onlinestates;
                        var dev = data.dev_id;
                        if (status === 2) {
                            $(".zhuangtai", tr).html('<img src="images/online.png" />在线');
                        } else {
                            $(".zhuangtai", tr).html('<img src="images/unonline.png" />离线');
                        }
                        if (dev === '') {
                            $(".dev_id", tr).html("设备未激活");
                            $(".dev_id", tr).attr('value', dev);
                        } else {
                            $(".dev_id", tr).html(online + '(天)');
                            $(".dev_id", tr).attr('value', dev);
                        }
                        if (lastupdate === '') {
                            $(".lastTime", tr).html("设备未激活");
                        } else {
                            var last_ms = parseInt(lastupdate);
                            var last_time = new Date(last_ms * 1000);
                            var new_time = new Date();
                            var qian_time = new_time - last_time;
                            var show_time = '';
                            if (qian_time / _y > 1) {
                                show_time = parseInt(qian_time / _y) + "年前"
                            } else if (qian_time / _mon > 1) {
                                show_time = parseInt(qian_time / _mon) + "月前"
                            } else if (qian_time / _d > 1) {
                                show_time = parseInt(qian_time / _d) + "天前"
                            } else if (qian_time / _h > 1) {
                                show_time = parseInt(qian_time / _h) + "小时前"
                            } else if (qian_time / _m > 1) {
                                show_time = parseInt(qian_time / _m) + "分前"
                            } else if (qian_time / _s > 1) {
                                show_time = parseInt(qian_time / _s) + "秒前"
                            } else {
                                show_time = "1秒前";
                            }
                            $(".lastTime", tr).html(show_time);
                        }
                    })(tr);
                }

                trs.each(function (index, element) {
                    refresh(index, $(element));			//获取手机的在线状态（传递tr参数）
                });
                loadingStatus('更新成功!', 0);
            }
            else {
                loadingStatus('更新失败!', 0);
            }

        },"正在更新用户设备状态");
    }
    else{
        return;
    }
}

function setText(select, text) {
    select.html(text);
}

//验证一个值是否为空
function verViod(val) {
    if (!val.replace(/\s/g, "")) {		//如果值为空，则返回false；
        return false;
    } else {		//如果值为非空，则返回true。
        return true;
    }
}

//抽象ajax请求函数
function ajaxReq(obj, func, str) { //obj是要发送的数据  url是nodejs接受请求的路径 time是请求允许的时间
    $.ajax({
        async: true,
        timeout: 60000,
        type: "POST",
        url: "/f_login",
        data: obj,
        dataType: 'json',
        beforeSend: function (jqXHR) {
            if (!!str) {
                loadingStatus(str, 1);
            }
        },
        success: function (data) {
            var rt = data.rt;
            switch (rt) {
                case 4:
                case 6:
                case 8:
                    $.cookie("org_session_id", null);
                    $.cookie("configStatus", null);
                    location.href = "/";
                    break;
                default:
                    func(data);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            //console.log('解析对像:' + JSON.stringify(jqXHR));
            switch (textStatus) {
                case "timeout":
                    //alert("请求超时!", obj._path);
                    loadingStatus("请求超时!", 0);
                    break;
                case "error":
                case null:
                    loadingStatus("发生错误，请重试!", 0);
                    break;
                case "notmodified":
                    //alert("notmodified.", obj._path);
                    loadingStatus("notmodified!", 0);
                    break;
                case "parsererror":
                    //console.log("parsererror.", obj._path);
                    loadingStatus("parsererror!", 0);
                    break;
                default:
                    //alert("未知错误。", obj._path);
                    loadingStatus("未知错误!", 0);
            }
        }
    });
}

function ajaxReq1(obj, func, str) { //obj是要发送的数据  url是nodejs接受请求的路径 time是请求允许的时间
    $.ajax({
        async: false,
        timeout: 60000,
        type: "POST",
        url: "/f_login",
        data: obj,
        cache: true,
        dataType: 'json',
        beforeSend: function (jqXHR) {
            if (!!str) {
                loadingStatus(str, 1);
            }
        },
        success: function (data) {
            var rt = data.rt;
            switch (rt) {
                case 4:
                case 6:
                case 8:
                    $.cookie("org_session_id", null);
                    $.cookie("configStatus", null);
                    location.href = "/";
                    break;
                default:
                    func(data);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            //console.log('解析对像:' + JSON.stringify(jqXHR));
            switch (textStatus) {
                case "timeout":
                    //alert("请求超时!", obj._path);
                    loadingStatus("请求超时!", 0);
                    break;
                case "error":
                case null:
                    loadingStatus("发生错误，请重试!", 0);
                    break;
                case "notmodified":
                    //alert("notmodified.", obj._path);
                    loadingStatus("notmodified!", 0);
                    break;
                case "parsererror":
                    //console.log("parsererror.", obj._path);
                    loadingStatus("parsererror!", 0);
                    break;
                default:
                    //alert("未知错误。", obj._path);
                    loadingStatus("未知错误!", 0);
            }
        }
    });
}

function pf(sid, dev_id, func) {
    var obj = {
        _path: '/a/wp/user/get_online_status',
        _methods: 'get',
        param: {
            sid: sid,
            dev_id: dev_id
        }
    }
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        var status = data.status;
        if (rt === 0 && status === 2) {
            func();
        } else {
            //loadingStatus('用户不在线,不能执行操作!', 0);

            return;
        }
    })
}

var status = '<div id="tanceng"><div id="loadingStatus" style="display:none;font-size:24px"></div></div>';
$(document.body).append(status);
var idArr = null;

function loadingStatus(state, sh) {
    var errTishi = $("#loadingStatus");
    if (idArr != null) {
        clearTimeout(idArr);
        idArr = null;
    }
    errTishi.html(state).fadeIn('fast');
    if (!sh) {
        idArr = setTimeout(hideLoad, 2000);
    }
}

//排序
function sortable(index, aid) {
    setFlagsAndTitle(aid);
    var sortKeys = getSortKeys();
    //每次排序默认回到第一页？
    var users = getSortedPageUsers(1,sortKeys);
}

//+++20150922 联系人界面的联系人仍采用页面内排序
function pagesort(index,aid){
        var table = document.getElementById('yglb');
    var tbody = table.tBodies[0];
    var colRows = tbody.rows;
    var aTrs = new Array;
    //alert(colRows.length);
    if (colRows.length == 0) {
        return;
    }
    else {
        for (var i = 0; i < colRows.length; i++) {
            if (colRows[i].style.display != 'none') {
                aTrs.push(colRows[i]);
            }
        }

        //现在已经获取到所有的tbody中的数据，要做的就是根据相应的行进行排序
        var aa = document.getElementById(aid);//获取到a标签
        if (index == 5) {
            //alert(getTitleCode(aTrs[0].cells[index].innerHTML));

            if (aa.className == '0') {
                aa.className = '1';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (getTitleCode(aTrs[j].cells[index].innerHTML) > getTitleCode(aTrs[j + 1].cells[index].innerHTML)) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else {
                aa.className = '0';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (getTitleCode(aTrs[j].cells[index].innerHTML) <= getTitleCode(aTrs[j + 1].cells[index].innerHTML)) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                    }
                    i--;
                }

            }

        }


        else if (index == 6) {
            if (aa.className == '0') {
                aa.className = '1';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (getDeCode(aTrs[j].cells[index].innerHTML) > getDeCode(aTrs[j + 1].cells[index].innerHTML)) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                        if (getDeCode(aTrs[j].cells[index].innerHTML) == getDeCode(aTrs[j + 1].cells[index].innerHTML)) {
                            if (getTitleCode(aTrs[j].cells[index - 1].innerHTML) >= getTitleCode(aTrs[j + 1].cells[index - 1].innerHTML)) {
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                                aTrs[j + 1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }
            }
            else {
                aa.className = '0';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (getDeCode(aTrs[j].cells[index].innerHTML) < getDeCode(aTrs[j + 1].cells[index].innerHTML)) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                        if (getDeCode(aTrs[j].cells[index].innerHTML) == getDeCode(aTrs[j + 1].cells[index].innerHTML)) {
                            if (getTitleCode(aTrs[j].cells[index - 1].innerHTML) < getTitleCode(aTrs[j + 1].cells[index - 1].innerHTML)) {
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                                aTrs[j + 1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }

            }
        }


        else {
            //alert(aa.className);
            if (aa.className == '0') {
                aa.className = '1';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j + 1].cells[index].innerHTML) > 0) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else if (aa.className == '1') {
                aa.className = '0';
                var i = aTrs.length - 1;
                while (i) {
                    for (var j = 0; j < i; j++) {
                        if (aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j + 1].cells[index].innerHTML) <= 0) {
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j + 1].innerHTML;
                            aTrs[j + 1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
        }
    }
}

//+++20150831 设置标志位
function setFlagsAndTitle(aid){
    $("#ygt tr th[id]").each(function(index,element){
        //不是需要排序的表头全部置0
        if($(element).attr("id")!=aid&&$(element).attr("id")!="thactive"){
            $(element).attr("class",0);
        }
        switch($(element).attr("id")){
            case aid:
                break;
            case "thstatus":
                $(element).attr("title","点击按状态排序");
                break;
            case "thname":
                $(element).attr("title","点击按姓名排序");
                break;
            case "thimei":
                $(element).attr("title","点击按设备号排序");
                break;
            case "thtelephone":
                $(element).attr("title","点击按电话号码排序");
                break;
            case "thjob":
                $(element).attr("title","点击按职位/职称排序");
                break;
            case "thdepartment":
                $(element).attr("title","点击按部门排序");
                break;
            case "thupdatetime":
                $(element).attr("title","点击按最后在线时间排序");
                break;
            case "thdevice":
                $(element).attr("title","点击按活跃度排序");
                break;
            default :
                $(element).attr("title","点击按表头排序")
        }
    });
    var th = document.getElementById(aid);
    if(th.className==0||th.className==-1){
        th.className=1;
        th.title = "升序排列";
    }else if(th.className==1){
        th.className=-1;
        th.title = "降序排列";
    }
}

//+++20150831 获取排序的键,这个可扩展为多字段排序
function getSortKeys(){
    var status = $("#thstatus").attr("class");
    var username = $("#thname").attr("class");
    var imei = $("#thimei").attr("class");
    var uid = $("#thtelephone").attr("class");
    var job = $("#thjob").attr("class");
    var department = $("#thdepartment").attr("class");
    var updatetime = $("#thupdatetime").attr("class");
    var liveness = $("#thdevice").attr("class");

    var sort_keys = [];

    if(status!=0)sort_keys.push({"name":"status","order":status});
    if(username!=0)sort_keys.push({"name":"username","order":username});
    if(imei!=0)sort_keys.push({"name":"imei","order":imei});
    if(uid!=0)sort_keys.push({"name":"uid","order":uid});
    if(job!=0)sort_keys.push({"name":"title","order":job});
    if(department!=0)sort_keys.push({"name":"oudn","order":department});
    if(updatetime!=0)sort_keys.push({"name":"last_update","order":updatetime});
    if(liveness!=0)sort_keys.push({"name":"liveness","order":liveness});//这个是活跃度

    return sort_keys;
}
//+++20150831 整体排序
function getSortedPageUsers(page,sort_keys){
    //需要传入排序的依据和顺序
    var sid = $.cookie("org_session_id");
    var obj = {
        _path:"/a/wp/org/get_page_users",
        _methods:"get",
        param:{
            sid:sid,
            page:page,
            size:userPerPageGlobal,
            sort_keys:JSON.stringify(sort_keys)
        }
    };
    ajaxReq(obj,function(data){
        var rt= data.rt;
        if(rt==0){
            var users = data.users;
            if (users.length <= 0) {
                page = 0;
            }
            var place = location.href;
            if (place.indexOf("home") > -1) {
                modPage(Number(page));
                showUsersList(users);
            }
        }else{
            alert("排序失败");
        }

    });
}

function getSortedPageUsersqj(xialakuang,guanjianzi,page,sort_keys){
	//需要传入排序的依据和顺序
	var sid = $.cookie("org_session_id");
	var obj = {
		_path:"/a/wp/org/search_all_users",
		_methods:"get",
		param:{
			sid:sid,
			xialakuang: xialakuang,
			guanjianzi: guanjianzi,
			page:page,
			size:userPerPageGlobal,
			sort_keys:JSON.stringify(sort_keys)
		}
	};
	ajaxReq(obj,function(data){
		var rt= data.rt;
		if(rt==0){
			var users = data.users;
			if (users.length <= 0) {
				page = 0;
			}
			var place = location.href;
			if (place.indexOf("home") > -1) {
				modPage(Number(page));
				showUsersListqj(users,xialakuang,guanjianzi);
			}
		}else{
			alert("排序失败");
		}

	});
}

function hideLoad() {
    $("#loadingStatus").fadeOut('fast');
}

//判断是否有权限在当前页面(后来加的)
function judgeyemianqx() {
    var sid = $.cookie("org_session_id");
    var obj = {
        _path: "/a/wp/org/org_info",
        _methods: "get",
        param: {
            sid: sid
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
//        var uid=$.cookie("userid");
//        var loginType=$.cookie("loginType");
        if (rt == 0) {
            //判断是否是当前用户该在的页面
        } else {
            location.href = "/";
        }
    }, "正在获取管理员信息!");
}

/*修改用户信息 20150326*/
function mloadselect() {
    var qxoudn = $("#yic div")[0].childNodes[2].title;
    mod_user_info_ous = new RightList("modbm",[qxoudn]);
}

function loadous(sid, oudn) {
    var obj = {
        _path: "/a/wp/org/ldap_onelevel",
        _methods: "get",
        param: {
            sid: sid,
            oudn: oudn
        }
    };
    var txt = "";
    ajaxReq1(obj, function (data) {
        var ous = data.ous;
        if (data.rt == 0) {
            for (var i = 0; i < ous.length; i++) {
                txt += "<option value='" + ous[i].ou + "'>" + ous[i].ou + "</option>";
            }
        } else {
        }
    }, "");
    return txt;
}

function loadnextous(element) {
    var span = document.getElementById('modbm');
    var seletes = span.children;
    var classname = element.className;
    for (var i = seletes.length - 1; i > 0; i--) {
        if (seletes[i].className.indexOf(classname) > 0) {
            span.removeChild(seletes[i]);
        }
    }
    if (element.value == "请选择") {
        return;
    }
    var oudn = "ou=" + element.value + "," + element.className;
    var txt = "";
    var obj = {
        _path: "/a/wp/org/ldap_onelevel",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id"),
            oudn: oudn
        }
    };
    ajaxReq(obj, function (data) {
        var ous = data.ous;
        if (ous.length > 0) {
            var st = "<select onchange='loadnextous(this)'class='" + oudn + "' id='st" + oudn + "'></select>";
            $("#modbm").append(st);
            if (data.rt == 0) {
                document.getElementById("st" + oudn).options.add(new Option("请选择", "请选择"));
                for (var i = 0; i < ous.length; i++) {
                    document.getElementById("st" + oudn).options.add(new Option(ous[i].ou, ous[i].ou));
                }
            }
        }
        else {
            var span = document.getElementById('modbm');
        }
    }, "");
}

$("#muserinfo").submit(function (event) {
    event.preventDefault();
    var username = $("#mname").val();
//    var email = $("#memail").val();
    var phone = $("#mphone").val();
    var imei = $("#mimei").val();
    var zhiW = $("#mzhiw").val();
    var zhiC = $("#mzhic").val();
    var mobile = 'Y';
    //姓名监测
    if (!verViod(username)) {
        loadingStatus("用户名不能为空!");
        return false;
    } else if (username.TextFilter() != username) {
        alert("用户名不得含有特殊字符！");
        return false;
    }
    //邮箱监测
//    if (!verViod(email)) {
//        loadingStatus("邮箱不能为空!");
//        return false;
//    }
    //if(email!=""){
    //    if (!checkemail(email)) {
    //        loadingStatus("邮箱格式不对!");
    //        return false;
    //    }
    //}
    //号码检测
    var check_phone_result = checkphone(phone);

    //设备号检测
    var check_dev_result = checkdev(imei);
    console.log(check_phone_result);
    console.log(check_dev_result);
    //群组检测
    var ou = mod_user_info_ous.oudn();
    if(ou==""){
        loadingStatus("群组信息不能为空!");
        return false;
    }
    var key = $("#cur_usr").attr("value");
    //姓名检测，原则时每一个原子群组中不能出现同名的用户
    var is_has_username = check_username(key,username,ou);
    if(is_has_username){
        loadingStatus("目标群组存在重名用户，请修改用户名!", 0);
        return;
    }

    //处理号码和设备的检测结果
    if(check_phone_result==0&&check_dev_result==0){
        //构造职位/职称
        var title = generateTitle(zhiW,zhiC);
        //判定所属部门
        //获得待修改用户(根据括号格式)
        var pnumber = this.className;
        if (!pnumber.length) {
            loadingStatus("请激活待修改信息的用户!", 0);
            return false;
        }
        var key = $("#cur_usr").attr("value");
        var obj = {
            _path: "/a/wp/org/ldap_mod_user",
            _methods: "post",
            param: {
                sid: $.cookie("org_session_id"),
                key:key,
                username: username,
                email: "",
                mobile: mobile,
                pnumber: phone,//获取当前锁定的用户
                dev_id:imei,
                title: title,
                dn: ou
            }
        };
        ajaxReq(obj, function (data) {
            if (data.rt == 0) {
                sessionStorage.clear();   //******************************//
                loadingStatus("用户修改成功!", 0);
                alert("用户修改成功！");
                reloadTree();
                resetModUserLog();
//          window.location.reload();
            }else {
                loadingStatus("用户修改失败!", 0);
                alert("用户修改失败！");
            }
        }, "正在提交...");
    }
});
//+++20150902 加入重新加载用户树的逻辑，在用户删除和修改用户信息的时候要用
function reloadTree(){
    $("#yic").html("");
    home(true);
    getlocs();
    //+++20150831 加入每个页面用户数量的说明
    $("#users_perpage").html("（每页"+userPerPageGlobal+"条）");
//    setTimeout(function(){mloadselect();},3000);
}
//+++20151014 用户信息修改成功后，将输入框中信息置空
function resetModUserLog(){
    $("#muserinfo input").each(function(index,element){
        element.value="";
    });
    $("#cur_usr").html("");
    if(mod_user_info_ous){
        mod_user_info_ous.reset();
    }
}
//获取勾选设备pnumber(uid)
function check_uid() {
    var arr = [];
    var that;
    $("#yglb tbody tr .checkbox_checked").each(function (index, element) {
        var that = $(element).parent().parent();
        if (($(".Telephone", that).html() != 'undefined')) {
            arr.push($(".Telephone", that).html());
        }
    });
    return arr;
}
//+++20151020 根据权限字符串获取dn
function get_admin_oudn(qx){
    var oudn = "";
    if(qx=="admin"||qx=="所有用户"){
        oudn = ldap_base_dn;
    }else if(qx.indexOf(",")>=0){
        var ou_names = qx.split(",");
        for(var i=ou_names.length-1;i>=0;i--){
            oudn+= "ou="+ou_names[i]+",";
        }
        oudn+= ldap_base_dn;
    }else{
        oudn = "ou="+qx+","+ldap_base_dn;
    }
    return oudn;
}

//邮箱规则判断
function checkemail(email) {
    var rg = new RegExp('^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])');
    if (!rg.test(email))
        return false;
    return true;
}
//电话号码规则判断
function checkphone(phone){
    var result = 0;
    var former_phone = $("#cur_usr").attr("class");
    if(phone.trim()==""){
        alert("电话号码不能为空");
        result = 1;
    }else if(phone.toString()==former_phone.toString()){
        result = 0;
    }else{
        var rg = /^(13[0-9]|14[0-9]|15[0-9]|17[0-9]|18[0-9])\d{8}$/;
        if(!rg.test(phone)){
            alert("号码格式不正确,请修改后再提交");
            result = 1;
        }else{
            var target_user = get_user_by_uid(phone);
            if(target_user){
                var oudn = target_user['oudn'];
                var admin_qx = get_admin_right($.cookie("org_session_id"));
                var target_user_name = target_user['username'];
                if(oudn.indexOf(admin_qx)>=0){
                    //号码在管理员管理范围内

                    var confirm_change = confirm("号码已被"+target_user_name+"占用，您有权修改，是否强制互换？");
                    if(confirm_change){
                        result = 0;
                    }else{
                        result = 1;
                    }

                }else{
                    alert("号码已被"+target_user_name+"占用，您无权修改，请更换目标号码或者联系更高权限管理员修改。");
                    result = 1;//号码不在管理员的管控范围内
                }
            }

        }
    }
    return result;
}

//设备号合法性检测
function checkdev(dev_id){
    var result = 0;
    var former_dev_id = document.getElementById("mimei").getAttribute("former"); //原来的dev_id值
    if(dev_id.toString()!=former_dev_id){
        if(dev_id.trim()==""){
            if(confirm("设备号将被置空，您确定？")){
                result = 0;
            }else{
                result = 1;
            }
        }else{
            var dev = get_dev_by_id(dev_id);
            if(dev){
                //如果已存在该设备
                var cur_user = dev['cur_user'];
                if(cur_user!=""){
                    //如果设备被占用
                    var cur_user_info = get_user_by_uid(cur_user);
                    var oudn = cur_user_info['oudn'];    //用户所在的群组
                    var admin_qx = get_admin_right($.cookie("org_session_id"));
                    if(oudn.indexOf(admin_qx)>=0){
                        //目标设备号在管控范围内
                        var confirm_change = confirm("该设备已被"+cur_user_info['username']+
                            ":"+cur_user_info['uid']+"占用，您有权修改，是否强制互换设备？");
                        if(!confirm_change){
                            $("mimei").val(former_dev_id);
                            result = 1;
                        }
                    }else{
                        //目标设备号不在管控范围内
                        alert("该设备已被"+cur_user_info['username']+
                            ":"+cur_user_info['uid']+"占用，您无权更改，请联系更高级别的管理员");
                        result = 1;
                    }
                }else{
                    //设备未被占用
                    //需要提示一个可以更改的信息

                }
            }else{
                //考虑后台是否添加设备，应该不用
            }
        }
    }
    return result;
}

//检测修改后的用户姓名的合法性
function check_username(key,username,ou){
    var result = false;
    //需要拿用户的key去查询原来的用户名和姓名和现在的关系，获得结果
    if(key==""){
        result = false;
    }else{
        var obj = {
            _path: "/a/wp/org/check_username",
            _methods: "get",
            param: {
                sid: $.cookie("org_session_id"),
                key:key,
                username: username,
                oudn: ou
            }
        };
        ajaxReq1(obj, function (data) {
            if(data.rt == 0) {
                //可以进行修改
                result = false;
            }else {
                result = true;
            }
        });
        return result;
    }
}

//+++20160220 弹出对话框
function show_dialog(id,text){
    var p = document.createElement("P");
    p.innerHTML = text;
    $("div[id='"+id+"']").append(p);
    $("div[id='"+id+"']").dialog({
        resizable: false,
        bgiframe: true,
        height: 240,
        width: 400,
        modal: true,
        buttons: {
            "确定": function () {
                $(this).dialog("close");
            },
            "取消": function () {
                $(this).dialog("close");
            }}
    });
}
/***********end 修改用户信息*************/

//+++ 20150720 SHA1加密算法
// MD5 SHA1 共用
function add(x, y) {
    return ((x & 0x7FFFFFFF) + (y & 0x7FFFFFFF)) ^ (x & 0x80000000) ^ (y & 0x80000000);
}

// SHA1
function SHA1hex(num) {
    var sHEXChars = "0123456789abcdef";
    var str = "";
    for (var j = 7; j >= 0; j--)
        str += sHEXChars.charAt((num >> (j * 4)) & 0x0F);
    return str;
}

function AlignSHA1(sIn) {
    var nblk = ((sIn.length + 8) >> 6) + 1, blks = new Array(nblk * 16);
    for (var i = 0; i < nblk * 16; i++)blks[i] = 0;
    for (i = 0; i < sIn.length; i++)
        blks[i >> 2] |= sIn.charCodeAt(i) << (24 - (i & 3) * 8);
    blks[i >> 2] |= 0x80 << (24 - (i & 3) * 8);
    blks[nblk * 16 - 1] = sIn.length * 8;
    return blks;
}

function rol(num, cnt) {
    return (num << cnt) | (num >>> (32 - cnt));
}

function ft(t, b, c, d) {
    if (t < 20)return (b & c) | ((~b) & d);
    if (t < 40)return b ^ c ^ d;
    if (t < 60)return (b & c) | (b & d) | (c & d);
    return b ^ c ^ d;
}

function kt(t) {
    return (t < 20) ? 1518500249 : (t < 40) ? 1859775393 :
        (t < 60) ? -1894007588 : -899497514;
}

function SHA1(sIn) {
    var x = AlignSHA1(sIn);
    var w = new Array(80);
    var a = 1732584193;
    var b = -271733879;
    var c = -1732584194;
    var d = 271733878;
    var e = -1009589776;
    for (var i = 0; i < x.length; i += 16) {
        var olda = a;
        var oldb = b;
        var oldc = c;
        var oldd = d;
        var olde = e;
        for (var j = 0; j < 80; j++) {
            if (j < 16)w[j] = x[i + j];
            else w[j] = rol(w[j - 3] ^ w[j - 8] ^ w[j - 14] ^ w[j - 16], 1);
            t = add(add(rol(a, 5), ft(j, b, c, d)), add(add(e, w[j]), kt(j)));
            e = d;
            d = c;
            c = rol(b, 30);
            b = a;
            a = t;
        }
        a = add(a, olda);
        b = add(b, oldb);
        c = add(c, oldc);
        d = add(d, oldd);
        e = add(e, olde);
    }
    SHA1Value = SHA1hex(a) + SHA1hex(b) + SHA1hex(c) + SHA1hex(d) + SHA1hex(e);
    return SHA1Value.toUpperCase();
}

function showUserqj(key,status, username, imei, uid, title, ou, dev_id, xialakuang, guanjianzi) {
	//根据数据重新加载
    //alert("showuserqj");
	var department = '';
	var fenjie = ou.split(',');
	for (var i = fenjie.length - 1; i >= 0; i--) {
		if (fenjie[i].substring(0, 2) == 'ou') {
			department += fenjie[i].substring(3) + '/';
		}
	}
	department = department.slice(0, -1);
	//+++ 20150827 根据选择全部标志位的值确定span的选中情况
	var span_class = "checkbox checkbox_uncheck";
	if($("#xzqb").attr("value")==1){
		span_class = "checkbox checkbox_checked";
	}
	var usernameqj = username;
	var imeiqj = imei;
	var uidqj = uid;
	var titleqj = title;
	var departmentqj = department;
	var reg=new RegExp(guanjianzi,"g");
	if(xialakuang == "username" && username.indexOf(guanjianzi) > -1){
		//var username = username.replace(reg,"<font color=Yellow>"+guanjianzi+"</font>");改变字体颜色
		//var username = username.replace(reg,"<b style='color:Yellow;'>"+guanjianzi+"</b>");同上
		usernameqj = username.replace(reg,"<b style='background:Yellow;'>"+guanjianzi+"</b>");
	}else if(xialakuang == "devs" && imei.indexOf(guanjianzi) > -1){
		imeiqj = imei.replace(reg,"<b style='background:Yellow;'>"+guanjianzi+"</b>");
	}else if(xialakuang == "uid" && uid.indexOf(guanjianzi) > -1){
		uidqj = uid.replace(reg,"<b style='background:Yellow;'>"+guanjianzi+"</b>");
	}else if(xialakuang == "title" && title.indexOf(guanjianzi) > -1){
		titleqj = title.replace(reg,"<b style='background:Yellow;'>"+guanjianzi+"</b>");
	}else if(xialakuang == "oudn" && department.indexOf(guanjianzi) > -1){
		departmentqj = department.replace(reg,"<b style='background:Yellow;'>"+guanjianzi+"</b>");
	}

	var txt;
	txt = "";
	txt += '<tr class="' + uid + '" value="'+key+'">';
	txt += '<td><span class="'+span_class+'"></span></td>';
	txt += '<td class="zhuangtai">' + status + '</td>';
	txt += '<td class="username" value="'+username+'">' + usernameqj + '</td>';
	txt += '<td class="imei" value="'+imei+'">' + imeiqj + '</td>';
	txt += '<td class="Telephone" value="'+uid+'">' + uidqj + '</td>';
	txt += '<td class="title" value="'+title+'">' + titleqj + '</td>';
	txt += '<td class="oudn" value="'+ou+'">' + departmentqj + '</td>';
	txt += '<td class="lastTime">获取中...</td>';
	txt += '<td class="dev_id">获取中...</td>';
	txt += '<td><img class="lock" alt="unlock" title="suoding" src="images/unlock.png" /></td></tr>';
	$("#yglb tbody").append(txt);
	$("#shebeiB").mCustomScrollbar("update");
	$(".zhuangtai").html('<img src="images/unonline.png" />状态获取中...');
}

function showUsersListqj(users,xialakuang,guanjianzi) {
	//清除所有列表
	$("#yglb tbody tr").each(function (index, element) {
		$(element).remove();
	});
	$.each(users, function (index, element) {
		var user = element;
		var dev_id = "设备未激活";
		if (user['devs'].length > 0) {
			dev_id = user['devs'][0];
		}
		showUserqj(user['key'],user['status'], user['username'], dev_id, user['uid'], user['title'], user['oudn'], dev_id, xialakuang, guanjianzi);
	});
	setTimeout(loopUpForOnce, 1000);
}

/***********end sha1*************/

/*master*/
//管理员页面初始化
function masterinit(){
    var loginType=$.cookie("loginType");
    var uid=$.cookie("userid");
    var master_right="";
    if (loginType=="master"){
        if (uid=="master"){
            master_right="高级管理员";
        }
        else{
            master_right="普通管理员";
        }
    }
    setText($("#masterqx"),master_right);
    setText($("#masterName"),uid);
}
//masterlist初始化
function masterhome(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/master_tree",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            showlist(all);
            loadingStatus("成功获取用户信息！", 0);
            $("#ma_yic").append(html);	//添加一个账户
            $("#ma_guanli").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    var count=1;
    function showlist(all){
        html='<h1>中国科学院信息工程研究所</h1>'
        count+=1;
        temp = count;
        loadingStatus("正在获取用户信息!",0);

        var users=all;   //所有master

        //每一个群组要进行的操作
        html+='<div id=masterdiv>';
        html+='<span id=master></span>';
        html+='<img src="images/group.png"/>';
        html+='<span>';
        html+= "管理员列表";
        html+='</span>';
        html+='</div>';

        for(var j=0;j<users.length;j++){
            html+='<li title="'+users[j]['uid']+'">';
            html+='<span title="'+users[j]['uid']+'" id="'+users[j]['uid']+'" class="checkbox checkbox_uncheck" onclick="showmaster(this.title)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html+='<img src="images/unline.png"/>';
            html+='<a class="'+users[j]['phonenumber']+":"+users[j]['email']+'"name="'+users[j]['qx']+'" title="'+users[j]['uid']+'" style="cursor:pointer">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html+=users[j]['uid'];
            html+='</a>';
            html+='</li>';
        }
        html+='</div>';
        count=temp;
    }
}
//master信息展示
function showmaster(uid){
    span=document.getElementById(uid);
    //是否选中
    if(span.className=="checkbox checkbox_uncheck"){
        /*if(($Element).tagName=="SPAN"){
         changeclass(uid);
         }*/
        var obj={
            _path:"/a/wp/org/master_tree",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            var all = data.all;
            if (rt != 0) {
                loadingStatus("获取信息失败！", 0);
            } else {
                //勾选显示管理员信息
                for(var j=0;j<all.length;j++){
                    if(uid==all[j]['uid']){
                        if(all[j]['qx']=='ptgly'){
                            var qx='普通管理员';
                        }else if(all[j]['qx']=='gjgly'){
                            var qx='高级管理员';
                        }
                        var xuhao=j+1;
                        var txt;
                        txt="";
                        txt+='<tr class="'+uid+'">';
                        txt+='<td><span class="checkbox checkbox_uncheck"></span>';
                        txt+='</td><td id="'+xuhao+'">'+xuhao+'</td>';
                        txt+='<td class="username">'+uid+'</td>';
                        txt+='<td class="Email">'+all[j]['email']+'</td><td class="Telephone">'+all[j]['phonenumber']+'</td><td>'+qx+'</td></tr>';
                        $("#ma_yglb tbody").append(txt);
                        $("#ma_shebeiB").mCustomScrollbar("update");
                        loadingStatus("获取用户信息成功！",0);
                        //updateStatus("#ma_yglb tbody tr:last-child");
                    }
                }
            }
        },"正在获取用户信息!");
    }else{
        //解除勾选隐藏用户信息
        $("#ma_yglb tbody tr").each(function(index,element){
            var username =$(".username",$(element)).html();
            if(username==uid){
                $(element).remove();
            }
        });
    }
}
//master-adminlist展示
function adminhome(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/admin_tree",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            showadminlist(all);
            loadingStatus("成功获取用户信息！", 0);
            $("#ad_yic").append(html);	//添加一个账户
            $("#ad_guanli").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    var count=1;
    function showadminlist(all){
        html='<h1>中国科学院信息工程研究所</h1>'
        count+=1;
        temp = count;
        loadingStatus("正在获取用户信息!",0);

        var users=all;   //所有master

        //每一个群组要进行的操作
        html+='<div id=admindiv>';
        html+='<span id=admin></span>';
        html+='<img src="images/group.png"/>';
        html+='<span>';
        html+= "操作员列表";
        html+='</span>';
        html+='</div>';

        for(var j=0;j<users.length;j++){
            html+='<li title="'+users[j]['uid']+'">';
            html+='<span title="'+users[j]['uid']+'" id="'+users[j]['uid']+'" class="checkbox checkbox_uncheck" onclick="showadmin(this.title)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html+='<img src="images/unline.png"/>';
            html+='<a class="'+users[j]['phonenumber']+":"+users[j]['email']+'"name="'+users[j]['qx']+'" title="'+users[j]['uid']+'" style="cursor:pointer">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html+=users[j]['uid'];
            html+='</a>';
            html+='</li>';
        }
        html+='</div>';
        count=temp;
    }
}
//admin信息展示
function showadmin(uid){
    span=document.getElementById(uid);
    //是否选中
    if(span.className=="checkbox checkbox_uncheck"){
        /*if(($Element).tagName=="SPAN"){
         changeclass(uid);
         }*/
        var obj={
            _path:"/a/wp/org/admin_tree",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            var all = data.all;
            if (rt != 0) {
                loadingStatus("获取信息失败！", 0);
            } else {
                //勾选显示管理员信息
                for(var j=0;j<all.length;j++){
                    if(uid==all[j]['uid']){
                        var xuhao=j+1;
                        var txt;
                        txt="";
                        txt+='<tr class="'+uid+'">';
                        txt+='<td><span class="checkbox checkbox_uncheck"></span>';
                        txt+='</td><td id="'+xuhao+'">'+xuhao+'</td>';
                        txt+='<td class="username">'+uid+'</td>';
                        txt+='<td class="Email">'+all[j]['email']+'</td>' +
                            '<td class="Telephone">'+all[j]['phonenumber']+'</td>' +
                            '<td class="ou" oudn="'+all[j]['ou']+'">'+get_oudn_name(all[j]['ou'])+'</td>' +
                            '<td class="contact_ous" contact_ous="'+all[j]['contact_ous'].join("|")+'"><a onclick="show_contact_ous_info(this);" style="text-decoration:underline;cursor: pointer">点击查看</a></td>'+
                            '<td><button onclick="change_admin(this);">修改</button></td>'+
                            '</tr>';
                        $("#ad_yglb tbody").append(txt);
                        $("#ad_shebeiB").mCustomScrollbar("update");
                        loadingStatus("获取用户信息成功！",0);
                    }
                }
            }
        },"正在获取用户信息!");
    }else{
        //解除勾选隐藏用户信息
        $("#ad_yglb tbody tr").each(function(index,element){
            var username =$(".username",$(element)).html();
            if(username==uid){
                $(element).remove();
            }
        });
    }
}

function show_contact_ous_info(element){
    var td = element.parentNode;
    var contact_ous = $(td).attr("contact_ous").split("|");
    var ous_list_str = "该操作员的通信权限为:\n";
    for(var i=0;i<contact_ous.length;i++){
        ous_list_str += get_oudn_name(contact_ous[i])+"\n";
    }
    alert(ous_list_str);
}

/*安全员*/
//安全员页面初始化
function sainit(){
    var loginType=$.cookie("loginType");
    var uid=$.cookie("userid");
    var sa_right="";
    if (loginType=="sa"){
        if (uid=="SA"){
            sa_right="高级安全员";
        }else{
            sa_right="普通安全员";
        }
    }
    setText($("#saqx"),sa_right);
    setText($("#saName"),uid);
}
//salist初始化
function sahome(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/sa_tree",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            showsalist(all);
            loadingStatus("成功获取用户信息！", 0);
            $("#sa_yic").append(html);	//添加一个账户
            $("#sa_guanli").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    var count=1;
    function showsalist(all){
        html='<h1>中国科学院信息工程研究所</h1>'
        count+=1;
        temp = count;
        loadingStatus("正在获取用户信息!",0);

        var users=all;   //所有master

        //每一个群组要进行的操作
        html+='<div id=sadiv>';
        html+='<span id=sa></span>';
        html+='<img src="images/group.png"/>';
        html+='<span>';
        html+= "安全员列表";
        html+='</span>';
        html+='</div>';

        for(var j=0;j<users.length;j++){
            html+='<li title="'+users[j]['uid']+'">';
            html+='<span title="'+users[j]['uid']+'" id="'+users[j]['uid']+'" class="checkbox checkbox_uncheck" onclick="showsa(this.title)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html+='<img src="images/unline.png"/>';
            html+='<a class="'+users[j]['phonenumber']+":"+users[j]['email']+'"name="'+users[j]['qx']+'" title="'+users[j]['uid']+'" style="cursor:pointer">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html+=users[j]['uid'];
            html+='</a>';
            html+='</li>';
        }
        html+='</div>';
        count=temp;
    }
}
//sa信息展示
function showsa(uid){
    span=document.getElementById(uid);
    //是否选中
    if(span.className=="checkbox checkbox_uncheck"){
        var obj={
            _path:"/a/wp/org/sa_tree",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            var all = data.all;
            if (rt != 0) {
                loadingStatus("获取信息失败！", 0);
            } else {
                //勾选显示管理员信息
                for(var j=0;j<all.length;j++){
                    if(uid==all[j]['uid']){
                        var xuhao=j+1;
                        var txt;
                        txt="";
                        txt+='<tr class="'+uid+'">';
                        txt+='<td><span class="checkbox checkbox_uncheck"></span>';
                        txt+='</td><td id="'+xuhao+'">'+xuhao+'</td>';
                        txt+='<td class="username">'+uid+'</td>';
                        txt+='<td class="Email">'+all[j]['email']+'</td><td class="Telephone">'+all[j]['phonenumber']+'</td><td>'+all[j]['qx']+'</td></tr>';
                        $("#sa_yglb tbody").append(txt);
                        $("#sa_shebeiB").mCustomScrollbar("update");
                        loadingStatus("获取用户信息成功！",0);
                    }
                }
            }
        },"正在获取用户信息!");
    }else{
        //解除勾选隐藏用户信息
        $("#sa_yglb tbody tr").each(function(index,element){
            var username =$(".username",$(element)).html();
            if(username==uid){
                $(element).remove();
            }
        });
    }
}

/*审计员*/
//审计员页面初始化
function auditorinit(){
    var loginType=$.cookie("loginType");
    var uid=$.cookie("userid");
    var auditor_right="";
    if (loginType=="auditor"){
        if (uid=="auditor"){
            auditor_right="高级审计员";
        }else{
            auditor_right="普通审计员";
        }
    }
    setText($("#auditorqx"),auditor_right);
    setText($("#auditorName"),uid);
}
//auditorlist初始化
function auditorhome(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/auditor_tree",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            showaulist(all);
            loadingStatus("成功获取用户信息！", 0);
            $("#au_yic").append(html);	//添加一个账户
            $("#au_guanli").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    var count=1;
    function showaulist(all){
        html='<h1>中国科学院信息工程研究所</h1>'
        count+=1;
        temp = count;
        loadingStatus("正在获取用户信息!",0);

        var users=all;   //所有master

        //每一个群组要进行的操作
        html+='<div id=auditordiv>';
        html+='<span id=auditor></span>';
        html+='<img src="images/group.png"/>';
        html+='<span>';
        html+= "审计员列表";
        html+='</span>';
        html+='</div>';

        for(var j=0;j<users.length;j++){
            html+='<li title="'+users[j]['uid']+'">';
            html+='<span title="'+users[j]['uid']+'" id="'+users[j]['uid']+'" class="checkbox checkbox_uncheck" onclick="showauditor(this.title)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html+='<img src="images/unline.png"/>';
            html+='<a class="'+users[j]['phonenumber']+":"+users[j]['email']+'"name="'+users[j]['qx']+'" title="'+users[j]['uid']+'" style="cursor:pointer">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html+=users[j]['uid'];
            html+='</a>';
            html+='</li>';
        }
        html+='</div>';
        count=temp;
    }
}
//auditor信息展示
function showauditor(uid){
    span=document.getElementById(uid);
    //是否选中
    if(span.className=="checkbox checkbox_uncheck"){
        var obj={
            _path:"/a/wp/org/auditor_tree",
            _methods:"get",
            param:{
                sid:$.cookie("org_session_id"),
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            var all = data.all;
            if (rt != 0) {
                loadingStatus("获取信息失败！", 0);
            } else {
                //勾选显示管理员信息
                for(var j=0;j<all.length;j++){
                    if(uid==all[j]['uid']){
                        var xuhao=j+1;
                        var txt;
                        txt="";
                        txt+='<tr class="'+uid+'">';
                        txt+='<td><span class="checkbox checkbox_uncheck"></span>';
                        txt+='</td><td id="'+xuhao+'">'+xuhao+'</td>';
                        txt+='<td class="username">'+uid+'</td>';
                        txt+='<td class="Email">'+all[j]['email']+'</td><td class="Telephone">'+all[j]['phonenumber']+'</td><td>'+all[j]['qx']+'</td></tr>';
                        $("#au_yglb tbody").append(txt);
                        $("#au_shebeiB").mCustomScrollbar("update");
                        loadingStatus("获取用户信息成功！",0);
                    }
                }
            }
        },"正在获取用户信息!");
    }else{
        //解除勾选隐藏用户信息
        $("#au_yglb tbody tr").each(function(index,element){
            var username =$(".username",$(element)).html();
            if(username==uid){
                $(element).remove();
            }
        });
    }
}
//审计日志列表显示(预加载)
function loadauditorlog(){
    loadingStatus("正在加载审计日志...",1);
    var obj={
        _path:"/a/wp/org/get_audit_log",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj,function(data){
        //auditorlogs:{'_id':0,'uid':1,'action':1,'info':1,'result':1,'time':1}
        var rt=data.rt;
        var auditlogs=data.auditlogs;
        var log_space_state=data.log_space_state;
        if(rt == 0)
        {
            loadingStatus("获取审计日志成功!",0);
            if(log_space_state=='need_del'){
                alert("提示：日志空间将满，请及时清理！");
            }else if(log_space_state=='del'){
                alert("警告：日志空间已满，请处理！！！");
            }
            for(var i=0;i<auditlogs.length;i++)
            {
                showauditlog(auditlogs[i],i+1);
            }
        }else{
            loadingStatus("获取审计日志失败!",0);
        }
    },"正在获取审计日志...");
}
function showauditlog(auditlog,i){
    //auditorlogs:{'_id':0,'uid':1,'action':1,'info':1,'result':1,'time':1}
    //操作时间 操作者 操作类型 操作描述 操作结果
    var op_time=auditlog['time'];
    var user=auditlog['uid'];
    var op_type=auditlog['action'];
    var op_desc=auditlog['info'];
    var op_result=auditlog['result'];
    var op_obj=auditlog['users'];
    //解析json对象
    //op_desc=JSON.stringify(op_desc);
    //op_desc=op_desc.toJSONString();
    //var op_time=new Date(parseInt(optime) * 1000).toLocaleString()
    //console.log(JSON.stringify(op_desc));
    if(op_type=="send contacts"){
        //op_desc=JSON.stringify(op_desc['ous'][0]['users']);
        op_desd=JSON.stringify(op_obj[0]['oudn'].split(',')[0].slice(3,-1));
        op_desdnum=JSON.stringify(op_obj.length);
        str=op_desd.replace(/\"/g,"");
        //console.log(op_desd);
        //console.log(op_desdnum);
        if (op_result==0){
            op_result="下发成功"
        }
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+"同步联系人"+'</td>';
        txt+='<td>'+str+':'+op_desdnum+'人'+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="adminlogin"){
        var op_type="操作员登陆";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="auditorlogin"){
        var op_type="审计员登陆";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="masterlogin"){
        var op_type="管理员登陆";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="salogin"){
        var op_type="安全员登陆";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="adminlogout"){
        var op_type="操作员登出";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="auditorlogout"){
        var op_type="审计员登出";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="masterlogout"){
        var op_type="管理员登出";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_type=="salogout"){
        var op_type="安全员登出";
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
    }else if(op_desc=="修改锁屏密码") {
        var txt;
        txt = "";
        txt += '<tr><td>' + i + '</td>';
        txt += '<td>' + op_time + '</td>';
        txt += '<td>' + user + '</td>';
        txt += '<td>' + op_type + '</td>';
        txt += '<td>' + op_desc+":"+op_obj + '</td>';
        txt += '<td>' + op_result + '</td>';
    }else{
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+op_type+'</td>';
        txt+='<td>'+op_desc+'</td>';
        txt+='<td>'+op_result+'</td>';
}


    //console.log(op_desc);
    //审计日志内容

    $("#au_stB tbody").append(txt);
    $(" #auditlogB").mCustomScrollbar("update");

}


//control多维管控页面初始化
function controlhome(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/control_tree",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id")
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all = data.all;
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            showcontrollist(all);
            loadingStatus("成功获取用户信息！", 0);
            $("#control_yic").append(html);	//添加一个账户
            $("#control_guanli").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    var count=1;
    function showcontrollist(all){
        html='<h1>中国科学院信息工程研究所</h1>'
        count+=1;
        temp = count;
        loadingStatus("正在获取用户信息!",0);
        var users=all;   //所有master

        //每一个群组要进行的操作
        //html+='<div id=controldiv>';
        //html+='<span id=control></span>';
        //html+='<img src="images/group.png"/>';
        //html+='<span>';
        //html+= "多维管控列表";
        //html+='</span>';
        //html+='</div>';

        for(var j=0;j<users.length;j++) {
            html += '<li title="' + users[j] + '">';
            html += '<span title="' + users[j] + '" id="' + users[j] + '" class="checkbox checkbox_uncheck" onclick="showcontrol(this.title)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html += '<img src="images/unline.png"/>';
            html += '<a class="' + users[j] + '" title="' + users[j] + '" style="cursor:pointer">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html += users[j];
            html += '</a>';
            html += '</li>';
        }

        html+='</div>';
        count=temp;
    }
}
//基站设备信息展示
function showcontrol(uid){
    span=document.getElementById(uid);
    //是否选中
    if(span.className=="checkbox checkbox_uncheck"){
        var obj={
            _path:"/a/wp/org/control_tree_list",
            _methods:"get",
            param:{

                institute:uid
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            var all = data.all;
            console.log(all);
            if (rt != 0) {
                loadingStatus("获取信息失败！", 0);
            } else {
                //勾选显示管理员信息
                for(var j=0;j<all.length;j++){
                    if(uid==all[j]['institute']){

                        if(all[j]['status']=='1'){
                            var st="在线";
                        }else{
                            var st="离线";
                        }
                        if(all[j]['type']=='pseudo_bs'){
                            var tp="伪基站"
                        }else{
                            var tp="检测门"
                        }
                        console.log(st);
                        var xuhao=j+1;
                        var txt;
                        institute=all[j]["institute"];
                        position=all[j]["position"];
                        txt="";
                        txt+='<tr class="'+all[j]['uid']+'" >';
                        txt+='<td><span class="checkbox checkbox_uncheck"></span>';
                        txt+='</td><td id="'+xuhao+'">'+st+'</td>';
                        txt+='<td class="control_type">'+tp+'</td>';
                        //txt+='<td class="control_uid">'+all[j]['uid']+'</td><td class="control_institute">'+all[j]['institute']+'</td><td class="control_time">'+all[j]["last_time"]+'</td><td class="control_position">'+all[j]["position"]+'</td><td><label onclick="findinfo()">静态信息</td></tr>';
                        txt+='<td class="control_uid">'+all[j]['uid']+'</td>' +
                            //'<td class="control_institute">'+all[j]['institute']+'</td>' +
                            '<td class="control_institute" onclick="showallinstitute(this)">'+institute+'</td>'+
                            '<td class="control_time">'+all[j]["last_time"]+'</td>' +
                            '<td class="control_position" onclick="showallposition(this)">'+position+'</td>' +
                            '<td><img class="lock" alt="unlock" title="suoding" src="images/unlock.png" /></td></tr>';
                        $("#control_yglb tbody").append(txt);
                        $("#control_shebeiB").mCustomScrollbar("update");
                        loadingStatus("获取用户信息成功！",0);
                        //updateStatus("#ma_yglb tbody tr:last-child");
                    }
                }
            }
        },"正在获取用户信息!");
    }else{
        //解除勾选隐藏用户信息
        $("#control_yglb tbody tr").each(function(index,element){
            var username =$(".control_institute",$(element)).html();
            if(username==uid){
                $(element).remove();
            }
        });
    }
}
function showallinstitute(element){
    alert(element.innerText);
}
function showallposition(element){
    alert(element.innerText);
}
//多维管控设备动态信息页面初始化
function controlinfohome(){
    //window.location.href="http://111.204.189.58:8083/f_org_controlInfo";

    //var  getval=document.getElementById("cc").value;
    //document.location.href("b.html?cc="+getval);
    var a=[];
    var arr = check_controlssyh();
    for(var i=0;i<arr.length;i++){
        a.push(arr[i]);
    }
    //window.location.href='http://111.204.189.58:8083/f_org_controlInfo?param='+a;
    //location.href='http://111.204.189.58:8083/f_org_controlInfo?param='+a;
    location.href='http://111.204.189.34:8083/f_org_controlInfo?param='+a;
}


