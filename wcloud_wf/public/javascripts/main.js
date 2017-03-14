//切换
$(".tab a").on("click",function(event){
	var tabTarget=this.dataset.target;	//获取tab项的目标
	var id=$(this).attr("href");			//获取要显示的项目的id；
	var container=this.dataset.container;	//获取按钮的包含容器
	$("#"+container+" a").removeClass("active");	//从包含容器中删除所有按钮的活动状态
	$(this).addClass("active");		//为当前按钮添加活动状态
	$("#"+tabTarget+" > .tabP").hide();	//隐藏目标项目的所有项
	$(id).show();			//显示当前目标href指定的项目
	event.preventDefault();	//阻止默认行为
});

//初始化
var height=$(window).outerHeight(true);		//获取窗口的高度
var mainMenuContainer=$("#mainMenuContainer");	//获取mainMenuContainer元素
var mainContainer=$("#mainContainer");		//获取mainContainer元素
var lastAppTit=$("#lastAppTit");			//获取首页最新app的容器。
var lastCon=$("#lastCon");				//显示更多页面中的项目容器。
var historyApp=$("#historyApp");		//显示历史应用的容器。
var canUpdate=$("#canUpdate");		//可以更新的容器。
var onLast=$("#onLast");				//已经是最新的容器。
var shRes=$("#shRes");				//搜索结果的容器。
var url=location.href;
var session_id="";			//初始化sessionid；
var dev_id="";				//初始化设备的id；
var appTemp={
	allApps:[],		//所有的app_id.
	allAppsInfo:[],	//所有的应用的详细信息。
	notInstallNativeApps:[],		//以前有，但是现在没有的app_id ['aa','bb']
	notInstallNativeAppsInfo:[],	//历史原生app的详细信息。
	lastVerApps:[],					//最新的			['aa','bb']
	installNativeApps:[],			//当前已经安装的本地app_id [{},{}]
	notInstallWebApps:[],			//以前有，现在没有的web app ['aa','bb']
	notInstallWebAppsInfo:[],		//获取未安装的webapp的详细信息。
	installWebApps:[],				//当前已经安装的web app [{},{}]
	canUpdateAppsInfo:[]				//可以更新的app 的详细信息。
};
(function parseSessionAndDev(){			//解析session和dev
	var sandid=url.split("?")[1];
	var sid=sandid.split("&")[0];
	var dev=sandid.split("&")[1];
	session_id=sid.split("=")[1];
	dev_id=dev.split("=")[1];
})();//立即执行解析。
mainMenuContainer.css({height:height});	//将mainMenuContainer的高度设置为窗口高度

$(window).resize(function(event){
	height=$(window).outerHeight(true);		//窗口变化时，更新窗口的大小
	mainMenuContainer.css({height:height});	//更新mainMenuContainer的高度。
})
//注册点击账户时弹出和收回菜单
$(".zhu img").on("click",popMenu);		//点击主页面的时候弹出menu
function popMenu(event){
	var that=$("#mainPage")[0];			//获取mainPage
	that.style.left="160px";			//将mainPage的lefe值变成160，露出菜单
	setTimeout(function(){that.style.zIndex=-1;},400);	//将mainPage的zIndex变小，露出菜单。
	mainContainer.css({overflowY:"hidden"});			//弹出菜单时设置y方向溢出隐藏
	event.preventDefault();
}
mainMenuContainer.on("click",pushMenu);
function pushMenu(event){
	var that=$("#mainPage")[0];
	that.style.left="0";
	that.style.zIndex="auto";
	mainContainer.css({overflowY:"visible"});
	event.preventDefault();
}
//登陆进来之后，首先获取所有appId。
loadAppId();		//已时间排序获得。
//获取所有的app——id列表	***
function loadAppId(){
	var obj={
		_path:"/a/was/applist",
		_methods:"get",
		param:{
			//key:all 不提供表示所有
			sort:"time",
			is_asc:"no",
			count:100
		}
	};
	ajaxReq(obj,function(data){
		appTemp.allApps=data.applist;		//将所有的设备名存储到allApps
		loadAllAppsInfo();					//获取到app-id之后立刻去获取信息。
		loadWebApp();						//获取到所哟的app-id之后才能回去到已安装的web app；
	});
}
//获取所有app_id的详细信息，赋值到allAppsInfo； ***
function loadAllAppsInfo(){
	var allApps=appTemp.allApps;
	for(var i=0,len=allApps.length;i<len;i++){
		var obj={
			_path:"/a/was/appinfo",
			_methods:"get",
			param:{
				app_id:allApps[i]
			}
		};
		ajaxReq(obj,function(data){
			var appInfo=data.appinfo;
			appTemp.allAppsInfo.push(appInfo);
		});
	}
}
//获取设备webApp应用信息	**
function loadWebApp(){
	var obj={
		_path:"/a/wp/user/dev_wapp_info",
		_methods:"get",
		param:{
			sid:session_id,
			dev_id:dev_id
		}
	};
	ajaxReq(obj,function(data){
		var apps=[];		//暂存webapps
		var not_install_apps=[];	//暂存历史webapps
		if(data.apps){
			apps=JSON.parse(data.apps);
		}
		if(data.not_install_apps){
			not_install_apps=data.not_install_apps;
		}
		appTemp.installWebApps=apps;		//获取webapp的详细信息。
		appTemp.notInstallWebApps=not_install_apps;	//历史webapp的id。
		//获取未安装的webapp的详细信息
		loadNotInstallWebApps();
	});
}
//获取未安装的历史webApp的信息
function loadNotInstallWebApps(){
	var notInstallWebApps=appTemp.notInstallWebApps;
	for(var i=0,len=notInstallWebApps.length;i<len;i++){
		var obj={
			_path:"/a/was/appinfo",
			_methods:"get",
			param:{
				app_id:notInstallWebApps[i]
			}
		};
		ajaxReq(obj,function(data){
			var appInfo=data.appinfo;
			appTemp.notInstallWebAppsInfo.push(appInfo);
		});
	}
	//获取完历史webapp之后再获取原生的app。
	loadInstallApp();
}
//获取设备原生App应用信息
function loadInstallApp(){
	var obj={
		_path:"/a/wp/user/dev_app_info",
		_methods:"get",
		param:{
			sid:session_id,
			dev_id:dev_id
		}
	};
	ajaxReq(obj,function(data){
		var apps=[];		//暂存apps
		var not_install_apps=[];		//暂存历史原生app
		if(data.apps){		//如果存在已经安装的本地app则赋值
			apps=JSON.parse(data.apps);
		}
		if(data.not_install_apps){	//如果存在历史本地app则赋值
			not_install_apps=data.not_install_apps;
		}
		appTemp.installNativeApps=apps;	//将已安装的本地app信息存储。（包含版本名和icon)
		appTemp.notInstallNativeApps=not_install_apps;	//将历史webapp信息存储。(只是app名字)
		//name:apps[0].app_name;
		//version:apps[0].version_name;
		//icon:apps[0].icon;    data:image/png;base64,

		//checkoutUpdateApps();			//获取到已经安装的本地应用之后，检出能更新的app；
		//获取原生app之后，再次获取历史原生app。
		loadNotNativeInfo();
	})
}
//获取本地历史app的详细信息
function loadNotNativeInfo(){
	var notInstallNativeApps=appTemp.notInstallNativeApps;
	for(var i=0,len=notInstallNativeApps.length;i<len;i++){
		var obj={
			_path:"/a/was/appinfo",
			_methods:"get",
			param:{
				app_id:notInstallNativeApps[i]
			}
		};
		ajaxReq(obj,function(data){
			var appInfo=data.appinfo;
			appTemp.notInstallNativeAppsInfo.push(appInfo);
		})
	}
	checkoutUpdateAppsAndLast();
}
//检索出可以更新的app和最新的app
function checkoutUpdateAppsAndLast(){
	try{
		for(var i=0,len=appTemp.installNativeApps.length;i<len;i++){
			for(var k=0,lg=appTemp.allAppsInfo.length;k<lg;k++){
				if(appTemp.allAppsInfo[k]["app_id"]==appTemp.installNativeApps[i]["app_id"]){
					var currVersion=parseFloat(appTemp.allAppsInfo[k]["version"]);
					var version=parseFloat(appTemp.installNativeApps[i]["version_name"]);
					if(currVersion>version){		//如果有新版本，则从以安装移动到可更新
						appTemp.installNativeApps[i]["apptype"]="native";
						appTemp.canUpdateAppsInfo.push(appTemp.installNativeApps.splice(i,1));
					}
					//最后在所有app中删除它。以后他就属于可更新的了，allappinfo存储的其实是未安装的。
					appTemp.allAppsInfo.splice(k,1);
				}
			}
		}
		for(var j=0,size=appTemp.installWebApps.length;j<size;j++){
			for(var d=0,ds=appTemp.allAppsInfo.length;d<ds;d++){
				if(appTemp.allAppsInfo[d]["app_id"]==appTemp.installWebApps[j]["app_id"]){
					appTemp.allAppsInfo.splice(d,1);	//检索allapps中是否有已经安装的webapp，有则删除。
				}
			}
		}
	}catch(err){}
		
	//检索分类完成之后，就可以更新页面了。
	callShowLast(6,appTemp.allAppsInfo,lastAppTit);		//首先显示预览的最新的app
	setTimeout(function(){
		callShowLast(6,appTemp.allAppsInfo,lastAppTit);		//首先显示预览的最新的app
	},10000)			//10s之后再刷新一次。
	callShowLast(0,appTemp.allAppsInfo,lastCon);			//接下来填充更多页面的app
	showInstallAndCanUpdate();							//再然后显示已安装的和可更新的。
}
//通过app—id显示首页app的信息
function showPreLastApp(obj,container){
	//console.log(showPreLastApp.caller)
	var type;
	var btnTxt;
	var btnClass;
	var html="";
	//包含类型名字和icon之类的信息
	try{
	if(obj.apptype=="native"){
		type="本地应用";
		btnTxt="下载";
		btnClass="btn_download";
	}else if(obj.apptype=="web"){
		type="web应用";
		btnTxt="安装";
		btnClass="btn_install";
	}else{
		return false;
	}
	html+='<div class="threeList">';
	html+='<p class="photo">';
	html+='<img src="data:image/png;base64,'+obj["icon"]+'" />';
	html+='</p>';
	html+='<p class="name">'+obj["app_name"]+'</p>';
	html+='<p class="small">'+type+'</p>';
	html+='<p class="disc small">版本 '+obj["version"]+'</p>';
	html+='<p class="btn"><a href="#'+obj["app_id"]+'" class="'+btnClass+'">'+btnTxt+'</a></p>';
	html+='</div>';
	container.append(html);
	}catch(err){}
	
}
function callShowLast(num,obj,container){
	//console.log(callShowLast.caller);
	container.html("");
	var total;
	if(num>0&&num<obj.length){		//检查传递的参数，如果大于0(并且不多于全部），则按照num显示，如果非，则显示所有。
		total=num;
	}else{
		total=appTemp.allApps.length;
	}
	for(var i=0;i<total;i++){
		showPreLastApp(obj[i],container);
	}
}
//显示历史的app
function showHistory(){
	historyApp.html("");
	var historyAppsInfo=appTemp.notInstallNativeAppsInfo.concat(appTemp.notInstallWebAppsInfo);
	for(var i=0,len=historyAppsInfo.length;i<len;i++){
		var appInfo;
		var html="";
		var btnTxt;
		var btnClass;
		var type;
		appInfo=historyAppsInfo[i];
		if(appInfo.apptype=="native"){
			type="本地应用";
			btnTxt="下载";
			btnClass="btn_download";
		}else if(appInfo.apptype=="web"){
			type="web应用";
			btnTxt="安装";
			btnClass="btn_install";
		}else{
			return false;
		}
		html+='<div class="oneList">';
		html+='<div class="photoc">';
		html+='<p class="photo">';
		html+='<img src="data:image/png;base64,'+appInfo["icon"]+'" />';
		html+='</p>';
		html+='</div>';
		html+='<div class="discB">';
		html+='<p class="name">'+appInfo["app_name"]+'</p>';
		html+='<p class="disc small">'+type+' 版本号 '+appInfo["version"]+'</p>';
		html+='</div>';
		html+='<div class="btn">';
		html+='<a href="#'+appInfo["app_id"]+'" class="'+btnClass+'">'+btnTxt+'</a>';
		html+='</div>';
		html+='</div>';
		historyApp.append(html);
	}
}
//显示已经安装的（包括可更新的)
function showOneList(obj,container,btnClass,btnTxt,type){
	try{
		if(obj.apptype=="native"){
			type="本地应用";
			btnTxt="下载";
			btnClass="btn_download";
		}else if(obj.apptype=="web"){
			type="web应用";
			btnTxt="安装";
			btnClass="btn_install";
		}else{
			
		}		
	
	var html="";
	html+='<div class="oneList">';
	html+='<div class="photoc">';
	html+='<p class="photo">';
	html+='<img src="data:image/png;base64,'+obj["icon"]+'" />';
	html+='</p>';
	html+='</div>';
	html+='<div class="discB">';
	html+='<p class="name">'+obj["app_name"]+'</p>';
	html+='<p class="disc small">'+type+' 版本号 '+obj["version"]+'</p>';
	html+='</div>';
	html+='<div class="btn">';
	html+='<a href="#'+obj["app_id"]+'" class="'+btnClass+'">'+btnTxt+'</a>';
	html+='</div>';
	html+='</div>';
	container.append(html);
	}catch(err){
		console.log(err.message);
	}
}
function showInstallAndCanUpdate(){
	canUpdate.html("");
	onLast.html("");
	for(var i=0,len=appTemp.canUpdateAppsInfo.length;i<len;i++){
		showOneList(appTemp.canUpdateAppsInfo[i],canUpdate,'btn_download',"可更新","本地应用");
	}
	for(var k=0,lg=appTemp.installWebApps.length;k<lg;k++){
		showOneList(appTemp.installWebApps[k],onLast,'btn_disabled',"已安装","web应用");
	}
	for(var j=0,bn=appTemp.installNativeApps.length;j<bn;j++){
		showOneList(appTemp.installNativeApps[j],onLast,'btn_disabled',"已安装","本地应用");
	}
}
$("#tmpBtn").on("click",function(event){		//点击我的应用默认刷新历史应用。
	showHistory();
})
$("#yysd").on("click",function(event){			//点击应用商店，默认刷新首页展示的6个app
	callShowLast(6,appTemp.allAppsInfo,lastAppTit);
})
$("#lishi").on("click",function(event){		//点击历史应用按钮，刷新历史应用。
	showHistory();
})
$("#dangqian").on("click",function(event){		//点击当前应用按钮，刷新当前应用。
	showInstallAndCanUpdate();
})
$("#gengduo").on("click",function(event){		//点击更多按钮的时候，刷新更多页面的app
	callShowLast(0,appTemp.allAppsInfo,lastCon);
})
$("#qxl").on("click",function(event){		//点击搜索页面的取消按钮，则清空
	shRes.html("");
})
//注册按钮点击事件
$(document).on("click","a.btn_disabled",function(evnet){
	event.preventDefault();
})
$(document).on("click","a.btn_download",sendCmd);
$(document).on("click","a.btn_install",sendCmd);
$(document).on("click","#updateAll",function(event){		//点击更新全部的按钮，可更新容器的按钮都会被触发安装请求。
	$("a",canUpdate).click();
	event.preventDefault();
})
//像设备发送指令（安装app的指令）
function sendCmd(event){
	event.preventDefault();
	var that=$(this);
	if(that.hasClass("btn_install")){
		that.removeClass("btn_install").addClass("btn_disabled");
		that.html("正在安装");
	}else if(that.hasClass("btn_download")){
		that.removeClass("btn_download").addClass("btn_disabled");
		that.html("正在下载");
	}else if(that.hasClass("btn_disabled")){
		return false;
	}
	var href=that.attr("href");
	var cmd=href.split("#")[1];
	var obj={
		_path:"/a/wp/user/send_cmd",
		_methods:"post",
		param:{
			sid:session_id,
			dev_id:dev_id,
			cmd:"install_app "+cmd		//点击安装按钮时触发这个安装请求。
		}
	};
	ajaxReq(obj,function(data){
		//完成之后要把下载或者更新的按钮改变状态
	});
}
$("#shBtn").on("keyup",flushShRes);
$("#shBtn").on("change",flushShRes);
$("#shBtn").on("keypress",flushShRes);
$("#shBtn").on("input",flushShRes);
function flushShRes(event){
	shRes.html("");
	var value=$(this).val();
	if(!!value){
		for(var i=0,len=appTemp.allAppsInfo.length;i<len;i++){
			var appInfo=appTemp.allAppsInfo[i];
			if(appInfo["app_name"].indexOf(value)>-1){
				showOneList(appInfo,shRes);
			}
		}
	}
	
}
//抽象ajax请求函数
function ajaxReq(obj, func) //obj是要发送的数据  url是nodejs接受请求的路径 time是请求允许的时间
{
	$.ajax({
		async: true,
		timeout: 60000,
		type: "POST",
		url: "/f_login",
		data: obj,
		dataType: 'json',
		beforeSend: function(jqXHR) {
		},
		success: function(data) {
			var rt = data.rt;
			switch (rt) {
				case 0:
					func(data);
					break;
				default:
					break;
			}
		},
		error: function(jqXHR, textStatus, errorThrown) {
			switch (textStatus) {
				case "timeout":
					alert("请求超时!");
					break;
				case "error":
				case null:
					alert("发生错误，请重试!");
					break;
				case "notmodified":
					alert("notmodified.");
					break;
				case "parsererror":
					alert("parsererror.");
					break;
				default:
					alert("未知错误。");
			}
		}
	});
}