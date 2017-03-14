var pInfo=[
	{
		title:'1. WorkPhone版本',
		firmware_version : "固件版本",
		model_number : "型号号码",
		version_number : "版本号码",
	},
	{
		title:'2. 电话通讯',
		imei : "IMEI",
		imei_version : "IMEI软件版本",
		sim_supplier : "SIM供应商",
		sim_sn : "SIM序列号",
		sim_state : "SIM插入状态",
		signal_strength : "信号强度",
		network_providers : "网络供应商",
		network_type : "网络类型",
		phone_type : "手机类型（手机制式）",
		call_status : "通话状态",
	},
	{
		title:'3. 无线网络',
		wifi_bssid : "WIFI BSSID",
		wifi_ip_addr : "WIFI IP地址",
		wifi_mac_addr : "WIFI MAC地址",
		wifi_rssi : "WIFI RSSI",
		wifi_ssid : "WIFI SSID",
		wifi_network_id : "WIFI 网络id",
		wifi_request_status : "WIFI 请求状态",
		wifi_conn_speed : "WIFI 连接速度"
	},
	{
		title:'4. 蓝牙',
		bluetooth_is_on : "蓝牙是否打开",
		bluetooth_is_search : "蓝牙是否搜索中",
		bluetooth_name : "蓝牙名称",
		bluetooth_addr : "蓝牙地址",
		bluetooth_status : "蓝牙状态",
		bluetooth_pair_dev : "蓝牙配对设备"
	},
	{
		title:'5. 电源',
		battery_status : "电池状态",
		battery_power : "现时电量",
		battery_voltage : "电压",
		battery_temperature : "电池温度",
		battery_technology : "电池技术",
		battery_life : "电池寿命"
	},
	{
		title:'6. 网络',
		data_activity_status : "数据活动状态",
		data_conn_status : "数据连接状态"
	},
	{
		title:'7. 音响',
		call_volume : "通话音量",
		system_volume : "系统音量",
		ring_volume : "铃声音量",
		music_volume : "音乐音量",
		tip_sound_volume : "提示声音音量"
	},
	{
		title:'8. 位置',
		longitude : "经度",
		latitude : "纬度",
		pos_corrention_time : "位置修正时间"
	}
];
function loadDetails(){
	var session_id=$.cookie("session_id");
	var dev_id = $("#currentZh a img").attr('alt');
	var obj={
		_path: '/a/wp/user/dev_static_info',
		_methods: 'get',
		param: {
			sid: session_id,
			dev_id:dev_id,
			all: 1
		}
	}
	ajaxReq(obj,'/f_login',15000,function(data){
		var rt=data.rt;
		if(rt==0){
			loadingStatus('成功取得手机详细信息!',0);
			var str='';		//定义要添加的每个h3；
			var cName='';
			var cSub='';
			var cNameP='';		//定义一个classnamep，方便查找list p
			var dd='';			//遍历每一项，创建字符串
			for(var i=0,len=pInfo.length;i<len;i++){
				str+='<div class="zj '+'list_'+i+'"><h3>'
				str+=pInfo[i].title;
				str+='</h3><div class="list_sub_'+i+'"></div></div>';
			}
			$("#details").html($(str));	//遍历信息，添加title
			for(var t in data){		//访问data的每一项
				for(var k=0;k<pInfo.length;k++){	//访问pinfo的每一项
					if(t in pInfo[k]){			//确定要添加的元素属于哪一项
						cName='.list_'+k;
						cSub='.list_sub_'+k;
						cNameP='.list_sub_'+k+' p';
						if($(cNameP).length==0||$('span',$(cNameP)[$(cNameP).length-1]).length>=3){
						//当没有p标签，或者最后一个p标签span的数量为三个的时候，新增一个p标签。
							dd+='<p><span>';
							dd+=pInfo[k][t];
							dd+=': ';
							dd+=data[t];
							dd+='</span></p>'
							$(cSub).append($(dd));
							dd='';		//添加完成后清空。
							$(cNameP+':even').addClass('alt');
						}else{
						//如果不是，那就直接向最后一个p中增加span
							dd+='<span>';
							dd+=pInfo[k][t];
							dd+=': ';
							dd+=data[t];
							dd+='</span>';
							$($(cNameP)[$(cNameP).length-1]).append($(dd));
							dd='';
						}
						break;			//确定添加完之后，跳出循环。
					}
				}
			}
		}else{
			loadingStatus('未能获得手机详细信息!',0);
			
		}

	})
}
$("#details .zj h3").live('click',function(event){	//注册h3标头的事件
	var target=$(event.target)
	var targetNext=target.next();
	if(targetNext.is(':hidden')){
		targetNext.slideDown('fast');
		target.removeClass('Halt');
	}else{
		targetNext.slideUp('fast');
		target.addClass('Halt');
	}
});
$("#infoBtn a").live('click',function(event){		//注册展开和收缩按钮的事件
	var classN=$(event.target).attr('class');
	if(classN=='show'){
		$(".zj div").slideDown('fast');
		$(".zj h3").removeClass('Halt');
	}else if(classN=='hide'){
		$(".zj div").slideUp('fast');
		$(".zj h3").addClass('Halt');
	}
});
function loadApp(){
	var session_id=$.cookie("session_id");
	var dev_id = $("#currentZh a img").attr('alt');
	var obj={
		_path: '/a/wp/user/dev_app_info',
		_methods: 'get',
		param: {
			sid: session_id,
			dev_id:dev_id
		}
	}
	ajaxReq(obj,'/f_login',15000,function(data){
		var rt=data.rt;
		if(rt==0){
			loadingStatus('成功取得手机应用信息!',0);
			var appLen;
			if(!data.apps){
				appLen=0;
			}else{
				var apps=JSON.parse(data.apps);
				appLen=apps.length;
			}
			var tableHtml='<table><thead><tr><th></th><th>应用名</th><th>版本号</th><th>build号</th><th>最后更新时间</th></tr></thead><tbody>';
			var lt=appLen>17? data['apps'].length:17;
			for(var i=0;i<lt;i++){
				tableHtml+='<tr><td></td><td></td><td></td><td></td><td></td></tr>';
			}
			tableHtml+='</tbody></table>';
			$("#app").html(tableHtml);
			$("#app table tbody tr:even").addClass('hbg');

			for(var x=0/*apps=data['apps'],*/;x<appLen;x++){
				var icon=apps[x]['icon'];
				var img=$('<img src="data:image/png;base64,'+icon+'" width="26" alt="" />');
				var app_name=apps[x]['app_name'];
				var last_update_time=parseInt(apps[x]['last_update_time']);
				var last_time=new Date(last_update_time);
				var mn=last_time.getMonth()+1;
				last_update_time=last_time.getFullYear()+'-'+mn+'-'+last_time.getDate();
				var version_code=apps[x]['version_code'];
				var version_name=apps[x]['version_name'];
				var tr=$("#app table tbody tr")[x];
				$($("td",tr)[0]).append(img);
				$($("td",tr)[1]).text(app_name);
				$($("td",tr)[2]).text(version_name);
				$($("td",tr)[3]).text(version_code);
				$($("td",tr)[4]).text(last_update_time);
			}
		}else{
			loadingStatus('未能获得手机应用信息!',0);	
		}

	});
}