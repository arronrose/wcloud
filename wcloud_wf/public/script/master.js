/**
 * Created by ZXC on 2014/11/17.
 */
//管理员管理权限
var admin_right_list = null;
//管理员通信权限
var g_admin_contact_ous = null;
//添加操作员
$("#addadmin").submit(function(event){
    event.preventDefault();

    var uid=$("#adname").val();
    var pw1=$("#adpw1").val();
    var pw2=$("#adpw2").val();
    var email=$("#admail").val();
    var phonenumber=$("#adphone").val();
    var ou= operator_right_list.oudn();
    var contact_ous = get_admin_contact_ous(ou,"txqx_list");
    //var logo="admin";
    //判断输入
    //姓名监测
    if(!verViod(uid)){
        loadingStatus("用户名不能为空!");
        return false;
    }
    //邮箱监测
    if(!verViod(email)){
        loadingStatus("邮箱不能为空!");
        return false;
    }
    if (!checkemail(email)){
        loadingStatus("邮箱格式不对!");
        return false;
    }
    if(ou==[]){
        alert("管辖范围不能为空！！！");
        return;
    }
    //监测两次密码是否一样
    if(!verViod(pw1)){
        loadingStatus("密码不能为空!");
        return false;
    }
    if(!verViod(pw2)){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(pw1!=pw2){
        loadingStatus("两次密码不一致!");
        $("#adpw2").val("");
        return false;
    }
    //检验电话号码
    var reg = new RegExp('^[1][3-8]+\\d{9}');
    if(phonenumber.length<11 || !reg.test(phonenumber))
    {
        loadingStatus("电话号码无效！");
        return false;
    }
    if(ou==="")
    {
        loadingStatus("操作员权限不能为空！");
        return false;
    }
    if(contact_ous===[]){
        loadingStatus("通信权限不能为空！");
        return false;
    }


    //存入数据库（用于login检测）
    var obj={
        _path:"/a/wp/org/add_admin",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType"),
            uid:uid,
            pw:pw1,
            ou:ou,
            email:email,
            phonenumber:phonenumber,
            contact_ous:JSON.stringify(contact_ous),
            //logo:logo
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("操作员添加成功");
            $("#adname").val("");
            $("#adpw1").val("");
            $("#adpw2").val("");
            $("#admail").val("");
            $("#adphone").val("");
        }
        else if(data.rt==12){
            loadingStatus("操作员已存在");
        }
    },"正在提交...");

});

//管理员资料master.jade
//修改密码
$("#mastermim").submit(function(event){
    event.preventDefault();
    var dma=$("#masterdma");
    var xma=$("#masterxma");
    var qxma=$("#masterqxma");
    if(!verViod(dma.val())){
        loadingStatus("当前密码不能为空!");
        return false;
    }
    if(!verViod(xma.val())){
        loadingStatus("新密码不能为空!");
        return false;
    }
    if(!verViod(qxma.val())){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(xma.val()!=qxma.val()){
        loadingStatus("两次密码不一致!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/set_pw",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            oldpw:dma.val(),
            newpw:xma.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("密码已修改");
            $("#mastermim").parent().slideUp("fast");
            dma.val("");
            xma.val("");
            qxma.val("");
        }else if(data.rt==18){
            loadingStatus("密码不符合规则!");
        }else if(data.rt=19){
            loadingStatus("旧密码输入错误!");
        }
    },"正在提交...");
});

//审计员资料auditor.jade
//修改密码
$("#auditormim").submit(function(event){
    event.preventDefault();
    var dma=$("#auditordma");
    var xma=$("#auditorxma");
    var qxma=$("#auditorqxma");
    if(!verViod(dma.val())){
        loadingStatus("当前密码不能为空!");
        return false;
    }
    if(!verViod(xma.val())){
        loadingStatus("新密码不能为空!");
        return false;
    }
    if(!verViod(qxma.val())){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(xma.val()!=qxma.val()){
        loadingStatus("两次密码不一致!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/set_pw",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            oldpw:dma.val(),
            newpw:xma.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("密码已修改");
            $("#mastermim").parent().slideUp("fast");
            dma.val("");
            xma.val("");
            qxma.val("");
        }else if(data.rt==18){
            loadingStatus("密码不符合规则!");
        }else if(data.rt=19){
            loadingStatus("旧密码输入错误!");
        }
    },"正在提交...");
});
//添加审计员
$("#addauditor").submit(function(event){
    event.preventDefault();
    if(document.getElementById("auzhqx").disabled == true)
    {
        alert("您的权限不够，不能够添加审计员！！！");
        $("#auzh").val("");
        $("#auzhmm1").val("");
        $("#auzhmm2").val("");
        $("#auzhmail").val("");
        $("#auzhphone").val("");
        return;
    }
    var uid=$("#auzh").val();
    var pw1=$("#auzhmm1").val();
    var pw2=$("#auzhmm2").val();
    var email=$("#auzhmail").val();
    var phonenumber=$("#auzhphone").val();
    var ou=$("#auzhqx").val();

    if(ou==""){
        alert("审计员权限不能为空！！！");
        return;
    }
    //判断输入
    //姓名监测
    if(!verViod(uid)){
        loadingStatus("用户名不能为空!");
        return false;
    }
    //邮箱监测
    if(!verViod(email)){
        loadingStatus("邮箱不能为空!");
        return false;
    }
    if (!checkemail(email)){
        loadingStatus("邮箱格式不对!");
        return false;
    }
    //监测两次密码是否一样
    if(!verViod(pw1)){
        loadingStatus("密码不能为空!");
        return false;
    }
    if(!verViod(pw2)){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(pw1!=pw2){
        loadingStatus("两次密码不一致!");
        $("#xzhmm2").val("");
        return false;
    }
    //检验电话号码
    var reg = new RegExp('^[1][3-8]+\\d{9}')
    if(phonenumber.length<11 || !reg.test(phonenumber))
    {
        loadingStatus("电话号码无效！");
        return false;
    }

    var obj={
        _path:"/a/wp/org/add_auditor",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType"),
            uid:uid,
            pw:pw1,
            ou:ou,
            email:email,
            phonenumber:phonenumber
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("审计员添加成功");
            $("#auzh").val("");
            $("#auzhmm1").val("");
            $("#auzhmm2").val("");
            $("#auzhmail").val("");
            $("#auzhphone").val("");
        }
    },"正在提交...");

});

//安全员资料sa.jade
//修改密码
$("#samim").submit(function(event){
    event.preventDefault();
    var dma=$("#sadma");
    var xma=$("#saxma");
    var qxma=$("#saqxma");
    if(!verViod(dma.val())){
        loadingStatus("当前密码不能为空!");
        return false;
    }
    if(!verViod(xma.val())){
        loadingStatus("新密码不能为空!");
        return false;
    }
    if(!verViod(qxma.val())){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(xma.val()!=qxma.val()){
        loadingStatus("两次密码不一致!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/set_pw",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            oldpw:dma.val(),
            newpw:xma.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("密码已修改");
            $("#mastermim").parent().slideUp("fast");
            dma.val("");
            xma.val("");
            qxma.val("");
        }else if(data.rt==18){
            loadingStatus("密码不符合规则!");
        }else if(data.rt=19){
            loadingStatus("旧密码输入错误!");
        }
    },"正在提交...");
});
//添加安全员
$("#addsa").submit(function(event){
    event.preventDefault();
    if(document.getElementById("sazhqx").disabled == true)
    {
        alert("您的权限不够，不能够添加安全员！！！");
        $("#sazh").val("");
        $("#sazhmm1").val("");
        $("#sazhmm2").val("");
        $("#sazhmail").val("");
        $("#sazhphone").val("");
        return;
    }
    var uid=$("#sazh").val();
    var pw1=$("#sazhmm1").val();
    var pw2=$("#sazhmm2").val();
    var email=$("#sazhmail").val();
    var phonenumber=$("#sazhphone").val();
    var ou=$("#sazhqx").val();

    if(ou==""){
        alert("安全员权限不能为空！！！");
        return;
    }
    //判断输入
    //姓名监测
    if(!verViod(uid)){
        loadingStatus("用户名不能为空!");
        return false;
    }
    //邮箱监测
    if(!verViod(email)){
        loadingStatus("邮箱不能为空!");
        return false;
    }
    if (!checkemail(email)){
        loadingStatus("邮箱格式不对!");
        return false;
    }
    //监测两次密码是否一样
    if(!verViod(pw1)){
        loadingStatus("密码不能为空!");
        return false;
    }
    if(!verViod(pw2)){
        loadingStatus("确认密码不能为空!");
        return false;
    }
    if(pw1!=pw2){
        loadingStatus("两次密码不一致!");
        $("#xzhmm2").val("");
        return false;
    }
    //检验电话号码
    var reg = new RegExp('^[1][3-8]+\\d{9}')
    if(phonenumber.length<11 || !reg.test(phonenumber))
    {
        loadingStatus("电话号码无效！");
        return false;
    }

    var obj={
        _path:"/a/wp/org/add_sa",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType"),
            uid:uid,
            pw:pw1,
            ou:ou,
            email:email,
            phonenumber:phonenumber
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("安全员添加成功");
            $("#sazh").val("");
            $("#sazhmm1").val("");
            $("#sazhmm2").val("");
            $("#sazhmail").val("");
            $("#sazhphone").val("");
        }
    },"正在提交...");

});

/*master list*/
//master排序
function ma_sortable(index,aid){
    var table = document.getElementById('ma_yglb');
    var tbody = table.tBodies[0];
    var colRows = tbody.rows;
    var aTrs = new Array;
    //alert(colRows.length);
    if(colRows.length==0){
        return;
    }
    else{
        for (var i=0; i < colRows.length; i++) {
            aTrs[i] = colRows[i];
        }

        //现在已经获取到所有的tbody中的数据，要做的就是根据相应的行进行排序
        var aa=document.getElementById(aid);//获取到a标签
        if(index==5){
            //alert(getTitleCode(aTrs[0].cells[index].innerHTML));

            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)>getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)<=getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }

            }

        }



        else if(index==6){
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)>getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)>=getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)<getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)<getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }

            }
        }




        else{
            //alert(aa.className);
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)>0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else if(aa.className=='1'){
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)<=0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
        }
    }
}
//master选择全部与空出选择
//选择全部的按钮
$("#ma_xzqb").live("click",function(event){
    if($("#ma_yglb tbody tr").children("td").length==0){
        alert("请在左侧选取用户");//jquery搜索标签并对标签进行操作的过程基本上都是用的函数
    }
    else{
        $("#ma_yglb tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
        $("#gnan .tog").show();
    }
});
//空出选择的按钮
$("#ma_kcxz").live("click",function(event){
    $("#ma_yglb tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    $("#gnan .tog").hide();
});
//删除master
$("#ma_lsscyh").submit(function(event){
    event.preventDefault();
    $("#ma_delete").dialog("close");
    var org_session_id=$.cookie("org_session_id");
    var arr = check_massyh();
    
    for(var i=0,len=arr.length;i<len;i++){
        var uid=arr[i];
        //删除master
        var obj={
            _path: '/a/wp/org/del_master',
            _methods: 'post',
            param: {
                sid: org_session_id,
                uid:uid,
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            if(rt==0){
                loadingStatus("已经清除工作数据!",0);
                $("#ma_yglb tbody tr .checkbox_checked").each(function(index,element){
                    var tr = $(element).parent().parent();
                    tr.hide();
                    $("#ma_shebeiB").mCustomScrollbar("update")
                });
            }else{
                loadingStatus("清除工作数据失败!",0);
            }
        },"正在清除工作数据...");
    }
    //需要重新加载树,清除原来的数据
    $("#ma_yic").html("");
    masterhome();
});
function check_massyh(){
    var arr=[];
    $("#ma_yglb tbody tr .checkbox_checked").each(function(index,element){
        var that=$(element).parent().parent();
        if($(".username",that).html()!=''){
            arr.push($(".username",that).html());
        }
    });
    return arr;
}
//拒绝删除master
$("#ma_bScyh").click(function(event) {
    $("#ma_delete").dialog("close");
});
//通过电话或者邮件过滤设备master
$("#ma_guolv").bind("keyup",flushmaDev);
function flushmaDev(event){
    var value=$(this).val();
    if(!!value){	//如果value非空，则隐藏所有tr，只显示匹配tr。
        $("#ma_yglb tbody tr").hide();
        $("#ma_yglb tbody tr").each(function(index,element){
            var trText=$(element).text();
            if(trText.indexOf(value)>-1){
                $(element).show();
            }
        })
    }else{		//反之，则显示所有tr。
        $("#ma_yglb tbody tr").show();
    }

}

/*admin list*/
//admin排序
function ad_sortable(index,aid){
    var table = document.getElementById('ad_yglb');
    var tbody = table.tBodies[0];
    var colRows = tbody.rows;
    var aTrs = new Array;
    if(colRows.length==0){
        return;
    }
    else{
        for (var i=0; i < colRows.length; i++) {
            aTrs[i] = colRows[i];
        }

        //现在已经获取到所有的tbody中的数据，要做的就是根据相应的行进行排序
        var aa=document.getElementById(aid);//获取到a标签
        if(index==5){
            //alert(getTitleCode(aTrs[0].cells[index].innerHTML));

            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)>getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)<=getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }

            }

        }



        else if(index==6){
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)>getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)>=getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)<getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)<getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }

            }
        }




        else{
            //alert(aa.className);
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)>0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else if(aa.className=='1'){
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)<=0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
        }
    }
}
//admin选择全部与空出选择
//选择全部的按钮
$("#ad_xzqb").live("click",function(event){
    if($("#ad_yglb tbody tr").children("td").length==0){
        alert("请在左侧选取用户");//jquery搜索标签并对标签进行操作的过程基本上都是用的函数
    }
    else{
        $("#ad_yglb tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
        $("#gnan .tog").show();
    }
});
//空出选择的按钮
$("#ad_kcxz").live("click",function(event){
    $("#ad_yglb tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    $("#gnan .tog").hide();
});
//删除admin
$("#ad_lsscyh").submit(function(event){
    event.preventDefault();
    $("#ad_delete").dialog("close");
    var org_session_id=$.cookie("org_session_id");
    var arr = check_adssyh();
    for(var i=0,len=arr.length;i<len;i++){
        var uid=arr[i];
        var obj={
            _path: '/a/wp/org/del_admin',
            _methods: 'post',
            param: {
                sid: org_session_id,
                uid:uid,
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            if(rt==0){
                loadingStatus("已经清除工作数据!",0);
                $("#ad_yglb tbody tr .checkbox_checked").each(function(index,element){
                    var tr = $(element).parent().parent();
                    tr.hide();
                    $("#ad_shebeiB").mCustomScrollbar("update")
                });
            }else{
                loadingStatus("清除工作数据失败!",0);
            }
        },"正在清除工作数据...");
    }
    //需要重新加载树,清除原来的数据
    $("#ad_yic").html("");
    adminhome();
});
function check_adssyh(){
    var arr=[];
    $("#ad_yglb tbody tr .checkbox_checked").each(function(index,element){
        var that=$(element).parent().parent();
        if($(".username",that).html()!=''){
            arr.push($(".username",that).html());
        }
    });
    return arr;
}
//拒绝删除admin
$("#ad_bScyh").click(function(event) {
    $("#ad_delete").dialog("close");
});
//单个修改admin
function change_admin(element){
    reset_admin_info();
    $("#op_admin").show();
    //element是点击的button元素，需要先获取上层的tr信息
    var tr = element.parentNode.parentNode;
    var admin_id = $(".username",tr).html();
    var admin_email = $(".Email",tr).html();
    var admin_phone = $(".Telephone",tr).html();
    var admin_ou = $(".ou",tr).attr("oudn");
    var admin_contact_ous =$(".contact_ous",tr).attr("contact_ous").split("|");
    load_admin_info(admin_id,admin_email,admin_phone,admin_ou,admin_contact_ous);
}
//加载操作员信息
function load_admin_info(admin_id,admin_email,admin_phone,admin_ou,admin_contact_ous){
    var op_admin = $("#op_admin");
    $("#adname",op_admin).val(admin_id);
    $("#admail",op_admin).val(admin_email);
    $("#adphone",op_admin).val(admin_phone);

    //加载用户管理权限
    if(admin_right_list==null){
        admin_right_list = new RightList("gxfw",[ldap_base_dn]);
    }
    //当添加管控权限的时候默认添加为通信权限
    $("#gxfw select").bind("change",function(event){
        var xqxstr = admin_right_list.right_friendly_name();
        var admin_oudn = admin_right_list.oudn();
        var xzhContent = document.getElementById("txqx_list");
        //首先清空通信权限列表
        xzhContent.innerHTML = "";
        if(admin_oudn!=""){
            console.log("进入了");
            //将获取到的管控权限添加到通信权限列表
            var qx_item = create_new_qx_item(xqxstr,admin_oudn);
            //将该条目的移除button禁用
            qx_item.getElementsByTagName("button")[0].disabled = true;
            xzhContent.appendChild(qx_item);
        }
    });
    admin_right_list.show_oudn(ldap_base_dn,admin_ou);
    //加载用户通信权限
    if(g_admin_contact_ous==null){
        g_admin_contact_ous = new RightList("txqxbm",[ldap_base_dn]);
    }
    show_contact_ous(admin_contact_ous,admin_ou);
}
//重置操作员信息
function reset_admin_info(){
    var op_admin = $("#op_admin");
    $("#adname",op_admin).val("");
    $("#admail",op_admin).val("");
    $("#adphone",op_admin).val("");

    //加载用户管理权限
    if(admin_right_list){
        admin_right_list.reset();
    }
    if(g_admin_contact_ous){
        g_admin_contact_ous.reset();
    }

    $("#txqx_list").html("");
}






//修改中点击添加按钮
$("#change_addtxqxBtn").click(function(event){

    event.preventDefault();
    //如果同行的select中只有一个且值为“请选择”，提示请选择要添加的权限
    var btn = document.getElementById("change_addtxqxBtn");
    if(admin_right_list.oudn()==""){
        alert("请先选择该操作员的管控权限！！");
        return;
    }
    if(!g_admin_contact_ous.oudn()){
        alert("请选择要添加的权限");
    }
    else{
        //如果不是请选择，那么将select的权限字符串取出，添加新的权限行
        var xqxstr = g_admin_contact_ous.right_friendly_name();
        var xqx_oudn = g_admin_contact_ous.oudn();
        var xzhContent = document.getElementById("txqx_list");

        var qx_valid = is_qx_valid(xqxstr,"txqx_list");
        if(qx_valid==0){
            //父容器div
            var qx_item = create_new_qx_item(xqxstr,xqx_oudn);
            xzhContent.appendChild(qx_item);
//            resetAddAdminLog();
        }
        else if(qx_valid==-1){
            alert("已经添加了相同或更高级权限，请重新选择");
//            resetAddAdminLog();
        }
        else{
            if(confirm("您的列表中已经有子权限，是否选择覆盖")==true){
                //覆盖子权限
                var qx_lables = $("#txqx_list .qxlabel");
                for(var i=0;i<qx_lables.length;i++){
                    var item_oudn = $(qx_lables[i]).attr("oudn");
                    if(item_oudn.indexOf(xqx_oudn)>=0){
                        var parent_div = qx_lables[i].parentNode;
                        xzhContent.removeChild(parent_div);
                    }
                }
                var new_qx_item = create_new_qx_item(xqxstr,xqx_oudn);
                xzhContent.appendChild(new_qx_item);
            }
        }
    }
});






$("#change_adminexit").click(function(event){
    $("#op_admin").hide();
});
//提交修改--操作员信息
$("#change_operator_form").submit(function(event){
    event.preventDefault();

    var uid=$("#adname").val();
    var email=$("#admail").val();
    var phonenumber=$("#adphone").val();
    var ou= admin_right_list.oudn();
    var contact_ous = get_admin_contact_ous(ou,"txqx_list");

    //判断输入
    //姓名监测
    if(!verViod(uid)){
        loadingStatus("用户名不能为空!");
        return false;
    }
    //邮箱监测
    if(!verViod(email)){
        loadingStatus("邮箱不能为空!");
        return false;
    }
    if (!checkemail(email)){
        loadingStatus("邮箱格式不对!");
        return false;
    }
    //检验电话号码
    var reg = new RegExp('^[1][3-8]+\\d{9}');
    if(phonenumber.length<11 || !reg.test(phonenumber))
    {
        loadingStatus("电话号码无效！");
        return false;
    }
    if(ou=="")
    {
        loadingStatus("操作员权限不能为空！");
        return false;
    }
    if(contact_ous.length==0){
        loadingStatus("通信权限不能为空！");
        return false;
    }


    //存入数据库（用于login检测）
    var obj={
        _path:"/a/wp/org/mod_admin",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            loginType:$.cookie("loginType"),
            uid:uid,
            ou:ou,
            email:email,
            phonenumber:phonenumber,
            contact_ous:JSON.stringify(contact_ous)
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("操作员信息修改成功");
            reset_admin_info();
            $("#op_admin").hide();
        }
        else if(data.rt==12){
            loadingStatus("操作员已存在");
        }
    },"正在提交...");
});
//通过电话或者邮件过滤设备master
$("#ad_guolv").bind("keyup",flushadDev);
function flushadDev(event){
    var value=$(this).val();
    if(!!value){	//如果value非空，则隐藏所有tr，只显示匹配tr。
        $("#ad_yglb tbody tr").hide();
        $("#ad_yglb tbody tr").each(function(index,element){
            var trText=$(element).text();
            if(trText.indexOf(value)>-1){
                $(element).show();
            }
        })
    }else{		//反之，则显示所有tr。
        $("#ad_yglb tbody tr").show();
    }

}

/*sa list*/
//sa排序
function sa_sortable(index,aid){
    var table = document.getElementById('sa_yglb');
    var tbody = table.tBodies[0];
    var colRows = tbody.rows;
    var aTrs = new Array;
    if(colRows.length==0){
        return;
    }
    else{
        for (var i=0; i < colRows.length; i++) {
            aTrs[i] = colRows[i];
        }

        //现在已经获取到所有的tbody中的数据，要做的就是根据相应的行进行排序
        var aa=document.getElementById(aid);//获取到a标签
        if(index==5){
            //alert(getTitleCode(aTrs[0].cells[index].innerHTML));

            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)>getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)<=getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }

            }

        }



        else if(index==6){
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)>getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)>=getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)<getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)<getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }

            }
        }




        else{
            //alert(aa.className);
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)>0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else if(aa.className=='1'){
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)<=0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
        }
    }
}
//sa选择全部与空出选择
//选择全部的按钮
$("#sa_xzqb").live("click",function(event){
    if($("#sa_yglb tbody tr").children("td").length==0){
        alert("请在左侧选取用户");//jquery搜索标签并对标签进行操作的过程基本上都是用的函数
    }
    else{
        $("#sa_yglb tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
        $("#gnan .tog").show();
    }
});
//空出选择的按钮
$("#sa_kcxz").live("click",function(event){
    $("#sa_yglb tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    $("#gnan .tog").hide();
});
//删除sa
$("#sa_lsscyh").submit(function(event){
    event.preventDefault();
    $("#sa_delete").dialog("close");
    var org_session_id=$.cookie("org_session_id");
    var arr = check_sassyh();
    for(var i=0,len=arr.length;i<len;i++){
        var uid=arr[i];
        //删除master
        var obj={
            _path: '/a/wp/org/del_sa',
            _methods: 'post',
            param: {
                sid: org_session_id,
                uid:uid,
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            if(rt==0){
                loadingStatus("已经清除工作数据!",0);
                $("#sa_yglb tbody tr .checkbox_checked").each(function(index,element){
                    var tr = $(element).parent().parent();
                    tr.hide();
                    $("#sa_shebeiB").mCustomScrollbar("update")
                });
            }else{
                loadingStatus("清除工作数据失败!",0);
            }
        },"正在清除工作数据...");
    }
    //需要重新加载树,清除原来的数据
    $("#sa_yic").html("");
    sahome();
});
function check_sassyh(){
    var arr=[];
    $("#sa_yglb tbody tr .checkbox_checked").each(function(index,element){
        var that=$(element).parent().parent();
        if($(".username",that).html()!=''){
            arr.push($(".username",that).html());
        }
    });
    return arr;
}
//拒绝删除sa
$("#sa_bScyh").click(function(event) {
    $("#sa_delete").dialog("close");
});
//通过电话或者邮件过滤设备master
$("#sa_guolv").bind("keyup",flushsaDev);
function flushsaDev(event){
    var value=$(this).val();
    if(!!value){	//如果value非空，则隐藏所有tr，只显示匹配tr。
        $("#sa_yglb tbody tr").hide();
        $("#sa_yglb tbody tr").each(function(index,element){
            var trText=$(element).text();
            if(trText.indexOf(value)>-1){
                $(element).show();
            }
        })
    }else{		//反之，则显示所有tr。
        $("#sa_yglb tbody tr").show();
    }

}

/*auditor list*/
//auditor排序
function au_sortable(index,aid){
    var table = document.getElementById('au_yglb');
    var tbody = table.tBodies[0];
    var colRows = tbody.rows;
    var aTrs = new Array;
    if(colRows.length==0){
        return;
    }
    else{
        for (var i=0; i < colRows.length; i++) {
            aTrs[i] = colRows[i];
        }

        //现在已经获取到所有的tbody中的数据，要做的就是根据相应的行进行排序
        var aa=document.getElementById(aid);//获取到a标签
        if(index==5){
            //alert(getTitleCode(aTrs[0].cells[index].innerHTML));

            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)>getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getTitleCode(aTrs[j].cells[index].innerHTML)<=getTitleCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }

            }

        }



        else if(index==6){
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)>getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)>=getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }
            }
            else{
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(getDeCode(aTrs[j].cells[index].innerHTML)<getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                        if(getDeCode(aTrs[j].cells[index].innerHTML)==getDeCode(aTrs[j+1].cells[index].innerHTML)){
                            if(getTitleCode(aTrs[j].cells[index-1].innerHTML)<getTitleCode(aTrs[j+1].cells[index-1].innerHTML)){
                                var temp = aTrs[j].innerHTML;
                                aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                                aTrs[j+1].innerHTML = temp;
                            }
                        }
                    }
                    i--;
                }

            }
        }




        else{
            //alert(aa.className);
            if(aa.className=='0'){
                aa.className='1';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)>0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
            else if(aa.className=='1'){
                aa.className='0';
                var i=aTrs.length-1;
                while(i){
                    for(var j=0;j<i;j++){
                        if(aTrs[j].cells[index].innerHTML.localeCompare(aTrs[j+1].cells[index].innerHTML)<=0){
                            var temp = aTrs[j].innerHTML;
                            aTrs[j].innerHTML = aTrs[j+1].innerHTML;
                            aTrs[j+1].innerHTML = temp;
                        }
                    }
                    i--;
                }
            }
        }
    }
}
//auditor选择全部与空出选择
//选择全部的按钮
$("#au_xzqb").live("click",function(event){
    if($("#au_yglb tbody tr").children("td").length==0){
        alert("请在左侧选取用户");//jquery搜索标签并对标签进行操作的过程基本上都是用的函数
    }
    else{
        $("#au_yglb tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
        $("#gnan .tog").show();
    }
});
//空出选择的按钮
$("#au_kcxz").live("click",function(event){
    $("#au_yglb tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
    $("#gnan .tog").hide();
});
//删除auditor
$("#au_lsscyh").submit(function(event){
    event.preventDefault();
    $("#au_delete").dialog("close");
    var org_session_id=$.cookie("org_session_id");
    var arr = check_aussyh();
    for(var i=0,len=arr.length;i<len;i++){
        var uid=arr[i];
        //删除auditor
        var obj={
            _path: '/a/wp/org/del_auditor',
            _methods: 'post',
            param: {
                sid: org_session_id,
                uid:uid,
                loginType:$.cookie("loginType")
            }
        };
        ajaxReq(obj,function(data){
            var rt=data.rt;
            if(rt==0){
                loadingStatus("已经清除工作数据!",0);
                $("#au_yglb tbody tr .checkbox_checked").each(function(index,element){
                    var tr = $(element).parent().parent();
                    tr.hide();
                    $("#au_shebeiB").mCustomScrollbar("update")
                });
            }else{
                loadingStatus("清除工作数据失败!",0);
            }
        },"正在清除工作数据...");
    }
    //需要重新加载树,清除原来的数据
    $("#au_yic").html("");
    auditorhome();
});
function check_aussyh(){
    var arr=[];
    $("#au_yglb tbody tr .checkbox_checked").each(function(index,element){
        var that=$(element).parent().parent();
        if($(".username",that).html()!=''){
            arr.push($(".username",that).html());
        }
    });
    return arr;
}
//拒绝删除auditor
$("#au_bScyh").click(function(event) {
    $("#au_delete").dialog("close");
});
//通过电话或者邮件过滤设备master
$("#au_guolv").bind("keyup",flushauDev);
function flushauDev(event){
    var value=$(this).val();
    if(!!value){	//如果value非空，则隐藏所有tr，只显示匹配tr。
        $("#au_yglb tbody tr").hide();
        $("#au_yglb tbody tr").each(function(index,element){
            var trText=$(element).text();
            if(trText.indexOf(value)>-1){
                $(element).show();
            }
        })
    }else{		//反之，则显示所有tr。
        $("#au_yglb tbody tr").show();
    }

}

//+++20160309 添加通信权限
$("#addtxqxBtn").click(function(event){
    event.preventDefault();
    //如果同行的select中只有一个且值为“请选择”，提示请选择要添加的权限
    var btn = document.getElementById("addtxqxBtn");
    var pannel = btn.parentNode;
    var span = document.getElementById("txqxContent");
    var selects = span.children;
    //如果用户还没有选择管控权限，提醒先选管控权限
    if(operator_right_list.oudn()==""){
        alert("请先选择该操作员的管控权限！！");
        return;
    }
    if(!contact_rightList.oudn()){
        alert("请选择要添加的通信权限");
    }else{
        //如果不是请选择，那么将select的权限字符串取出，添加新的权限行
        //取得是ou 海信测试组
        var xqxstr = contact_rightList.right_friendly_name();
        //alert("111");
        //alert(xqxstr);
        //取的是oudn  ou=海信测试组 ,dc=test,dc=com
        var xqx_oudn = contact_rightList.oudn();
        //alert("222");
        //alert(xqx_oudn);
        var xzhContent = document.getElementById("txqxContent");
        //判断ou是否有效
        var qx_valid = is_qx_valid(xqxstr,"txqxContent");
        if(qx_valid==0){
            //父容器div
            var qx_item = create_new_qx_item(xqxstr,xqx_oudn);
            xzhContent.appendChild(qx_item);
            //alert(xzhContent);

        }
        else if(qx_valid==-1){
            alert("已经添加了相同或更高级权限，请重新选择");
//            resetAddAdminLog();
        }
        else{
            if(confirm("您的列表中已经有子权限，是否选择覆盖")==true){
                //覆盖子权限
                var qx_lables = $("#txqxContent .qxlabel");
                for(var i=0;i<qx_lables.length;i++){
                    var item_oudn = $(qx_lables[i]).attr("oudn");
                    if(item_oudn.indexOf(xqx_oudn)>=0){
                        var parent_div = qx_lables[i].parentNode;
                        xzhContent.removeChild(parent_div);
                    }
                }
                var new_qx_item = create_new_qx_item(xqxstr,xqx_oudn);
                xzhContent.appendChild(new_qx_item);
            }
        }
    }
});
//+++20151023 检查是否存在该权限或者是更高级权限
function is_qx_valid(qx_str,list_container){
    var result = 0;
    $("[id='"+list_container+"'] .qxlabel").each(function(index,element){
        var qx = element.innerHTML;
        if(qx=="所有用户"){
            result = -1;
        }else{
            if(qx_str.indexOf(qx)==0){
                result = -1;//新权限包含在旧权限之内，操作重复
            }else if(qx.indexOf(qx_str)==0){
                result = 1;//旧权限包含在新权限之内，询问是不是覆盖
            }
        }
    });
    return result;//权限不冲突，可以添加
}

function create_new_qx_item(xqxstr,xqx_oudn){
    var parent = document.createElement("DIV");
    var contentLabel = document.createElement("LABEL");
    contentLabel.className="qxlabel";
    contentLabel.innerHTML = xqxstr;
    $(contentLabel).attr("oudn",xqx_oudn);
    parent.appendChild(contentLabel);

    //加一个移除权限的标签
    var del_buttuon = document.createElement("BUTTON");
    del_buttuon.innerHTML = "移除";
    del_buttuon.className = "inline_button";
    $(del_buttuon).click(function(event){
        event.preventDefault();
        var contact_ous_content = event.target.parentNode.parentNode;
        var parent_span = event.target.parentNode;
        contact_ous_content.removeChild(parent_span);
    });
    parent.appendChild(del_buttuon);
    return parent;
}


$("#xtxqx").submit(function(event){
    event.preventDefault();
    var txqx_items = $("#txqx_list .qxlabel");
    if(txqx_items.length==0){
        alert("通信权限不能为空");
        return;
    }else{
        var oudn_list = [];
        for(var i=0;i<txqx_items.length;i++){
            oudn_list.push($(txqx_items[i]).attr("oudn"));
        }

        var obj={
            _path:"/a/wp/org/admin_contact_ous",
            _methods:"post",
            param:{
                sid:$.cookie("org_session_id"),
                type:"set",
                oudn_list:JSON.stringify(oudn_list)
            }
        };
        ajaxReq(obj,function(data){
            if(data.rt==0){
                loadingStatus("修改通信权限成功！");
            }else{
                loadingStatus("修改通信权限失败！");
                alert("管理员添加失败！");
            }
        },"正在提交...");
    }
});