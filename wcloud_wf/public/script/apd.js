var appCont=$("#appB");
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
		if(data.rt==0){
			var applist=data.applist;
			for(var i=0,len=applist.length;i<len;i++){
				paddingCont(applist[i]);
			}
		}
	});
}
loadAppId();
function paddingCont(appId){
	var obj={
		_path:"/a/was/appinfo",
		_methods:"get",
		param:{
			app_id:appId
		}
	};
	ajaxReq(obj,function(data){
		if(data.rt==0){
			var appinfo=data.appinfo;
            var updatetime=data.updatetime;
            var versionCode = appinfo['versionCode'];
			var send='',type='',update='';
            send='<button id="'+appId+','+versionCode+'" style="padding-left:4px;padding-right:4px;margin:0px;font: 16px/1.5em 微软雅黑" class="send">下发应用</button>';
            update='<button style="padding-left:4px;padding-right:4px;margin:0px;font: 16px/1.5em 微软雅黑" class="letb">应用升级</button>';
            if(appinfo['apptype']=="workapp"){
				type="移动办公";
			}else if(appinfo['apptype']=="communicate"){
				type="社交通讯";
            }else if(appinfo['apptype']=="safeapp"){
                type="安全套件";
            }else if(appinfo['apptype']=="systemapp"){
                type="系统工具";
            }else{
				return false;
			}
            //更新时间
            var ltime=updatetime['year']+'-'+updatetime['month']+'-'+updatetime['day'];
			var str='';
			str+='<tr class="'+appinfo['app_id']+','+appinfo['versionCode']+'"><td><span name="'+appinfo['app_id']+','+appinfo['versionCode']+'"class="checkbox checkbox_uncheck"></span></td>';
			str+='<td class="appName">';
			str+=appinfo['app_name']||"";
			str+='</td><td>';
			str+=appinfo['version']||"";
			str+='</td><td>';
			str+=type;
			str+='</td><td class="scu">';
			str+=ltime||"";
			str+='</td><td class="mak">';
			str+=appinfo['remark']||"";
            str+='</td><td>';
			str+='</td><td>';
			str+=send;
            str+='</td><td>';
            str+=update;
			str+='</td></tr>';
			$("tbody",appCont).append(str);
			appCont.mCustomScrollbar("update");
		}
	})
}
$("#appxz").click(function(event){
	$("tbody tr .checkbox",appCont).removeClass("checkbox_uncheck").addClass("checkbox_checked");
});
$("#appkc").click(function(event){
	$("tbody tr .checkbox",appCont).removeClass("checkbox_checked").addClass("checkbox_uncheck");
});
$(".letb").live('click',function(event){
	event.preventDefault();
	$("#upApp")[0].reset();
	var left=($(window).outerWidth(true)-$(".cppUp").outerWidth(true))/2;
	var top=($(window).outerHeight(true)-$(".cppUp").outerHeight(true))/2;
	$(".cppUp").css({left:left,top:top});
	$("#lestou").html("新增企业应用");
	$(".cppUp").show();
	$("#lesTy").val("add");
});
$(".letb",appCont).live('click',function(event){
	event.preventDefault();
	$("#upApp")[0].reset();
	var parent=$(this).parent().parent();		//tr
	var left=($(window).outerWidth(true)-$(".cppUp").outerWidth(true))/2;
	var top=($(window).outerHeight(true)-$(".cppUp").outerHeight(true))/2;
	$(".cppUp").css({left:left,top:top});
	$("#lestou").html("应用升级");
	$("#lesTy").val("update");
	$(".cppUp").show();
	$("#appName").val($(".appName",parent).html()).attr("readonly","readonly");
	$("#appSocu").val($(".scu",parent).html()).attr("readonly","readonly");
	$("#lei #lesnat").attr("selected","selected");
	$("#lei").change();
	$("#lei").attr("disabled",true);
});
$(".cppUp .x").click(function(event){
	$(".cppUp").hide();
	$("#appName").attr("readonly",null);
	$("#appSocu").attr("readonly",null);
	$("#lei").attr("disabled",false);
	$(".wb").hide();
	$(".nat").show();
});
$(".cppUp .err").click(function(event){
	$(".cppUp .x").click();
});
/*$("#lei").change(function(event){
	var val=$("#lei option:selected").val();
	if(val=="web"){
		$(".wb").show();
		$(".nat").hide();
		$(".nat input").val("");
	}else if(val=="native"){
		$(".wb").hide();
		$(".wb input").val("");
		$(".nat").show();
	}
});*/
$("#upApp").submit(function(event){
	var val=$("#lei option:selected").val();
    if(!$("#apks").val()){
        loadingStatus("上传文件不能为空!",0);
        return false;
    }
    var apkname =$("#apks").val();
//    var apkmode =/\.[^\.]+/.exec(apkname);
    var apkmode=apkname.toLowerCase().substr(apkname.lastIndexOf("."));
    if(apkmode != '.apk' && apkmode != '.sop'){
        alert('上传文件格式不对，请重新上传apk/sop格式的文件!');
        return false;
    }

	loadingStatus("正在上传...",1);
	$(".cppUp .x").click();
	$("#lei").attr("disabled",false);
    diswles();		//禁用上传的按钮；
});
//禁用上传按钮
var wles=$("#wles")
function diswles(){
    wles.attr({"disabled":"disabled"});
    wles.live('click',lesalert);
}
//释放上传按钮
function abwles(){
    wles.removeAttr("disabled");
    wles.die('click',lesalert);
}
function lesalert(event){
    alert("有一个应用正在上传，请稍侯...");
}
$("#apks").focus(function(event){
	$("#apll").click();
});
$("#apll").change(function(event){
	$("#apks").val($(this).val());
});
function waitL(data){
    abwles();		//释放上传的按钮！
    var rt=data.rt;
    if(rt==0){
        loadingStatus("应用上传成功！",0);
        alert("应用上传成功！");
        if(data['app_id']){
            paddingCont(data['app_id']);
        }
    }else{
        loadingStatus("应用上传失败！",0);
        alert("应用上传失败！");
    }
}

//$("#shanchu").click(function(event){
//    if ($("#appTb tbody tr .checkbox_checked").length<1){
//        alert("请先选择需要删除的应用！");
//        return false;
//    }
//	event.preventDefault();
//	$("tbody tr .checkbox_checked",appCont).each(function(index,element){
//		var that=$(element).parent().parent();
//		var appId=that.attr("class").split(",")[0];
//		var obj={
//			_path:"/a/was/del_app",
//			_methods:"post",
//			param:{
//				app_id:appId
//			}
//		};
//		(function(that){
//			ajaxReq(obj,function(data){
//				var rt=data.rt;
//				if(rt==0){
//					loadingStatus("删除成功!",0);
//					that.remove();
//				}else{
//					loadingStatus("删除失败!",0);
//				}
//			},"正在删除...")
//		})(that);
//	});
//});
$("#appgu").live("keyup",function(event){
	var value=$(this).val();
	if(!!value){
		$("tbody tr",appCont).hide();
		$("tbody tr",appCont).each(function(index,element){
			var trText=$(element).text();
			if(trText.indexOf(value)>-1){
				$(element).show();
			}
		})
	}else{
		$("tbody tr",appCont).show();
	}
})

$("#app #sendapps").live('click',function(event){
    if($("#yic .checkbox_checked").length==0){
        alert("请在左边用户列表选取用户！！");
    }else if($("#appTb tbody tr .checkbox_checked").length==0){
        alert("请在列表中选择要推送的应用！！");
    }else{

    var app_ids=[];
    $("#appTb tbody tr .checkbox_checked").each(function(index,element){
        var app_id = element.parentNode.parentNode.className;
        app_ids.push(app_id);
    });
//    for(var i=0;i<app_ids.length;i++){
//        var app_id = '';
//        var versionCode = '';
//        app_id = app_ids[i].split(",")[0];
//        versionCode = app_ids[i].split(",")[1];
//        sendApp(app_id,versionCode);
//    }
    sendApp(app_ids);
    }
});

$(".send").live('click',function(event){
    if($("#yic .checkbox_checked").length==0){
        alert("请在左边用户列表选取用户！！");
    }else{
        var app_id=event.target.id;
        var app_ids = [];
        app_ids.push(app_id);
        sendApp(app_ids);
    }
});


function sendApp(app_ids){
    var users = [];
    var nodes = $("#yic .checkbox_checked");
    for (var i=0;i<nodes.length;i++){
        if(nodes[i].title)
        {
            users.push(nodes[i].title);
        }
    }
    //+++20150824从后台获取选中的用户
    users = JSON.stringify([]);
    app_ids = JSON.stringify(app_ids)
    var obj={
        _path:"/a/was/send_app",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            app_ids:app_ids,
            users:users
        }
    };
    ajaxReq(obj,function(data){
        var rt=data.rt;
        if(rt == 0)
        {
            loadingStatus("推送应用成功!",0);
            alert("推送应用指令已成功下发，请确保手机在线，从而下载并安装应用程序。");

        }else{
            loadingStatus("推送应用失败!",0);
            alert("网络异常，请重试！");
        }
    },"正在推送应用...");
}

//function sendApp(app_id,versionCode){
//    var users = [];
//    var nodes = $("#yic .checkbox_checked");
//    for (var i=0;i<nodes.length;i++){
//        if(nodes[i].title)
//        {
//            users.push(nodes[i].title);
//        }
//    }
//    users = JSON.stringify(users);
//    var obj={
//        _path:"/a/was/send_app",
//        _methods:"post",
//        param:{
//            sid:$.cookie("org_session_id"),
//            app_id:app_id,
//            versionCode:versionCode,
//            users:users
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt=data.rt;
//        if(rt == 0)
//        {
//            loadingStatus("推送应用成功!",0);
//
//        }else{
//            loadingStatus("推送应用失败!",0);
//        }
//    },"正在推送应用...");
//}

//+++20150428
function delapp(){
    if ($("#appTb tbody tr .checkbox_checked").length<1){
        alert("请先选择需要删除的应用！");
        return false;
    }
    if(confirm("该操作将会删除您所选应用，确定继续删除？")){
        event.preventDefault();
        $("tbody tr .checkbox_checked",appCont).each(function(index,element){
            var that=$(element).parent().parent();
            var appId=that.attr("class").split(",")[0];
            var obj={
                _path:"/a/was/del_app",
                _methods:"post",
                param:{
                    app_id:appId
                }
            };
            (function(that){
                ajaxReq(obj,function(data){
                    var rt=data.rt;
                    if(rt==0){
                        loadingStatus("删除成功!",0);
                        alert("删除成功!");
                        that.remove();
                    }else{
                        loadingStatus("删除失败!",0);
                        alert("删除失败!");
                    }
                },"正在删除...")
            })(that);
        });
    }
}