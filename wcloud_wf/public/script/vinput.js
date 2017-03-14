var selectObj=function(){
	var select=$(".select");		//容器。
	var option=$(".select .option");	//选项。
	select.live("click",function(event){
		var that=$(this);
		if(that.hasClass("select_disabled")) return false;
		var ul=$("ul",this);
		ul.slideDown("fast");
	});
	select.live("mouseleave",function(event){
		var ul=$("ul",this);
		ul.slideUp("fast");
	});
	option.live("click",function(event){
		var val=$(this).html();
		var id=$(this).attr("href");
		$(id).html(val);
		$(this).parent().parent().slideUp("fast");
		return false;
	});

}
/*
*selectObj 使用方法
*HTML结构
<div class="select">	给定div容器类名 select
	<p id="cname">选中的</p>	
	<ul>
		<li><a href="#cname" class="option">选项</a></li>	//给定option类，href等于选中项的id
	</ul>
</div>
*最后调用selectObj方法即可。
*/
selectObj();

var jiaonang=function(){
	$(".jiaonang").live("click",function(event){
		var that=$(this);
		if(that.hasClass("jiaonang_disabled")) return false;
//        wifi_data(that);   //用于管控时的wifi和data不同时禁用
		if(that.hasClass("jiaonang_open")){
			that.removeClass("jiaonang_open").addClass("jiaonang_close");
		}else if(that.hasClass("jiaonang_close")){
			that.removeClass("jiaonang_close").addClass("jiaonang_open");
		}else{
            return
        }
	})
}
jiaonang();

function wifi_data(obj){
    if(obj.attr("id")=="wifiCon"){
        if(obj.attr("class")=="jiaonang jiaonang_open"){
            $("#mobiledataCon").removeClass().addClass("jiaonang jiaonang_disabled");
            $("#mobiledataCon").addClass("jiaonang_no");
        }else{
            $("#mobiledataCon").removeClass("jiaonang_no");
        }
    }
    if(obj.attr("id")=="mobiledataCon"){
        if(obj.attr("class")=="jiaonang jiaonang_open"){
            $("#wifiCon").removeClass().addClass("jiaonang jiaonang_disabled");
            $("#wifiCon").addClass("jiaonang_no");
        }else{
            $("#wifiCon").removeClass("jiaonang_no");
        }
    }
}

var radio=function(){
	$(".radio").live("click",function(event){
		var that=$(this);
		if(that.hasClass("radio_disabled")) return false;
		if(that.hasClass("radio_checked")){
			that.removeClass("radio_checked").addClass("radio_uncheck");
		}else if(that.hasClass("radio_uncheck")){
			that.removeClass("radio_uncheck").addClass("radio_checked");
		}
	})
}
radio();

var checkbox=function(){
	$(".checkbox").live("click",function(event){
		var that=$(this);
		if(that.hasClass("checkbox_disabled")) return false;
		if(that.hasClass("checkbox_checked")){
			that.removeClass("checkbox_checked").addClass("checkbox_uncheck");
		}else if(that.hasClass("checkbox_uncheck")){
			that.removeClass("checkbox_uncheck").addClass("checkbox_checked");
		}
	})
}
checkbox();
$(".lesAlt").live("click",function(event){
	var $wWidth=$(window).outerWidth(true);
	var $wHeight=$(window).outerHeight(true);
	var $cont=$(".lesCont")
	var $cWidth=$cont.outerWidth(true);
	var $cHeight=$cont.outerHeight(true);
	var to=($wHeight-$cHeight)/2;
	var lef=($wWidth-$cWidth)/2;
	$cont.css({top:to,left:lef});
	$cont.show();
	$(".overLay").show();
})
$(".lesClose").live("click",function(event){
	$(".lesCont").hide();
	$(".overLay").hide();
});