/**
 * Created by GCY on 2015/11/6.
 */
var logs_per_page = 50;
//+++20151109 页面元素加载完毕时需要完成的事
$(document).ready(function(event){
    set_log_count("all");
    $(".jscroll").mCustomScrollbar();
    load_logs("all",1);//默认获取第一页
});
//页面加载时需要执行的动作
$("#admin_id").html($.cookie("userid"));
$("#search").click(function(){
    clear_table();
    load_logs_by_input(1);
});
//+++20151127 加入一个判断当前加载的日志类型的函数，作为分发的出发点
function load_logs_by_input(page_index){
    var op_type = $("#op_type").val();
    switch(op_type){
        case "all":
            set_log_count("all");
            load_logs("all",page_index);
            break;
        case "contact":
            set_log_count("send contacts");
            load_logs("send contacts",page_index);
//            load_contacts_logs(1);//默认获取第一页
            break;
        case "login":
            set_log_count("login");
            load_logs("login",page_index);  //默认获取第一页
            break;
        case "strategy":
        case "cmd":
        case "app":
            break;
        default :
            return;
    }
}

//+++20151109 加入查看是否存在管理员的逻辑
$("#op_user").blur(function(event){
    if($("#op_user").val()!=""){
        var org_session_id = $.cookie("org_session_id");
        var obj = {
            _path:"/a/wp/org/is_has_admin",
            _methods:"post",
            param:{
                sid:org_session_id,
                adminID:$("#op_user").val()
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            if(rt==0){
                var result = data.result;
                if(parseInt(result)==0){
                    alert("不存在该管理员，请重新填写");
                    $("#op_user").val("");
                }
            }else{
                return;
            }
        });
    }
});
//+++20151110 获取日志数量信息
function set_log_count(action){
    var org_session_id = $.cookie("org_session_id");
    var op_user = $("#op_user").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    var obj = {
        _path:"/a/wp/org/get_user_log_count",
        _methods:"get",
        param:{
            sid:org_session_id,
            admin:op_user,
            action:action,
            start_time:start_time,
            end_time:end_time
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var logs_count = data.logs_count;
        if(rt==0){
            set_bottom(logs_count,logs_per_page);
        }
    },"");
}
//+++20151127 根据类型加载日志
function load_logs(action,page_index){
    var org_session_id = $.cookie("org_session_id");
    var op_user = $("#op_user").val();
    var start_time = $("#start_time").val();
    var end_time = $("#end_time").val();
    var obj = {
        _path:"/a/wp/org/get_web_logs",
        _methods:"get",
        param:{
            sid:org_session_id,
            admin:op_user,
            action:action,
            start_time:start_time,
            end_time:end_time,
            size:logs_per_page,
            page_index:page_index,

        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var logs = data.logs;
        if(rt==0){
            clear_table();
            loadingStatus("成功获取日志信息",0);
            show_logs(logs);
            //设定页数信息
            var page = 0;
            if(logs.length>0){
                page=page_index;
            }
            set_page(page);
        }else if(rt==7){
            loadingStatus("超出权限，只能查看同级权限管理员日志！！",0);
            $("#op_user").val("");
            reset_bottom();
        }
    },"正在获取联系人下发日志");
}
//页面上的序号，没有实际的意义
var index = 0;
//+++20151103 加载管理员日志
//function load_contacts_logs(page_index){
//    var org_session_id = $.cookie("org_session_id");
//    var op_user = $("#op_user").val();
//    var start_time = $("#start_time").val();
//    var end_time = $("#end_time").val();
//    var obj = {
//        _path:"/a/wp/org/get_send_contacts_logs",
//        _methods:"get",
//        param:{
//            sid:org_session_id,
//            admin:op_user,
//            start_time:start_time,
//            end_time:end_time,
//            size:logs_per_page,
//            page_index:page_index
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt = data.rt;
//        var logs = data.logs;
//        if(rt==0){
//            clear_table();
//            loadingStatus("成功获取日志信息",0);
//            show_logs(logs);
//            //设定页数信息
//            var page = 0;
//            if(logs.length>0){
//                page=page_index;
//            }
//            set_page(page);
//        }else if(rt==7){
//            loadingStatus("超出权限，只能查看同级权限管理员日志！！",0);
//            $("#op_user").val("");
//            reset_bottom();
//        }
//    },"正在获取联系人下发日志");
//}
//+++20151103
function show_logs(logs){
    index = 0;
    var txt="";
    for(var i=0;i<logs.length;i++){
        var log = logs[i];
        var action = log['action'];
        switch (action){
            case "send contacts":
                txt+=show_contacts_log(log);
                break;
            case "adminlogin":
                txt+=show_login_log(log);
        }

    }
    $("#log_bcol tbody").append(txt);
    $("#log_body").mCustomScrollbar("update");
}
/*显示联系人信息日志区域*/
//+++20151127 显示下发联系人日志
function show_contacts_log(log){
    var txt = "";
    var users = log['users'];
    //生成user的html
    var user_html = "";
    var final_result = 0;
    for(var j=0;j<users.length;j++){
        var uid = users[j]['uid'];
        var result = users[j]['result'];
        var username = users[j]['username'];
        if(result==0){
            result="已取到";
        }else{
            result="未响应";
            final_result = 1;
        }
        user_html+=username+":"+result+";  ";
        if((i+1)%15==0){
            user_html+="\n";
        }
    }
    //生成通讯录html
    var info = log['info'];
    var oudn = info['oudn'];
    var log_info_str = get_log_info_str(info);
    //解析结果
    if(final_result==0){
        final_result = "全部发送成功";
    }else{
        final_result = "部分用户未响应";
    }
    txt += '<tr>';
    txt += '<td>' + log['uid'] + '</td>';
    txt += '<td>' + "同步联系人" + '</td>';
    txt += '<td>' + log['time']+ '</td>';
    txt += '<td><a title="点击查看作用用户" onclick="show_log_user(this)" style="text-decoration: underline" value="'+user_html+'">'
        + users.length+"人" + '</a></td>';
    txt += '<td><a title="点击查看通讯录内容" onclick="show_log_contacts(this)" style="text-decoration: underline" value="'+oudn+'">' +
        log_info_str+'</td>';
    txt += '<td>' + final_result + '</td>';
    txt += '</tr>';
    return txt;
}
//+++20151104 显示日志用户详情
function show_log_user(a){
    var log_tr = a.parentNode.parentNode;
    var admin = log_tr.childNodes[0].innerHTML;
    var time = log_tr.childNodes[2].innerHTML;
    var action = "";
    var count = $(a).html();
    switch($("#op_type").val()){
        case "contact":
        case "all":
            action = "send contacts";
            if($("#log_user_pop").attr("time")){
                if(time!=$("#log_user_pop").attr("time")){
                    $("#log_user_pop").attr("time",time);
                    $("#log_user_pop").hide();
                    $("#control_user_tree").html("");
                }
            }else{
                $("#log_user_pop").attr("time",time);
            }
            add_first_user_ou(admin,time,action,count);
//            get_son_contact(admin,time,action,oudn,oudn);
            break;
    }
}
//+++20151118 加入第一个日志作用人节点
function add_first_user_ou(admin,time,action,count){
    var org_session_id = $.cookie("org_session_id");
    var obj = {
        _path:"/a/wp/org/get_log_control_users",
        _methods:"get",
        param:{
            sid:org_session_id,
            admin:admin,
            action:action,
            time:time
        }
    };
    ajaxReq(obj,function(data){
        console.log(data);
        var rt = data.rt;
        if(rt==0){
            loadingStatus("获取作用人员信息成功",0);
            var oudn = data['result']['oudn'];
            var outitle = document.createElement("DIV");
            outitle.style = "cursor:pointer";
            var img = document.createElement("IMG");
            img.src = "images/group.png";
            var a = document.createElement("A");
            a.style.cursor= "pointer";
            a.onclick = Function("show_log_control_users('"+admin+"','"+time+"','"+action+"','"+oudn+"','"+oudn+"');");
            a.innerHTML = get_ou_name(oudn)+"（"+count+"）";

            outitle.appendChild(img);
            outitle.appendChild(a);

            var oucontainer = document.createElement("DIV");
            oucontainer.style.marginLeft = "20px";
            oucontainer.style.display = "block";
            oucontainer.id = oudn;

            document.getElementById("control_user_tree").appendChild(outitle);
            document.getElementById("control_user_tree").appendChild(oucontainer);
            $("#log_user_pop").show();
        }
    },"正在获取作用人员信息");
}
function show_log_control_users(admin,time,action,oudn,container){
    //查看是否是同一条日志，如果是的话，继续，不是则需要隐藏重新加载

    if(document.getElementById(container).innerHTML!=""){
        var div = document.getElementById(container);
        if(div.style.display=="none"){
            div.style.display="block";
        }else{
            div.style.display="none";
        }

    }else{
        var org_session_id = $.cookie("org_session_id");
        var obj = {
            _path:"/a/wp/org/get_log_control_users",
            _methods:"get",
            param:{
                sid:org_session_id,
                admin:admin,
                action:action,
                time:time,
                oudn:oudn
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            if(rt==0){
                loadingStatus("获取作用人员信息成功",0);
                var log_contacts = data.result;
                var oudn = log_contacts['oudn'];
                var ous = log_contacts['ous'];
                var users = log_contacts['users'];
                var html = "";
                for (var i = 0; i < ous.length; i++) {
                    var sonoudn = ous[i]['oudn'];
                    var count = ous[i]['count'];
                    var outitle = document.createElement("DIV");
                    outitle.style = "cursor:pointer";

                    var img = document.createElement("IMG");
                    img.src = "images/group.png";
                    var a = document.createElement("A");
                    a.style.cursor= "pointer";
                    a.onclick = Function("show_log_control_users('"+admin+"','"+time+"','"+action+"','"+sonoudn+"','"+sonoudn+"');");
                    a.innerHTML = get_ou_name(sonoudn)+"（"+count+"人）";

                    outitle.appendChild(img);
                    outitle.appendChild(a);

                    var oucontainer = document.createElement("DIV");
                    oucontainer.style.marginLeft = "20px";
                    oucontainer.style.display = "block";
                    oucontainer.id = sonoudn;

                    document.getElementById(container).appendChild(outitle);
                    document.getElementById(container).appendChild(oucontainer);

                }

                for (var j = 0; j < users.length; j++) {
                    var user_li = document.createElement("LI");
                    user_li.title = users[j]['uid'];
                    var img = document.createElement("IMG");
                    img.src = "images/unline.png";
                    var a = document.createElement("A");
                    a.style.cursor = "pointer";
                    var fetch_result = "未响应";
                    if(users[j]['result']==0){
                        fetch_result="已取到";
                    }
                    a.innerHTML = users[j]['username']+":"+fetch_result;

                    user_li.appendChild(img);
                    user_li.appendChild(a);
                    document.getElementById(container).appendChild(user_li);
                }

            }
        },"正在作用人群详情");
    }
}
function show_log_contacts(a){
    var log_tr = a.parentNode.parentNode;
    var admin = log_tr.childNodes[0].innerHTML;
    var time = log_tr.childNodes[2].innerHTML;
    var action = "";
    var oudn = $(a).attr("value");
    var count = a.innerHTML.split(":")[1];
    switch($("#op_type").val()){
        case "contact":
        case "all":
            action = "send contacts";
            if($("#log_pop").attr("time")){
                if(time!=$("#log_pop").attr("time")){
                    $("#log_pop").attr("time",time);
                    $("#log_pop").hide();
                    $("#content_tree").html("");
                }
            }else{
                $("#log_pop").attr("time",time);
            }
            add_first_ou(admin,time,action,oudn,count);
            get_son_contact(admin,time,action,oudn,oudn);
            break;
    }

}
$("#log_bcol tbody tr td a[title='点击查看通讯录内容']").live("click",function(event){
    //修改div显示的坐标
    var x = event.clientX;
    var y = event.clientY;
    var container = document.getElementById("log_pop");

    if((y+container.offsetTop)<300){
        y +=200;
    }

    container.style.left = (x + container.offsetLeft+30)+"px";
    container.style.top = (y + container.offsetTop+30)+"px";
    //修改选中a的颜色
    $("#log_bcol tbody tr td .content_selected").each(function(index,element){
        element.className="content_normal";
    });
    $(this).attr("class","content_selected");
});
$("#log_bcol tbody tr td a[title='点击查看作用用户']").live("click",function(event){
    //修改div显示的坐标
    var x = event.clientX;
    var y = event.clientY;
    var container = document.getElementById("log_user_pop");

    if((y+container.offsetTop)<300){
        y +=200;
    }

    container.style.left = (x + container.offsetLeft+30)+"px";
    container.style.top = (y + container.offsetTop+30)+"px";
    //修改选中a的颜色
    $("#log_bcol tbody tr td .content_selected").each(function(index,element){
        element.className="content_normal";
    });
    $(this).attr("class","content_selected");
});
//+++20151117 添加第一层群组节点
function add_first_ou(admin,time,action,oudn,count){
    var outitle = document.createElement("DIV");
    outitle.style = "cursor:pointer";
    var img = document.createElement("IMG");
    img.src = "images/group.png";
    var a = document.createElement("A");
    a.style.cursor= "pointer";
    a.onclick = Function("get_son_contact('"+admin+"','"+time+"','"+action+"','"+oudn+"','"+oudn+"');");
    a.innerHTML = get_ou_name(oudn)+"（"+count+"）";

    outitle.appendChild(img);
    outitle.appendChild(a);

    var oucontainer = document.createElement("DIV");
    oucontainer.style.marginLeft = "20px";
    oucontainer.style.display = "block";
    oucontainer.id = oudn;

    document.getElementById("content_tree").appendChild(outitle);
    document.getElementById("content_tree").appendChild(oucontainer);
}
//+++20151116 向服务器请求通讯录数据
function get_son_contact(admin,time,action,oudn,container){
    //查看是否是同一条日志，如果是的话，继续，不是则需要隐藏重新加载

    if(document.getElementById(container).innerHTML!=""){
        var div = document.getElementById(container);
        if(div.style.display=="none"){
            div.style.display="block";
        }else{
            div.style.display="none";
        }

    }else{
        var org_session_id = $.cookie("org_session_id");
        var obj = {
            _path:"/a/wp/org/get_log_contacts",
            _methods:"get",
            param:{
                sid:org_session_id,
                admin:admin,
                action:action,
                time:time,
                oudn:oudn
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            if(rt==0){
                loadingStatus("成功获取通讯录详情，点击展开",0);
                var log_contacts = data.log_contacts;
                var oudn = log_contacts['oudn'];
                var ous = log_contacts['ous'];
                var users = log_contacts['users'];
                var html = "";
                for (var i = 0; i < ous.length; i++) {
                    var sonoudn = ous[i]['oudn'];
                    var count = ous[i]['count'];
                    var outitle = document.createElement("DIV");
                    outitle.style = "cursor:pointer";

                    var img = document.createElement("IMG");
                    img.src = "images/group.png";
                    var a = document.createElement("A");
                    a.style.cursor= "pointer";
                    a.onclick = Function("get_son_contact('"+admin+"','"+time+"','"+action+"','"+sonoudn+"','"+sonoudn+"');");
                    a.innerHTML = get_ou_name(sonoudn)+"（"+count+"人）";

                    outitle.appendChild(img);
                    outitle.appendChild(a);

                    var oucontainer = document.createElement("DIV");
                    oucontainer.style.marginLeft = "20px";
                    oucontainer.style.display = "block";
                    oucontainer.id = sonoudn;

                    document.getElementById(container).appendChild(outitle);
                    document.getElementById(container).appendChild(oucontainer);

                }

                for (var j = 0; j < users.length; j++) {
                    var user_li = document.createElement("LI");
                    user_li.title = users[j]['uid'];
                    var img = document.createElement("IMG");
                    img.src = "images/unline.png";
                    var a = document.createElement("A");
                    a.style.cursor = "pointer";
                    a.innerHTML = users[j]['name']+":"+users[j]['uid'];

                    user_li.appendChild(img);
                    user_li.appendChild(a);
                    document.getElementById(container).appendChild(user_li);
                }
                $("#log_pop").show();
            }
        },"正在获取通讯录详情");
    }
}
/*----end显示联系人信息区域----*/
//根据oudn获取群组名称
function get_ou_name(oudn){
    var ouname = "";
    if(oudn==""){
        ouname = "未知群组";
    }else{
        ouname = oudn.split(",")[0].split('=')[1];
        if(ouname =="test"){
            ouname = "总共";
        }
    }
    return ouname;
}
//+++20151104 获取日志显示的日志群组信息
function get_log_info_str(info){
//    var log_info_str = "";
//    for(var i=info_array.length-1;i>=0;i--){
//        log_info_str+=info_array[i]['name']+":"+info_array[i]['length']+"人\n";
//    }
//    log_info_str+="\n";
//    return log_info_str;
    var oudn = info['oudn'];
    var ouname = "";
    var muti_son = info['muti_son'];
    if(muti_son>1){
        ouname = "多个群组";
    }else{
        var ouarray = oudn.substr(0,oudn.indexOf("dc")-1).split(",");
        for(var i=ouarray.length-1;i>=0;i--){
            ouname+=ouarray[i].split("=")[1]+"/";
        }
        ouname = ouname.substr(0,ouname.length-1);
    }
    var count = info['count'];
    var log_info_str = ouname+":"+count+"人";
    return log_info_str;

}
//+++20151104 获取发送联系人的描述
var log_infos = [];
function get_log_info(info){
    var oudn = info['oudn'];
    var ous = info['ous'];
    var users = info['users'];
    var ou_user_count = 0;
    if(users.length>0){
        ou_user_count+=users.length;
    }
    if(ous.length>0){
        for(var i=0;i<ous.length;i++){
            ou_user_count += get_log_info(ous[i]);
        }
    }
    if(ou_user_count!=0){
        var ouname = "";
        if(oudn==ldap_base_dn){
            ouname = "所有用户";
        }else{
            var ouarray = oudn.substr(0,oudn.indexOf("dc")-1).split(",");
            for(var i=ouarray.length-1;i>=0;i--){
                ouname+=ouarray[i].split("=")[1]+"/";
            }
            ouname = ouname.substr(0,ouname.length-1);
        }
        log_infos.push({'name':ouname,'length':ou_user_count});
    }
    return ou_user_count;
}
/*end 显示联系人信息日志区域*/

/*显示登录日志信息区域*/
function show_login_log(log){
    var txt = "";
    var users = log['users'];
    //生成user的html
    var user_html = "";

    //生成通讯录html
    var info = log['info'];
    var oudn = info['oudn'];
    //生成登陆结果
    var rt = log['result'];
    var result = "登录失败";
    if(rt=="正确"){
        result = "登录成功";
    }else if(rt=="验证码错误"){
        result = "登录失败（验证码错误）";
    }

    txt += '<tr>';
    txt += '<td>' + log['uid'] + '</td>'; //操作人
    txt += '<td>' + "登录" + '</td>';     //操作类型
    txt += '<td>' + log['time']+ '</td>'; //操作时间
    txt += '<td>' + "管控系统"+ '</td>';   //操作对象，登录的是哪一个系统
    txt += '<td>' + log['info']+ '</td>'; //操作内容，登录IP
    txt += '<td>' + result + '</td>';//操作结果，是否成功登录，显示第三次控制？
    txt += '</tr>';
    index++;
    return txt;
}
/*end 显示登录日志信息区域*/

/* start 日志信息分页 */
//+++20151109 日志信息分页
function set_bottom(logNumber, logPerPage){
    var logPerPage = logPerPage;
    var pageNumber = Math.ceil(logNumber / logPerPage);
    //for title
    var txt = "共0页，0条用户信息";
    //for page change
    if (logNumber != 0 && logNumber != null) {
        txt = "共" + pageNumber + "页，" + logNumber + "条日志信息";
    }
    $("#logs_perpage").html("(每页"+logPerPage+"条)");
    $("#log_bottom_title").html(txt);
    $("#log_bottom_title").attr('value', pageNumber);
}
function set_page(page){
    $("#log_page_number").val(page);
    $("#log_page_number").attr('value', page);
}
function reset_bottom(){
    set_bottom(0,logs_per_page);
    set_page(0);
}
//首页
$("#log_first_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#log_page_number").val());
    if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }else{
        load_logs_by_input(1);
//        $("#log_page_number").val(1);
    }
});
//末页
$("#log_end_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#log_page_number").val());
    if (cur_page < 1) {
        return;
    } else if ($("#log_bottom_title").attr('value') == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }else{
        load_logs_by_input($("#log_bottom_title").attr('value'));
//        $("#log_page_number").val($("#log_bottom_title").attr('value'));
    }
});
//上一页
$("#log_pre_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#log_page_number").val());
    if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }else{
        load_logs_by_input(cur_page-1);
    }
});
//下一页
$("#log_next_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#log_page_number").val());
    if (cur_page < 1) {
        return;
    } else if ($("#log_bottom_title").attr('value') == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }else{
        load_logs_by_input(cur_page+1);
    }

});
//跳页
function log_page_change(page_index){
    var totalPages = $("#log_bottom_title").attr('value');
    if (totalPages < 1) {
        //+++20150824 如果用户不满1页，应显示成1页
        $("#page_number").val(0);
        return;
    }
    //判断当前输入页数是否合法,不合法则返回当前页
    if (isNaN(page_index)) {
        loadingStatus("非法输入，请输入数字！");
        $("#page_number").focus();
        return;
    }
    //+++20150824 加入对于输入页数0的限制
    if (parseInt(page_index) <= 0 || parseInt(page_index) > totalPages) {
        loadingStatus("当前输入超出页数范围，请重新输入！");
        return;
    }
    load_logs_by_input(parseInt(page_index));
}
/* end 日志信息分页 */

/* 一些全局操作*/
$("#log_ok").click(function(event){
    event.preventDefault;
    $("#log_pop").hide();
    $("#content_tree").html("");
    $("#log_bcol tbody tr td .content_selected").each(function(index,element){
        element.className="content_normal";
    });
});
$("#control_user_ok").click(function(event){
    event.preventDefault;
    $("#log_user_pop").hide();
    $("#control_user_tree").html("");
    $("#log_bcol tbody tr td .content_selected").each(function(index,element){
        element.className="content_normal";
    });
});
//+++20151109 将表中的信息清空
function clear_table(){
    $("#log_bcol tr").remove();
}
/* end一些全局操作*/
