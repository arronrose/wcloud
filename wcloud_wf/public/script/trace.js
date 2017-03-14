/**
 * Created by Seren on 14-6-16.
 */
//选择需要查询轨迹的用户
$("#trace_user").click(function(event){
    //清除input中的数据
    $("#trace_search_content").val("");
    $("#search_user").val("");
    $("#search_pwd").val("");

    var href = "#selectuser_div";
    $("#select_user_a").attr("href",href);
    $("#select_user_a").click();
    loadtraceusers();

});
//搜索
$("#trace_search_Btn").click(function(event){
    var username = $("#trace_search_content").val();
//    alert(username);
    if (username==''){
        alert('请先输入查询内容！');
        return;
    }
    var element = document.getElementById("trace_tree_users");
    searchuser(username,element);
});

//确定 验证密码是否正确
$("#traceSub").click(function(event){
//    验证密码
    var password = $("#search_pwd").val();
    var userId = $("#search_user").val();
    if(userId==''||password == '')
    {
        alert("用户名或密码不能为空！");
        return;
    }
    else{
        var uid = $("#search_user").attr("class");
        var sid = $.cookie("org_session_id");
        $('#tr_user').attr('title',uid);
        var obj={
            _path:"/a/wp/org/checkpwd_and_devs",
            _methods:"get",
            param:{
                sid:sid,
                uid:uid,
                pwd:password
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            if(rt == 0)
            {
                loadingStatus("验证成功！",0);
                var dev = data.dev;
                $("#tr_devtype").html(dev);
                loadrecord(sid,uid,"","");
                $("#selectuser_div").dialog("close");
                //添加用户信息
                $("#tr_user").html($("#search_user").val());
                $("#tr_pnumber").html($("#search_user").attr('name'));
                //清除input中的数据
                $("#trace_search_content").val("");
                $("#search_user").val("");
                $("#search_pwd").val("");
            }
            else if(rt == 2){
//                loadingStatus("用户名或密码错误！",0);
                alert("用户名或密码错误!");
            }
            else if(rt == 41){
//                loadingStatus("用户未激活！",0);
                alert("用户未激活!");
            }
            else if(rt == 17){
//                loadingStatus("用户不存在！",0);
                alert("用户不存在!");
            }
        });
    }
})
//取消 关闭窗口
$("#traceExit").click(function(event){
    $("#selectuser_div").dialog("close");
    //清除input中的数据
    $("#trace_search_content").val("");
    $("#search_user").val("");
    $("#search_pwd").val("");
})
//时间条件搜索
$("#tr_search").click(function(event){
    var uid = $('#tr_user').attr('title');
    var username = $('#tr_user').text();
//alert(username);
    if(username =="")
    {
        alert("请先选择追踪用户！");
        return;
    }
    var span = $("#tr_selectall");  //获取全选的checkbox
    span.removeClass("checkbox_checked").addClass("checkbox_uncheck");
    var sid = $.cookie("org_session_id");
    var start = $('#tr_starttime').val();
    var end = $('#tr_endtime').val();
    //+++ 20150605 判定开始时间
    if(start){
        var str=start.replace(/-/g,'/'); //将2014-06-16 08:00 转化为2014/06/16 08:00
        var date=new Date(str);     //构造一个日期型数据  输入格式必须是2014/06/16 08:00
        var endt = date.getTime();  //获取date的ms数
        var jutime=(parseInt(endt)>100);
        if(! jutime){
            alert("您输入的开始时间有误，请重新输入！");
            return;
        }
    }else{
        alert("请输入开始时间！")
        return;
    }
    //+++ 20150605 判定结束时间是否有效
    if(end){
        var str2=end.replace(/-/g,'/'); //将2014-06-16 08:00 转化为2014/06/16 08:00
        var date2=new Date(str2);     //构造一个日期型数据  输入格式必须是2014/06/16 08:00
        var endtt = date2.getTime();  //获取date的ms数
        var qian_time2 = endtt - endt;
        var jutime2=(parseInt(endtt)>100);
        if(! jutime2){
            alert("您输入的结束时间有误，请重新输入！");
            return;
        }
        if (qian_time2<0)
        {
            alert("查询时间区间无效，请重新输入！");
            return;
        }
    }else{
        alert("请输入结束时间！")
        return;
    }

    loadrecord(sid,uid,start,end)
})

//点击table中每行时触发动作
$("#tulb tbody tr").live("click",function(event){
    event.preventDefault();
    //    获取checkbox的span元素
    var cb = this.getElementsByTagName("span")[0];
//    alert(span.className);
    //    加载坐标

    if(cb.className == "checkbox checkbox_checked"){
        cb.className = "checkbox checkbox_uncheck";
        getcheckedpoint();
    }
    else {
        getcheckedpoint();
        cb.className = "checkbox checkbox_checked";
        //添加被点击时间的坐标
        var lon = $(".lon",$(this)).html();
        var lat = $(".lat",$(this)).html();
        var k = $(".number",$(this)).html();
        var recordtime = $(".recordtime",$(this)).html();
        tracemarkers.push({title:"坐标"+k,content:recordtime,point:{"lon":lon,"lat":lat},isOpen:1,icon:{w:21,h:21,l:0,t:0,x:6,lb:5}});
    }

//在地图上添加maker
    addmakertomap(tracemarkers);
    tracemap.centerAndZoom(new BMap.Point(lon,lat),15);

})

function loadrecord(sid,uid,start,end){
    var obj={
        _path:"/a/wp/org/trace_loc_info",
        _methods:"get",
        param:{
            sid: sid,
            start: start,
            end: end,
            uid:uid
        }
    };

    ajaxReq(obj,function(data){
        var rt = data.rt;
//        alert(rt);
        if(rt == 0){

            var locinfo = data.locinfo;
//            alert(JSON.stringify(locinfo));
            var html="";

            for(var i = 0;i<locinfo.length;i++)
            {
                //将时间戳转换为字符串的形式%Y-%m-%d %H:%M
                var  recordtime = formatdate(locinfo[i][0]);
                var info = locinfo[i][1].split(':');
                var lon = info[0];
                var lat = info[1];
                var status="";
                if (info[2]=="online")
                    status = "在线";
                else
                    status = "离线";
                var k=i+1;
//                只显示定位有效的数据
//                alert(parseFloat(lon));
                if(parseFloat(lon)>0.0&&parseFloat(lat)>0.0)
                {
                    html+='<tr class="'+recordtime+'">';
                    html+='<td><span class="checkbox checkbox_uncheck" onclick="loadmarkers(this)"></span></td>';
                    html+='<td class="number">'+k+'</td>';
                    html+='<td class="recordtime">'+recordtime+'</td>';
                    html+='<td class="status">'+status+'</td>';
                    html+='<td class="lon">'+lon+'</td>';
                    html+='<td class="lat">'+lat+'</td></tr>';
                }
            }

            $("#tulb tbody").html("");  //每次显示之前先清空
            $("#tulb tbody").append(html);
            $("#trace_list_b").mCustomScrollbar("update");
        }

    });
}
//搜索用户
function searchuser(username,element){
        element.innerHTML='';
        loadtraceusers();
        //取到用户输入的数据，去遍历整个contacts_list容器中的所有a
        var a_list = element.getElementsByTagName("a");
        setTimeout(function(){for(var i=0;i<a_list.length;i++){
            var a = a_list[i];
            if(a.innerHTML==username){

                var name = a.name;
                var type = name.substring(0,2);
                //以上获取了找到的a的name和类型，只要根据类型进行操作即可
                var parent = a.parentNode;
                while(parent.tagName!='FORM'){

                    parent.style.display='block';
                    parent = parent.parentNode;
                }
                a.style.color= '#ff0402';
            }
        }},50);
}
function loadtraceusers(){
    var html = "";//初始化要加入的html
    var obj={
        _path:"/a/wp/org/ldap_tree",
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
            loadlist(all,1);
            loadingStatus("成功获取用户信息！", 0);
            $("#trace_tree_users").html("");
            $("#trace_tree_users").append(html);	//添加一个账户
            $("#trace_tree").mCustomScrollbar("update");
        }
    },"正在获取用户信息!");

    loadLogo();
    //加入count变量用来记录现在群组的层级,20150829改，确定递归层级
    function loadlist(all,count){
        var dn = all['dn'];
        var ou = all['ou'];
        if(ou!='admin'){
            //每一个群组要进行的操作
            html+='<div style="margin:0px;cursor:pointer;border:1px solid #f2f2f2;background:#ededed;height:32px" style=" overflow: hidden !important">';
            html+='<img src="images/group.png"/>';
//            show(this.title)函数在login_ad.js中是一个公共方法，控制div的显示和隐藏
            html+='<a name="out:'+dn+'"href="javascript:;" title="t'+dn+'" onclick="show(this.title)">';
            html+= ou;
            html+='</a>';
            html+='</div>';
        }
        var ous = all['ous'];
        var users = all['users'];
        //当第三层群组时，群组默认闭合
        if(count<=1){
            html+='<div style="margin:0px;display:block;overflow: hidden !important;border:1px solid #ffffff;background:#ffffff;" id="t'+dn+'">';
        }else{
            html+='<div style="margin:0px;display:none;overflow: hidden !important" id="t'+dn+'">';
        }
        for(var j=0;j<users.length;j++){
            html+='<li style="height: 30px" title="'+users[j]['uid']+'">';
//            html+='<span title="'+users[j]['uid']+'" id="'+"ust:"+users[j]['dn']+'"class="checkbox checkbox_uncheck" onclick="showcontacts(this,this.title,this.id)"></span>';
            //这里的id是为了寻找span,class是控制前面的checkbox
            html+='<img src="images/unline.png"/>';
            html+='<a class="'+users[j]['job']+":"+users[j]['pnumber']+'"name="'+"ust:"+users[j]['dn']+'" title="'+users[j]['uid']+'" href="javascript:;" onclick="selectuser(this)">';
            //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
            html+=users[j]['username'];
            html+='</a>';
            html+='</li>';
        }

        for(var i=0;i<ous.length;i++){
            loadlist(ous[i],count+1);
        }
        html+='</div>';

    }
}
//全选/全不选
//地图标签
tracemarkers=[];//{title=k+1,content=recordtime point:{lot:116.498515,lat:39.269008},isOpen:1,icon:{w:21,h:21,l:0,t:0,x:6,lb:5}}
tracepoints = [];
function tr_selectAll(id){
//    alert("tr_selectAll");
    var span = document.getElementById(id);
    if(span.className=='checkbox checkbox_uncheck'){
        $("#tulb tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
    }
    else{
        $("#tulb tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    }
//    加载坐标

    getcheckedpoint();
    //在地图上添加maker
    addmakertomap(tracemarkers);
}
function loadmarkers(Element){
    getcheckedpoint();
    //如果点击的是span checkbox  则  如果该checkbox现在的状态是未选中则在坐标集合中加入该坐标，反之则删除
    var parentarr = $(Element).parent().parent(); //获取span 所在行的tr元素
    if(Element.tagName == "SPAN" && Element.className == "checkbox checkbox_uncheck")
    {
        Element.className= "checkbox checkbox_checked";
        var recordtime = $(".recordtime",parentarr).html();
        var lon = $(".lon",parentarr).html();
        var lat = $(".lat",parentarr).html();
        var k = tracemarkers.length;
        tracemarkers.push({title:"坐标"+k,content:recordtime,point:{"lon":lon,"lat":lat},isOpen:1,icon:{w:21,h:21,l:0,t:0,x:6,lb:5}});
    }
    else if(Element.tagName == "SPAN" && Element.className == "checkbox checkbox_checked")
    {
        Element.className= "checkbox checkbox_uncheck";
        var recordtime = $(".recordtime",parentarr).html();
        for(var i =0;i<tracemarkers.length;i++){
            if(tracemarkers[i].content == recordtime){
                tracemarkers.splice(i,1);
                break;
            }
        }
    }

    //在地图上添加maker
    addmakertomap(tracemarkers);
}
//获取勾选的坐标集合
function getcheckedpoint(){
    //每次数据之前先清空tracemakers
    tracemarkers.splice(0,tracemarkers.length);
    $("#tulb tbody tr .checkbox_checked").each(function(index,element){
        var tr = $(element).parent().parent();  //获取每一行的tr元素 即坐标
        var recordtime = $(".recordtime",tr).html();
        var lon = $(".lon",tr).html();
        var lat = $(".lat",tr).html();
        var k = $(".number",tr).html();

        tracemarkers.push({title:"坐标"+k,content:recordtime,point:{"lon":lon,"lat":lat},isOpen:1,icon:{w:21,h:21,l:0,t:0,x:6,lb:5}});
        tracepoints.push(new BMap.Point(lon,lat));
    });
}
//将坐标集合在地图上显示
function addmakertomap(arrmakers){
    //每次加载之前先将地图上的maker全部清除
    tracemap.clearOverlays();
    //加载坐标
    for(var i=0;i<arrmakers.length;i++){
        var json = arrmakers[i];
        var p0 = json.point.lon;
        var p1 = json.point.lat;
        var point = new BMap.Point(p0,p1);
        var iconImg = createIcon(json.icon);
        var marker = new BMap.Marker(point,{icon:iconImg});
//        var iw = createInfoWindow(i);
        var label = new BMap.Label(json.title,{"offset":new BMap.Size(json.icon.lb-json.icon.x+10,-20)});
        marker.setLabel(label);
        tracemap.panTo(point);       //添加标记之后，视图跳转（point中心点）
        tracemap.addOverlay(marker);
        label.setStyle({
            borderColor:"#808080",
            color:"#333",
            cursor:"pointer"
        });

        (function(){
//            var index = i;
            var _iw = createInfoWindow(json);
//            alert(arrmakers.length);
            var _marker = marker;
            _marker.addEventListener("click",function(){
                this.openInfoWindow(_iw);
            });
            _iw.addEventListener("open",function(){
                _marker.getLabel().hide();
            })
            _iw.addEventListener("close",function(){
                _marker.getLabel().show();
            })
            label.addEventListener("click",function(){
                _marker.openInfoWindow(_iw);
            })
            if(!!json.isOpen){
                label.show();
                _marker.openInfoWindow(_iw);
            }
        })()
    }
}
//点击列表中的用户将该用户姓名打到下面的用户名输入框中
function selectuser(elemet){
    $("#search_user").val(elemet.innerHTML);
    $("#search_user").attr('class',elemet.title);
    var pnumber = elemet.className.split(':')[1];
    $("#search_user").attr('name',pnumber);

}
//将时间戳转化为时间格式为%Y-%m-%d %HH:%MM
function formatdate(date){
//    var recordtime = locinfo[i][0];
    var dt = new Date(parseInt(date)*1000);
    var year = dt.getFullYear();
    var mouth = "00"+(dt.getMonth()+1);
    var day = "00"+dt.getDate();
    var minute = "00"+ dt.getMinutes();
    var hour =  "00"+dt.getHours();
    var str = year+"-"+mouth.substr(-2)+"-"+day.substr(-2)+" "+hour.substr(-2)+":"+minute.substr(-2);
    return str;
}

