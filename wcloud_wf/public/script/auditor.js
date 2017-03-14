//审计日志检索与报告生成
$(document).ready(function() {
    $("#searchlog").click(function(){
        var mydate = new Date();
        var year = mydate.getFullYear();
        var month ='00'+ (mydate.getMonth()+1);
        var date ='00'+ mydate.getDate()
        var start = year+"-"+month.substr(-2)+"-"+date.substr(-2)+" 00:00";
        var end  = year+"-"+month.substr(-2)+"-"+(parseInt(date.substr(-2))+1)+" 00:00";
        document.getElementById('log_start_time').value=start;
        document.getElementById('log_end_time').value=end;
        document.getElementById('operator_log').value='';
        document.getElementById('log_number').value='';
        document.getElementById("searchlog_con").style.display="block";
    });
    $("#ex2excel").click(function(){
        document.getElementById("auditlog_con").style.display="block";
    });
    $("#logspace").click(function(){
        document.getElementById("logspace_con").style.display="block";
        getspacestate();
    });
});
//退出
$("#exitlog").live('click',function(event) {
    var n = document.getElementById("auditlog_con");
    document.getElementById('log_end_time').className="false";
    n.style.display = "none";
    $("#auditlog_con input").val("");
    var n = document.getElementById("searchlog_con");
    document.getElementById('log_end_time').className="false";
    n.style.display = "none";
    $("#searchlog_con input").val("");
    var n = document.getElementById("logspace_con");
    n.style.display = "none";
    $("#logspace_con input").val("");
});

//刷新审计日志
$("#shuaxin_log").live('click',function(event) {
    $("#au_stB tbody").html("");
    loadauditorlog();
});

//检索功能实现
$("#logsearch").live('click',function(event) {
    event.preventDefault();
    var log_start_time = $("#log_start_time");
    var log_end_time = $("#log_end_time");
    var operator=$("#operator_log");
    var log_number=$("#log_number");
    var obj = {
        _path: '/a/wp/org/search_logs',
        _methods: 'get',
        param: {
            start: log_start_time.val(),
            end: log_end_time.val(),
            operator:operator.val(),
            log_number: log_number.val(),
            sid: $.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        var se_logs=data.se_logs;
        if (rt === 0) {
            loadingStatus("日志获取成功！", 0);
            document.getElementById("searchlog_con").style.display = "none";
            $("#au_stB tbody").html("");
            for(var i=0;i<se_logs.length;i++)
            {
                searchauditlog(se_logs[i],i+1);
            }
        }
        else {
            loadingStatus("检索日志失败！", 0);
            document.getElementById("searchlog_con").style.display = "none";
        }
    });
});
function searchauditlog(se_log,i){
    var user=se_log['uid'];
    var op_type=se_log['action'];
    var op_desc=se_log['info'];
    var op_result=se_log['result'];
    var optime=se_log['time'];

    var op_time=new Date(parseInt(optime) * 1000).toLocaleString();

    //审计日志内容
    if(op_type=="send contacts"){
        //op_desc=JSON.stringify(op_desc['ous'][0]['users']);
        op_desd=JSON.stringify(op_obj[0]['oudn'].split(',')[0].slice(3,-1));
        op_desdnum=JSON.stringify(op_obj.length);
        str=op_desd.replace(/\"/g,"");
        console.log(op_desd);
        console.log(op_desdnum);
        var txt;
        txt="";
        txt+='<tr><td>'+i+'</td>';
        txt+='<td>'+op_time+'</td>';
        txt+='<td>'+user+'</td>';
        txt+='<td>'+"同步联系人"+'</td>';
        txt+='<td>'+str+op_desdnum+'</td>';
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
    $("#au_stB tbody").append(txt);
    $(" #auditlogB").mCustomScrollbar("update");
}

//导出日志时的审计员验证
$("#audit_sure").live('click',function(event) {
    var auditlog_sazh = $("#auditlog_sazh");
    var auditlog_sapw = $("#auditlog_sapw");
    var obj = {
        _path: '/a/wp/org/auditlog_check',
        _methods: 'get',
        param: {
            sazh: auditlog_sazh.val(),
            sapw: auditlog_sapw.val()
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt == 0) {
            loadingStatus("正在导出审计报告...",1);
            document.getElementById("auditlog_con").style.display = "none";
            $("#auditlog_con input").val("");
            exportlog();
        }
        else {
            loadingStatus("验证失败！", 0);
            document.getElementById("auditlog_con").style.display = "none";
            $("#auditlog_con input").val("");
        }
    });
});
//导出日志
function exportlog(){
    var obj = {
        _path: '/a/wp/org/export_log',
        _methods: 'get',
        param: {
            sid: $.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt === 0) {
            loadingStatus("审计报告生成成功！", 0);
            excel_download();
        }
        else {
            loadingStatus("审计报告生成失败！", 0);
        }
    });
}
//下载生成的审计报告
function excel_download(){
    location.href='http://111.204.189.58:8083/download/audit_log.xls';
}
//审计阈值空间
function getspacestate(){
    var obj = {
        _path: '/a/wp/org/get_space_state',
        _methods: 'get',
        param: {
            sid: $.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        var currentspace=data.currentspace;
        var currentlimit=data.currentlimit;
        if (currentlimit==''){
            currentlimit=200*0.13;
        }
        if (rt === 0) {
            setText($("#currentspace"),currentspace.toFixed(3)+'kb');
            setText($("#currentlimit"),currentlimit.toFixed(3)+'kb');
        }
        else {
            loadingStatus("审计空间信息获取失败！", 0);
        }
    });
}
//设置阈值
$("#setspace").live('click',function(event) {
    var log_space_set = $("#log_space_set");
    var obj = {
        _path: '/a/wp/org/set_log_space',
        _methods: 'get',
        param: {
            log_space_set: log_space_set.val(),
            sid: $.cookie("org_session_id"),
            loginType:$.cookie("loginType")
        }
    };
    ajaxReq(obj, function(data) {
        var rt = data.rt;
        if (rt === 0) {
            document.getElementById("logspace_con").style.display = "none";
            $("#logspace_con input").val("");
            loadingStatus("阈值设置成功！");
            getspacestate();
        }
        else {
            document.getElementById("logspace_con").style.display = "none";
            $("#logspace_con input").val("");
            loadingStatus("阈值设置失败！", 0);
        }
    });
});