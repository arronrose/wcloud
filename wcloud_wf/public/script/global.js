// JavaScript Document
//定义错误代码列表
var gMark='#device';
$(document).ready(function(e) {
	//停留在设备管理页面
	var device=$("#device");
	var app=$("#app");
	var details=$("#details");
	var infoBtn=$("#infoBtn");
	var tab=$("#wrapper .tab");
	$("nav ul li a").live('click',function(event) {
		var target=$(event.target);
		var href=target.attr('href');
		if(!!href){
			$("nav ul li a").removeClass('here');
			target.addClass('here');
			if(href=='#device'){
				gMark='#device';		//标记到device页面。
				tab.hide();
				device.show();
				devPostion(); //更新设备的位置。	只有在显示地图的时候，才会刷新位置。
			}else if(href=='#details'){
				gMark='#details';		//标记到详细资料页面
				tab.hide();
				infoBtn.show();		//显示按钮
				details.show();		//显示详细信息
				loadDetails();	//获取设备的详细信息		只有在显示详细信息的时候才会刷新详细信息。
			}else if (href=='#app') {
				gMark='#app';		//标记到app页面
				tab.hide();
				app.show();
				loadApp();			//刷新APP信息
			}
		}
		return false;
	});
	/*头部*/
	var $acc = $("#acc");
	var $lb = $("#lb", $acc);
	$acc.click(function(event) {
		//$lb.slideToggle("fast");
		$("#zhanghao").addClass('act');
		$lb.slideDown("fast");
	});
	$acc.hover(function(event) {}, function(event) { //鼠标划出隐藏。
		$lb.slideUp("fast", function() {
			$("#zhanghao").removeClass('act');
		});
	});
	$("a", $acc).click(function(event) {
		var targetId = event.target.id;
		if (targetId == "gengxin" || targetId == "dengchu") {
			return true;
		} //预留登出和更新按钮
		$lb.slideUp("fast", function() {
			$("#zhanghao").removeClass('act');
		});
		return false;
	});
	var $currentZh = $("#currentZh");
	var $altZh = $("#altZh");
	$("#currentZh").live('click', function(event) {
		$("a", $currentZh).addClass("act");
		$("#altZh").toggle();
	})
	$("#zhangHu").hover(function(event) {}, function(event) {
		$("a", $currentZh).removeClass("act");
		$("#altZh").hide();
	});
	$("#zhangHu a").live('click', function(event) { //切换设备的时候
		event.preventDefault(); //阻止默认动作，不阻止事件冒泡
		$("a", $currentZh).removeClass("act");
		$("#altZh").append($("a", $("#currentZh"))).hide();
		$("#currentZh").append(this);
		lastUpdateTime(); //获得上次更新的时间（针对不同的设备)
		findPhone(); //看手机在线不在线
		if(gMark=='#details'){
			loadDetails();	//获取设备的详细信息
		}else if(gMark=='#device'){
			devPostion(); //更新设备的位置。	只有在显示地图的时候，才会刷新位置。
		}else if(gMark=='#app'){
			loadApp();
		}
	});
	$("#reload").click(function(event) {
		event.preventDefault();
		window.location.reload();
	});
	/*弹出层的设置*/
	$(".dialog").each(function(index, element) {
		var $width = $(this).outerWidth(); //宽度默认300， 添加宽度。
		$(this).dialog({ //所有添加dialog类的元素都会变成弹出层 开始是隐藏的
			width: $width,
			autoOpen: false,
			modal: true,
			resizable: false,
			show: "scale"
		});
	});
	$(".cb").click(function(event) { /*所有添加cb类的元素都弹出他连接对应的模块*/
		var id = this.href.split("#")[1];
		id = "#" + id;
		$(id).dialog("open");
		return false;
	});
	//验证码的切换事件注册
	$("#yanz").click(getVer);
	$("#huan").click(getVer);
	//登陆验证
	var login = $("#login");
	var email = $("#Email");
	var pwd = $("#pwd");
	var vert=$("#vert");
	var saveP=$("#savePerson");
	var errTishi = $("#errTishi");
	//账号输入框的控制
	vert.focus(function(event){
		$("label[for='vert']").fadeOut("fast");
	});
	vert.blur(function(event){
		if(!vert.val().replace(/\s/g,"")){
			$("label[for='vert']").fadeIn("fast");
		}
	});
	email.focus(function(event) {
		//--hideT();
		$("label[for='Email']").fadeOut("fast");
	});
	email.blur(function(event) {
		if (!email.val().replace(/\s/g, "")) { //如果都是空格
			email.val("");
			$("label[for='Email']").fadeIn("fast");
		}
	});
	email.change(function(event) {
		if (email.val()) {
			$("label[for='Email']").fadeOut("fast");
		}
	});
	email.keypress(function(event){
		$("label[for='Email']").fadeOut("fast");
	});
	pwd.keypress(function(event){
		$("label[for='pwd']").fadeOut("fast");
	});
	//兼容ie
	try{
		var ie_pwd=document.getElementById('pwd');
		var ie_email=document.getElementById('Email');
		ie_pwd.attachEvent('onpropertychange',function(){
			$("label[for='pwd']").fadeOut("fast");
		})
		ie_email.attachEvent('onpropertychange',function(){
			$("label[for='Email']").fadeOut("fast");
		})
		pwd.bind('input',function(event){
			$("label[for='pwd']").fadeOut("fast");
		})
		email.bind('input',function(event){
			$("label[for='Email']").fadeOut("fast");
		})
	}catch(error){
	}
	email.change();
	pwd.change();
	pwd.focus(function(event) {
		$("label[for='pwd']").fadeOut("fast");
	});
	pwd.blur(function(event) {
		if (!pwd.val().replace(/\s/g, "")) { //如果都是空格
			pwd.val("");
			$("label[for='pwd']").fadeIn("fast");
		}
	});
	pwd.change(function(event) {
		if (pwd.val()) {
			$("label[for='pwd']").fadeOut("fast");
		}
	});
	login.submit(function(event) {
		event.preventDefault(); //阻止表单提交。
		email.removeClass("errMsn"); //如果有错误提示，取消提示
		pwd.removeClass("errMsn");
		vert.removeClass("errMsn");
		errTishi.html(""); //开头是13 14 15 18的位数在7到11位的手机号码。
		//if (!(/^1[0|3|4|5|8][0-9]\d{8}$/.test(email.val())))
		if(!email.val().replace(/\s/g,""))		//不限定电话号码登陆，非空即可。
		{
			errTishi.html("请填写正确的手机号码!"); //提示手机号码格式不对。
			email.addClass("errMsn"); //框体变红提示。
			email.val("");
			email.focus();
			return false;
		}
		if (!pwd.val().replace(/\s/g, "")) //密码不能全是空格，也不能为空。
		{
			errTishi.html("密码不能为空!"); //提示密码格式不对。
			pwd.addClass("errMsn"); //增加错误视觉提示。
			pwd.val("");
			pwd.focus();
			return false;
		}
		// if(!vert.val().replace(/\s/g,"")){
		// 	errTishi.html("验证码不能为空!");
		// 	vert.val("");
		// 	vert.addClass("errMsn");
		// 	vert.focus();
		// 	return false;
		// }
		//截获表单，ajax发送这个指令
		var obj = {
			_path: '/a/wp/user/login',
			_methods: 'post',
			param: {
				uid: email.val(), //电话号码
				pw: pwd.val(), //密码
				dev_id: 'web'
			}

		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
		//	getVer();		登陆不需要验证码，禁止刷新验证码
			vert.val("");
			var rt = data.rt;
			var sid = data.sid;
			if (rt === 0) {
				//登陆成功之后，如果选中了记住账号，则保存账号(两周的时间)，如果没有，清空cookie的username字段。
				if(!!saveP.attr('checked')){
					$.cookie('username',email.val(),{ expires: 30 });
				}else{
					$.cookie('username',null);
				}

				var uri = '/f_per_device'//?= + sid;
				$.cookie("session_id",sid);
				loadingStatus("正在跳转...", 1);
				location.href = uri;
			} else if (rt == 2) {
				loadingStatus("用户名或密码错误!", 0);
			}else if(rt==23){
				loadingStatus("验证码输入错误!",0);
				vert.addClass('errMsn');
				vert.focus();
			}else if(rt==17){
				loadingStatus("不存在的用户!",0);
			}else {
				loadingStatus('登陆失败，请重试!', 0);
			}
		});
	}); //登陆验证结束。
	//取得cookie，判断有没有username，如果有，显示账号，选中checkbox，若没，什么都不做。
	if($.cookie('username')){
		email.val($.cookie('username'));
		saveP.attr('checked','checked');
		email.change();
	}
	//找回密码
	var definPwd=$("#definPwd");
//	definPwd.live('click',sv);
	function sv(event){
		event.preventDefault();
		var target=$(event.target);
		var href=target.attr("href");
		if(href=="#zhaohui"){
			$("#loginBtn").attr('disabled', true);
			$("#pnm").append(errTishi);
			$("#tgmp").hide();
			$("#zts").show();
			target.attr("href","#denglu").html("返回登陆 ");
			$("#loginBtn").hide();
			$("#sv").css({visibility:"hidden"});
			$("#zhmm").show();
			$("#yanzheng").show();
		}else if(href=="#denglu"){
			$("#loginBtn").attr('disabled', false);
			$("#tgmp").show().append(errTishi);
			$("#zts").hide();
			target.attr("href","#zhaohui").html("忘记密码?");
			$("#loginBtn").show();
			$("#sv").css({visibility:"visible"});
			$("#zhmm").hide();
			$("#yanzheng").hide();
		}
		derrMs();
	}
	function derrMs(){
		$(".errMsn").removeClass("errMsn");
		loadingStatus('',0);
	}
	var zhmm=$("#zhmm");
	zhmm.live('click',zhaohui);
	//找回密码的时间监听函数。
	function zhaohui(event){
		derrMs();
		// if (!(/^1[0|3|4|5|8][0-9]\d{8}$/.test(email.val())))
		if(!email.val().replace(/\s/g,""))		//不限定电话号码登陆，非空即可。
		{
			errTishi.html("请填写正确的手机号码!"); //提示手机号码格式不对。
			email.addClass("errMsn"); //框体变红提示。
			email.val("");
			email.focus();
			return false;
		}
		if(!vert.val().replace(/\s/g,"")){
			errTishi.html("验证码不能为空!");
			vert.val("");
			vert.addClass('errMsn');
			vert.focus();
			return false;
		}
		var uid = email.val();
		//--hideT();
		var obj = {
			_path: '/a/wp/user/forget_pw',
			_methods: 'post',
			param: {
				uid: uid,
				cid: $("#yanz").attr('alt'),
				cvalue: vert.val()
			}
		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
			getVer();
			var rt = data.rt;
			vert.val("");
			$("label[for='vert']").fadeIn('fast');
			vert.removeClass("errMsn");
			if (rt === 0) {
				definPwd.click();
				loadingStatus('密码发送成功，请登陆!', 0);
				email.removeClass('errMsn');
				vert.removeClass('errMsn');
			} else if (rt === 17) {
				loadingStatus('不存在的账户!', 0);
			}else if(rt==23){
				loadingStatus('验证码输入错误!',0);
				vert.addClass("errMsn");
				getVer();
			}else {
				loadingStatus('发送临时密码失败!', 0);
			}
		});
	}
	//推送连接按钮
	$("#urlSub").click(function(event) {
		var $purl = $("#purl"); //取得url字段
		var url = $purl.val(); //获得url。
		var strRegex = "^((https|http|ftp|rtsp|mms)?://)"  
                + "?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?" // ftp的user@  
                + "(([0-9]{1,3}\.){3}[0-9]{1,3}" // IP形式的URL- 199.194.52.184  
                + "|" // 允许IP和DOMAIN（域名）  
                + "([0-9a-z_!~*'()-]+\.)*" // 域名- www.  
                + "([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]\." // 二级域名  
                + "[a-z]{2,6})" // first level domain- .com or .museum  
                + "(:[0-9]{1,4})?" // 端口- :80  
                + "((/?)|" // a slash isn't required if there is no file name  
                + "(/[0-9a-z_!~*'().;?:@&=+$,%#-]+)+/?)$";  
        var re = new RegExp(strRegex);
		if (!url.replace(/\s/g, "")) {
			loadingStatus("不能发送空链接!", 0);
			return false;
		}
		if(!re.test(url)){
			loadingStatus("发送的连接格式不对!",0);
			return false;
		}
		$purl.val(''); //将文本字段的url置空。
		var session_id = $.cookie("session_id");
		var dev_id = $("#currentZh a img").attr('alt');
		var obj = {
			_path: '/a/wp/user/send_cmd',
			_methods: 'post',
			param: {
				sid: session_id,
				dev_id: dev_id,
				cmd: 'url ' + url
			}
		}
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				loadingStatus("推送连接完成!", 0);
			} else {
				loadingStatus("推送连接失败!", 0);
			}
		})
		$("#tuisong").dialog("close");
	});
	//关闭窗口时，清空数据
	$("#tuisong").live('dialogclose', function(event) {
		$("#purl").val("");
	});
	//清除工作数据的按钮。
	$("#sqingchu").click(function(event) {
		$("#qingchu").dialog("close"); //首先关闭对话框
		var session_id = $.cookie("session_id");
		var dev_id = $("#currentZh a img").attr('alt');
		var obj = {
			_path: '/a/wp/user/send_cmd',
			_methods: 'post',
			param: {
				sid: session_id,
				dev_id: dev_id, //测试设备。
				cmd: 'reset'
			}
		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				loadingStatus('已经清除工作数据!', 0);
			} else {
				loadingStatus('清除工作数据失败!', 0);
			}
		});
	});
	//拒绝拒绝清除的按钮。
	$("#bqingchu").click(function(event) {
		$("#qingchu").dialog("close");
	});

	//手机响铃
	$("#sBell").click(function(event) {
		$("#Bell").dialog("close");
		var session_id = $.cookie("session_id");
		var dev_id = $("#currentZh a img").attr('alt');
		var obj = {
			_path: '/a/wp/user/send_cmd',
			_methods: 'post',
			param: {
				sid: session_id,
				dev_id: dev_id, //测试设备。
				cmd: 'bell'
			}
		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				loadingStatus('设备响铃成功!', 0);
			} else {
				loadingStatus('设备响铃失败!', 0)
			}
		});
	});
	//否定响铃按钮。
	$("#bBell").click(function(event) {
		$("#Bell").dialog("close");
	});

	//锁定设备的按钮
	$("#sSuoding").click(function(event) {
		$("#suoding").dialog("close");
		var session_id = $.cookie("session_id");
		var dev_id = $("#currentZh a img").attr('alt');
		pf(session_id, dev_id, function() {
			var obj = {
				_path: '/a/wp/user/send_cmd',
				_methods: 'post',
				param: {
					sid: session_id,
					dev_id: dev_id,
					cmd: 'lockscreen'
				}
			}
			ajaxReq(obj, '/f_login', 15000, function(data) {
				var rt = data.rt;
				if (rt === 0) {
					loadingStatus("锁定成功!", 0);
				} else {
					loadingStatus("锁定失败!", 0);
				}
			})
		});
	});
	//退出锁定（不锁定）
	$("#bSuoding").click(function(event) {
		$("#suoding").dialog("close");
	});

	//重设锁屏密码
	$("#spshemi").click(function(event) {
		var session_id = $.cookie("session_id");
		var dev_id = $("#currentZh a img").attr('alt');
		var reg=/\d{4}/;
		if ($("#spxim").val() == '' || $("#qxspmi").val() == '') {
			loadingStatus("密码不能为空!", 0);
			return false;
		}
		if(!reg.test($("#spxim").val())||!reg.test($("#qxspmi").val())){
			loadingStatus("密码必须是四位数字!",0);
			return false;
		}
		if ($("#spxim").val() != $("#qxspmi").val()) {
			loadingStatus("您两次输入的密码不匹配!", 0);
			return false;
		}
		var pw = $("#qxspmi").val();
		var obj = {
			_path: '/a/wp/user/send_cmd',
			_methods: 'post',
			param: {
				sid: session_id,
				dev_id: dev_id,
				cmd: 'chg_screen_pw ' + pw
			}
		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				loadingStatus("更改锁屏密码成功!", 0);
			} else {
				loadingStatus("更改锁屏密码失败!", 0);
			}
		})
		$("#spmima").dialog("close"); //关闭窗口要在最后。
	});
	//关闭窗口时，清空数据
	$("#spmima").live('dialogclose', function(event) {
		$("#spxim").val("");
		$("#qxspmi").val("");
	})
	//重设个人密码
	$("#shemi").click(function(event) {
		event.preventDefault();
		var session_id = $.cookie("session_id");
		var jmm = $("#jmm").val();
		var xim = $("#xim").val();
		var qxim = $("#qxim").val();
		var re=/.{8,16}/;
		var wre=/[a-zA-Z]/;
		var cre=/[0-9]/;
		if (jmm == '' || xim == '' || qxim == '') {
			loadingStatus("密码不能为空!", 0);
			return false;
		}
		if (xim != qxim) {
			loadingStatus("确认密码不一致!", 0);
			return false;
		}
		if (!re.test(qxim)||!wre.test(qxim)||!cre.test(qxim)) {
			loadingStatus("密码必须是8-16位字母和非字母的组合!",0);
			return false;
		}
		var requestData = {
			jiumima: jmm,
			xinmima: xim,
			querenmima: qxim
		};
		var obj = {
			_path: '/a/wp/user/set_pw',
			_methods: 'post',
			param: {
				sid: session_id,
				oldpw: jmm,
				newpw: qxim
			}
		}
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				loadingStatus("更改个人密码成功!", 0);
			} else if (rt == 2||rt==19) {
				loadingStatus("更改个人密码失败：原密码错误!", 0);
			}else if(rt==18){
				loadingStatus("密码必须是8-16位字母和非字母的组合!",0);
			} else {
				loadingStatus("更改个人密码失败!", 0);
			}
		});
		$("#gaimi").dialog("close");
	});
	$("#gaimi").live("dialogclose", function(event) {
		$("#jmm").val("");
		$("#xim").val("");
		$("#qxim").val("");
	});
	$("#bpianhao").click(function(event) {
		event.preventDefault();
		loadingStatus("偏好设定正在建设!", 0);
		$("#pianhao").dialog("close");
	});
	//用户登出
	$("#dengchu").click(function(event) {
		event.preventDefault();
		var sid = $.cookie("session_id");
		var obj = {
			_path: '/a/wp/user/logout',
			_methods: 'post',
			param: {
				sid: sid
			}
		};
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt = data.rt;
			if (rt === 0) {
				$.cookie("session_id",null);
				location.href = '/f_per_login';
			} else {
				//console.log(errRt[rt]);
			}
		})
	});
	init();
	pwd.blur();
	//resetFields(document.getElementById('login'))
}); //ready事件到此结束
//获取设备列表。
var idArr = null;

function loadingStatus(state, sh) {
	var errTishi = $("#errTishi");
	if (errTishi.length == 0) { //如果不是在登陆页面，切换提示框
		errTishi = $("#loadingStatus");
	}
	if (idArr != null) {
		clearTimeout(idArr);
		idArr = null;
	}
	errTishi.html(state).fadeIn('fast');
	if (!sh) {
		idArr = setTimeout(hideLoad, 2000);
	}
	//console.log(state);
}

function hideLoad() {
	$("#loadingStatus").fadeOut('fast');
}

function dev_list() {
	var ssid = $.cookie("session_id");
	var obj = {
		_path: '/a/wp/user/get_devs',
		_methods: 'get',
		param: {
			sid: ssid
		}
	}
	//低级ajax同步获取设备列表。
	$.ajax({
		type: 'POST',
		url: '/f_login',
		data: obj,
		async: false,
		timeout: 1000, //同步的ajax设置超时没用。
		dataType: 'json',
		beforeSend: function() {
			loadingStatus("正在加载设备列表...", 1);
		},
		success: function(data) {
			var rt = data.rt;
			if (rt === 0) {
				var dev = data.devs;
				var len = dev.length;
				if (len > 0) {
					if(dev[0]['model_number']){
						$("#currentZh a span").html(dev[0]['model_number']);
					}else{
						$("#currentZh a span").html(dev[0]['dev_id']);
					}
					$("#currentZh a img").attr('alt',dev[0]['dev_id']);
					
				}
				if (len > 1) {
					var html = '<div id="altZh">';
					for (var i = 1; i < len; i++) //第一个为默认设备，第二个开始隐藏。
					{
						html += '<a><img src="images/user.png" alt='+dev[i]['dev_id']+' /><span>';
						if (dev[i]['model_number']) {
							html+=dev[i]['model_number'];
						}else{
							html+=dev[i]['dev_id'];
						}
						html += '</span>';
						html += '</a>'
					}
					html += '</div>';
					$("#zhangHu").append(html);
				}
				loadingStatus("加载设备列表成功。", 0);
			} else {
				loadingStatus("加载设备列表失败。", 0);
			}
		},
		//error: cuowu
		error: function(jqXHR, textStatus, errorThrown) {
			//errTishi.html("error:" + textStatus);
			switch (textStatus) {
				case "timeout":
					loadingStatus("请求超时!", 0);
					break;
				case "error":
				case null:
					loadingStatus("发生错误，请重试!", 0);
					break;
				case "notmodified":
					loadingStatus("notmodified.", 0);
					break;
				case "parsererror":
					loadingStatus("parsererror.", 0);
					break;
				default:
					loadingStatus("未知错误。", 0);
			}
		}
	});
}
//发送定位请求的功能函数。

function devPostion() {
	var ssid = $.cookie("session_id");
	var dev_id = $("#currentZh a img").attr('alt');
	var obj = {
		_path: '/a/wp/user/loc',
		_methods: 'get',
		param: {
			sid: ssid,
			dev_id: dev_id
		}
	};
	ajaxReq(obj, '/f_login', 15000, function(data) //发送定位请求数据。
	{
		var rt = data.rt;
		if (rt === 0) {
			try {
				markerArr[0].title = $("#currentZh a span").html();
				markerArr[0].content = "您的设备在此!";
				markerArr[0].point = {
					lot: parseFloat(data.lon),
					lat: parseFloat(data.lat)
				};
				addMarker();
				loadingStatus("更新设备位置成功。", 0);
			} catch (error) {

			}

		} else {
			loadingStatus("更新设备位置失败。", 0);
		}
	});
}
//取得账号。

function getAcc() {
	var sid = $.cookie("session_id");
	var obj = {
		_path: '/a/wp/user/get_acc_info',
		_methods: 'get',
		param: {
			sid: sid
		}
	};
	ajaxReq(obj, '/f_login', 15000, function(data) {
		var rt = data.rt;
		if (rt === 0) {
			var acc = data.uid;
			$("#zhanghao").html(acc);
		} else {
			loadingStatus("取得账号失败。", 0);
		}
	})
}
//获取设备信息（最后更新的时间）
var _s = 1000;
var _m = _s * 60;
var _h = _m * 60;
var _d = _h * 24;
var _mon = _d * 30;
var _y = _mon * 12;

function lastUpdateTime() {
	var sid = $.cookie("session_id");
	var dev_id = $("#currentZh a img").attr('alt');
	var obj = {
		_path: '/a/wp/user/get_dev_info',
		_methods: 'get',
		param: {
			sid: sid,
			dev_id: dev_id
		}
	};
	ajaxReq(obj, '/f_login', 15000, function(data) {
		var rt = data.rt;
		if (rt === 0) {
			var last_ms = parseInt(data.last_update);
			var last_time = new Date(last_ms*1000);
			var new_time = new Date();
			var qian_time = new_time - last_time;
			var show_time;
			if (qian_time / _y > 1) {
				show_time = parseInt(qian_time / _y) + "年前。"
			} else if (qian_time / _mon > 1) {
				show_time = parseInt(qian_time / _mon) + "月前。"
			} else if (qian_time / _d > 1) {
				show_time = parseInt(qian_time / _d) + "天前。"
			} else if (qian_time / _h > 1) {
				show_time = parseInt(qian_time / _h) + "小时前。"
			} else if (qian_time / _m > 1) {
				show_time = parseInt(qian_time / _m) + "分前。"
			} else if (qian_time / _s > 1) {
				show_time = parseInt(qian_time / _s) + "秒前。"
			} else {
				show_time = "1秒前。";
			}
			$("#update").html('上次更新时间: ' + show_time);
			loadingStatus("获得更新时间成功。", 0);
		} else {
			loadingStatus("获取设备最后登陆时间失败。", 0);
		}
	})
}
//抽象ajax请求函数

function ajaxReq(obj, url, time, func) //obj是要发送的数据  url是nodejs接受请求的路径 time是请求允许的时间
{
    time=60000;   //+++ 20150628
	$.ajax({
		async: true,
		timeout: time,
		type: "POST",
		url: url,
		data: obj,
		dataType: 'json',
		beforeSend: function(jqXHR) {
			loadingStatus('正在执行...', 1);
		},
		success: function(data) {
			var rt = data.rt;
			switch (rt) {
				//case 2:
				case 4:
				case 6:
				case 8:
					$.cookie("session_id",null);
					location.href = "/f_per_login";
					break;
				default:
					func(data);
			}
		},
		error: function(jqXHR, textStatus, errorThrown) {
			//console.log('解析对像:' + JSON.stringify(jqXHR));
			switch (textStatus) {
				case "timeout":
					loadingStatus("请求超时!", 0);
					break;
				case "error":
				case null:
					loadingStatus("发生错误，请重试!", 0);
					break;
				case "notmodified":
					loadingStatus("notmodified.", 0);
					break;
				case "parsererror":
					loadingStatus("parsererror.", 0);
					break;
				default:
					loadingStatus("未知错误。", 0);
			}
		}
	}); //首先调用的是beforesend，发生错误是是error然后是complete。
}
//出错时调用的函数

function cuowu(jqXHR, txtSt, errTh) {
	//jqXHR.status;	错误的代码。
	//jqXHR.responseText;	服务器返回的请求文本。
	var errTishi = $("#errTishi");
	errTishi.stop();
	errTishi.fadeIn('slow');
	switch (jqXHR.status) {
		case 400:
			errTishi.html("请求语法错误");
			break;
		case 401:
			errTishi.html("未授权");
			break;
		case 403:
			errTishi.html("禁止访问");
			break;
		case 404:
			errTishi.html("未发现请求的URL");
			break;
		case 500:
			errTishi.html("服务器内部错误");
			break;
		default:
			errTishi.html("未知错误");
	}
	//console.log('解析对像:' + JSON.stringify(jqXHR));
}
//手机在线状态

function findPhone() {
	var session_id = $.cookie("session_id");
	var span = $('#zhangHu img');
	span.each(function(index, element) {
		var dev_id = $(element).attr('alt');
		var obj = {
			_path: '/a/wp/user/get_online_status',
			_methods: 'get',
			param: {
				sid: session_id,
				dev_id: dev_id
			}
		}
		ajaxReq(obj, '/f_login', 15000, function(data) {
			var rt=data.rt;
			var status = data.status;
            var dev_sid = data.dev_sid;
            alert(dev_sid);
			var parent = $(element).parent();
			var img = $('img', parent);
			if (rt === 0 && status === 2) {
				img.attr('src', 'images/user_online.png');
			}else{
				img.attr('src','images/user.png');
			}
		})
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
	ajaxReq(obj, '/f_login', 15000, function(data) {
		var rt = data.rt;
		var status = data.status;
		if (rt === 0 && status === 2) {
			func();
		} else {
			loadingStatus('用户不在线,执行不可操作!', 0);
		}
	})
}
//获取验证码
function getVer(){
	var obj={
		_path:'/a/wp/caps/get',
		_methods:'get',
		param:{

		}
	}
	$.post('/f_login',obj,function(data){
		var rt=data.rt;
		if(rt==0){
			var src='data:image/jpg;base64,'+data.img_data_b64;
			$("#yanz").attr('src',src);
			$("#yanz").attr('alt',data.cid);
		}
	},'json').error(function(jqXHR){
		//console.log(jqXHR)
	});
	return false;
}
getVer();
//placeholder检测
function resetFields(whichform) {
  if (Modernizr.input.placeholder) return;
  for (var i=0; i<whichform.elements.length; i++) {
    var element = whichform.elements[i];
    if (element.type == "submit") continue;
    if (!element.getAttribute('placeholder')) continue;
    element.onfocus = function() {
    if (this.value == this.getAttribute('placeholder')) {
      this.value = "";
      this.className='';
     }
    }
    element.onblur = function() {
      if (this.value == "") {
        this.value = this.getAttribute('placeholder');
        this.className='placeholder';
      }
    }
    element.blur();
  }
}
//初始化设备管理页面

function init_device() {
	dev_list(); //初始化管理设备页面的时候要获得设备列表
	getAcc();
	lastUpdateTime();
	devPostion(); //初始化管理设备页面的时候要获得设备的位置
	findPhone(); //看手机在线状态。
}
//初始化app页面

function init_app() {
	
}
//初始化详细资料页面

function init_details() {
	//alert('init_details');
}
//初始化网络流量页面

function init_network_flow() {
	//alert('init_network_flow');
}
//根据不同的url初始化不同的页面。

function init() {
	var href = location.href;
	if (href.indexOf('device') > 0) {
		init_device();
	} else if (href.indexOf('app') > 0) {
		init_app();
	} else if (href.indexOf('details') > 0) {
		init_details();
	} else if (href.indexOf('network_flow') > 0) {
		init_network_flow();
	}
};