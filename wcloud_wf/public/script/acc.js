/**
 * Created by Seren on 14-4-22.
 */
//实现账户页面的切换
var ldap_base_dn = "dc=test,dc=com";
var contact_rightList = null;
var right_list = null;
var add_user_right_list = null;
var operator_right_list = null;
//ye页面转huan
$(".asideU .tab").click(function(event){
    event.preventDefault();
    //隐藏所有section
    $("section").hide();
    //获取用户点击的连接值
    var href=$(this).attr("href");
    //一些全局变量的初始化
    var sid=$.cookie("org_session_id");
//    var qx=$("#adminqx").attr("oudn");
    var qx=ldap_base_dn;
    var uid=$.cookie("userid");
    //获取初始options
    var txt=loadous(sid,qx);
    var loginType = $.cookie("loginType");

    if(href=="#addgly"){//用户点击管理员section
        //将以前有的选项残留删除
        resetAddAdminLog();
//        if(!right_list){
//            right_list = new RightList("xzhqxbm",[qx]);
//        }

    }
    else if(href=="#addyh"){
        resetAddUserLog();
        //+++20151016 要实现多总管理员，不能通过用户名判断权限
        if(!add_user_right_list){
            add_user_right_list = new RightList("addbm",[qx]);
        }
    }
    else if(href=="#addczy"){
        if(!operator_right_list){
            operator_right_list = new RightList("gxfw",[qx]);
        }
        //当添加管控权限的时候默认添加为通信权限
        $("#gxfw select").bind("change",function(event){

            var admin_oudn = operator_right_list.oudn();
            var xzhContent = document.getElementById("txqxContent");
            //首先清空通信权限列表
            xzhContent.innerHTML = "";
            if(admin_oudn!=""){
                //将获取到的管控权限添加到通信权限列表
                var xqxstr = operator_right_list.right_friendly_name();
                var qx_item = create_new_qx_item(xqxstr,admin_oudn);
                //将该条目的移除button禁用
                qx_item.getElementsByTagName("button")[0].disabled = true;
                xzhContent.appendChild(qx_item);
            }

        });
        if(!contact_rightList){
            contact_rightList = new RightList("txqxbm",[ldap_base_dn]);
        }
    }
    else if(href=="#addsjy"){
        if(loginType != "auditor")
        {
            document.getElementById("auzhqx").disabled = true;
        }
        else
        {
            document.getElementById("auzhqx").disabled = false;
        }
    }
    else if(href=="#addaqy"){
        if(loginType != "sa")
        {
            document.getElementById("sazhqx").disabled = true;
        }
        else
        {
            document.getElementById("sazhqx").disabled = false;
        }
    }
    $(href).show();
    $(".asideU .tab").removeClass("hover");
    $(this).addClass("hover")
});
//+++20151020 初始化时添加需要的ou
function append_selects(span_id,first_select,qx){
    var span = document.getElementById(span_id);
    var ou_names = qx.split(",");
    var oudn = ldap_base_dn;
    var first_select = document.getElementById(first_select);
    first_select.innerHTML = "";
    //+++20151021 配置第一个select的内容
    first_select.options.add(new Option(ou_names[0],ou_names[0]));
    first_select.className = oudn;

    oudn = "ou="+ou_names[0]+","+ oudn;
    //+++20151021 循环添加后面的select
    for(var i=1;i<ou_names.length;i++){
        var select_id = "st"+oudn;
        var select = document.createElement("SELECT");
        select.className = oudn;
        select.id = "st"+ oudn;
        var initOption = new Option(ou_names[i],ou_names[i]);
        select.options.add(initOption);
        span.appendChild(select);
        if(i==ou_names.length-1){
            loadnextous(select);
        }
        oudn = "ou="+ou_names[i]+oudn;
    }
}

//+++20151020 根据权限字符串获取dn
function get_admin_oudn(qx){
    var oudn = "";
    if(qx.indexOf(",")>=0){
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
function loadous(sid,oudn){
    var obj={
        _path:"/a/wp/org/ldap_onelevel",
        _methods:"get",
        param:{
            sid:sid,
            oudn:oudn
        }
    };
    var txt="";
    ajaxReq1(obj,function(data){
        //console.log(data);
        var ous=data.ous;
        if(data.rt==0){
            for(var i=0;i<ous.length;i++)
            {
                txt+="<option oudn='"+ous[i].dn+"' value='"+ous[i].ou+"'>"+ous[i].ou+"</option>";
            }
        }else{
        }
    },"");
    return txt;
}
//每点击一次加载下一级的群组
function loadnextous(element){
    var span = document.getElementById(element.id).parentNode;
    var seletes=span.children;
    var classname=element.className;
    //删除其后的所有兄弟节点后退出
    for(var i=seletes.length-1;i>0;i--)
    {
        if(seletes[i].className.indexOf(classname)>0)
        {
            span.removeChild(seletes[i]);
        }
    }
    if(element.value == "请选择")
    {
       return;
    }
    var oudn="ou="+element.value+","+element.className;
    var txt="";
    var obj={
        _path:"/a/wp/org/ldap_onelevel",
        _methods:"get",
        param:{
            sid:$.cookie("org_session_id"),
            oudn:oudn
        }
    };
    ajaxReq1(obj,function(data){
        var ous=data.ous;
        if(ous.length>0)
        {
            var st="<select onchange='loadnextous(this)' class='"+oudn+"' id='st"+oudn+"'></select>";
            $("span[id='"+span.id+"']").append(st);
            if(data.rt==0){
                document.getElementById("st"+oudn).options.add(new Option("请选择","请选择"));
                for(var i=0;i<ous.length;i++)
                {
                    document.getElementById("st"+oudn).options.add(new Option(ous[i].ou,ous[i].ou));
                }
            }
        }
        else{
            span = document.getElementById(element.id).parentNode;
//           alert(span.lastChild.className);
        }
    },"");
}
//隐藏的选项卡滑下的动作
$(".ra").click(function(event){
    var parent=$(this).parent();
    var yc=$(".yc",parent);
    yc.slideDown("fast");
});
//提交或者关闭的时候收上选项卡。
$(".yc .an button.err").click(function(event){
    var yc=$(this).parent().parent().parent();
//	$("input[type='text']").val("");
//	$("input[type='password']").val("");
    yc.slideUp("fast");
});
//修改企业信息的代码。
$("#dwmc").submit(function(event){
    event.preventDefault();
    var dwm=$("#dwm");
    if(!verViod(dwm.val())){
        loadingStatus("企业名不能为空!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/org_info",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            org_name:dwm.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("提交成功!",0);
            $("#dwmc").parent().slideUp("fast");
            dwm.val("");
        }else{
            loadingStatus("提交失败!",0);
        }
    },"正在提交...")
});
//修改企业地址
$("#addr").submit(function(event){
    event.preventDefault();
    var xadd=$("#xadd");
    if(!verViod(xadd.val())){
        loadingStatus("企业地址不能为空!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/org_info",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            org_addr:xadd.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("提交成功!")
            $("#addr").parent().slideUp("fast");
            xadd.val("");
        }else{
            loadingStatus("提交失败!",0);
        }
    },"正在提交...")
});
//修改手机号码
$("#shh").submit(function(event){
    event.preventDefault();
    var hm=$("#hm");
    if(!verViod(hm.val())){
        loadingStatus("手机号码不能为空!");
        return false;
    }
    var obj={
        _path:"/a/wp/org/org_info",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            admin_pnumber:hm.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("提交成功!",0);
            $("#shh").parent().slideUp("fast");
            hm.val("");
        }else{
            loadingStatus("提交失败!",0);
        }
    },"正在提交...");
});
//修改邮箱
$("#adyx").submit(function(event){
    event.preventDefault();
    var xyx=$("#xyx");
    if(!verViod(xyx.val())){
        loadingStatus("邮箱不能为空!")
        return false;
    }
    var obj={
        _path:"/a/wp/org/org_info",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            admin_email:xyx.val()
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            loadingStatus("提交成功!",0);
            $("#adyx").parent().slideUp("fast");
            xyx.val("");
        }else{
            loadingStatus("提交失败!",0);
        }
    },"正在提交...");
});
//修改密码
$("#xmim").submit(function(event){
    event.preventDefault();
    var dma=$("#dma");
    var xma=$("#xma");
    var qxma=$("#qxma");
    if(!verViod(dma.val())){
        alert("当前密码不能为空!");
        return false;
    }
    if(!verViod(xma.val())){
        alert("新密码不能为空!");
        return false;
    }
    if(!verViod(qxma.val())){
        alert("确认密码不能为空!");
        return false;
    }
    if(xma.val()!=qxma.val()){
        loadingStatus("两次密码不一致!");
        return false;
    }
    if(!checkpwrule(xma.val())){
        alert("密码至少为15位且必须为字母数字特殊符号的组合！");
        return false;
    }
    if(xma.val().length>30){
        alert("密码长度不得超过30位！");
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
            $("#xmim").parent().slideUp("fast");
            dma.val("");
            xma.val("");
            qxma.val("");
            loadingStatus("密码已修改,请重新登陆！");
            alert("密码已修改,请重新登陆！");
            relogin();
        }else if(data.rt==18){
            alert("密码至少为15位且必须为字母数字特殊符号的组合!");
            loadingStatus("新密码不符合规则!");
        }else if(data.rt=19){
            loadingStatus("旧密码输入错误！");
            alert("旧密码输入错误!");
        }
    },"正在提交...");
});
//添加用户
$("#adduser").submit(function(event){
    event.preventDefault();
    var username=$("#uname").val();
    var email = $("#umail").val();
    var pnumber=$("#uphone").val();
    var zhiW = $("#uzhiw").val();
    var zhiC = $("#uzhic").val();
    var mobile = 'Y';
    var pw1='12345678';
    var pw2='12345678';
    //姓名监测
    if(!verViod(username)){
        alert("用户名不能为空!");
        return false;
    }else if(username.TextFilter()!=username){
        alert("用户名不得含有特殊字符！");
        return false;
    }else if(username.length>6){
        alert("用户名不应超过6个字符！");
        return false;
    }
    //邮箱监测
//    if(!verViod(email)){
//        alert("邮箱不能为空!");
//        return false;
//    }
    if(email!=""){
        if (!checkemail(email)){
            alert("邮箱格式不对!");
            return false;
        }
    }
    //监测两次密码是否一样
    if(!verViod(pw1)){
        alert("密码不能为空!");
        return false;
    }
    if(!verViod(pw2)){
        alert("确认密码不能为空!");
        return false;
    }
    if(pw1!=pw2){
        alert("两次密码不一致!");
        $("#xzhmm2").val("");
        return false;
    }
    //检验电话号码
    var reg = new RegExp('^[1][3-8]+\\d{9}')
    if(pnumber.length<11 || !reg.test(pnumber))
    {
        alert("电话号码无效！");
        return false;
    }
    //构造职位/职称 +++20151020 改构造title的函数
    var title=generateTitle(zhiW,zhiC);
//    alert(title);
    //判定所属部门
    var oudn = add_user_right_list.oudn();

    var obj={
        _path:"/a/wp/org/ldap_add_user",
        _methods:"post",
        param:{
            sid:$.cookie("org_session_id"),
            username:username,
            pw:pw1,
            email:email,
            mobile:mobile,
            pnumber:pnumber,
            title:title,
            dn:oudn
        }
    };
    ajaxReq(obj,function(data){
        //console.log(data);
        if(data.rt==0){
            sessionStorage.clear();   //******************************//
            alert("用户添加成功！");
            $("#uname").val("");
            $("#umail").val("");
            $("#uphone").val("");
            $("#uzhiw").val("");
            $("#uzhic").val("");
//            $("#uldapsq").val();
//            $("#upw1").val("");
//            $("#upw2").val("");
//            $("#uldapou").val("请选择");
            resetAddUserLog();
            if($("#adminqx").html().indexOf(",")>0){
                append_selects("addbm","uldapou",qx);
            }
        }
        else if(data.rt == 12){
//            loadingStatus("该设备已被注册！");
            alert("该设备已被注册！");
        }
        else {
//            loadingStatus("用户添加失败！");
            alert("用户添加失败！");
        }

    });
});
//判断输入姓名是否合法
function legalJudgeName(name,nameid){
    var adminID = $(name).val();
    var a=nameid
    var a1= a.substr(1);
    //检测一下用户名是否合法
    if(adminID.trim()==""){
        $(nameid).html("");
    }
    //20161013添加|| adminID 使得在无输入时，失去焦点，判定为---用户名不能为空
    if(adminID ==""){
        addColoredText(a1, "用户名不得为空!", "red")
    }else{
        if(adminID.TextFilter()!= adminID) {
            addColoredText(a1, "用户名不得含有特殊字符!", "red")
        }else{
            addColoredText(a1,"该用户名合法!","blue");
        }
    }
}
//判断输入邮箱是否合法
function legalJudgeMail(mail,mailid){
    var adminEM = $(mail).val();
    //检测一下用户名是否合法
    var a=mailid;
    var a1= a.substr(1);
    if(adminEM.trim()==""){
        $(mailid).html("");
    }
    if(!checkemail(adminEM)) {
        addColoredText(a1, "邮箱格式不对！", "red")
    }else{
        addColoredText(a1,"邮箱格式正确！","blue");
    }
}
//判断输入电话是否合法
function legalJudgePhone(phone,phoneid){
    var pnumber=$(phone).val();
    var a=phoneid;
    var a1= a.substr(1);
    if(pnumber.trim()==""){
        $(phoneid).html("");
    }
    //var reg = new RegExp('^[1][3-8]+\\d{9}');
    if (!checkphone(pnumber)) {
        addColoredText(a1, "电话号码格式无效!", "red");

    } else {
        addColoredText(a1, "电话号码格式正确!", "blue");
        //check_is_has_user(pnumber);
    }
}
//操作员添加用户姓名判断是否合法
$("#uname").blur(function(){
    legalJudgeName("#uname","#adminIDLog");
});
//操作员添加用户邮箱判断是否合法
$("#umail").blur(function(){
    legalJudgeMail("#umail","#adminEMLog");
});
//操作员添加用户电话判断是否合法
$("#uphone").blur(function(){
    legalJudgePhone("#uphone","#uphoneLog");
});

function checkphone(phone){
    var reg = new RegExp('^[1][3-8]+\\d{9}');
    if( (!reg.test(phone))||(phone.length<11))
        return false;
    return true;
}

//+++20151020 构造title的函数
function generateTitle(zhiW,zhiC){
    var title = "";
    if (zhiW == "")
    {
        if (zhiC == "")
            title = "";
        else
            title = zhiC;
    }
    else
    {
        if (zhiC == "")
            title = zhiW;
        else
            title = zhiW+'/'+zhiC;
    }
    return title;
}
//+++20151020 获取用户所在群组
function getUserOus(selects){
    var ou = [];
    for(var i=selects.length-1;i>=0;i--)
    {
        if(selects[i].value != "请选择")
        {
            var selected = selects[i].value;
//            +++20151013正常逻辑
//            ou.push("ou="+selects[i].value);
            if(selected.indexOf(",")>=0){
                for(var j=selected.split(",").length-1;j>=0;j--){
                    ou.push("ou="+selected.split(",")[j]);
                }
            }else{
                ou.push("ou="+selects[i].value);
            }
        }
    }
    return ou;
}
//+++20151012 添加用户成功之后将外边的提示置空
function resetAddUserLog(){
    $("#uphoneLog").html("");
    if(add_user_right_list){
        add_user_right_list.reset();
    }
}
//+++20151012 添加管理员成功之后将输入框中的内容和外边的提示置空
function resetAddAdminLog(){
    $("#adminIDLog").html("");
    $("#adminPwLog").html("");
    $("#ensureLog").html("");
    if(contact_rightList){
        contact_rightList.reset();
    }
    if(right_list){
        right_list.reset();
    }
    $("#txqxContent").html("");
}
//
function resetAddMasterLog(){
    $("#xzh").val("");
    $("#xzhmm1").val("");
    $("#xzhmm2").val("");
    $("#xzhmail").val("");
    $("#xzhphone").val("");
    $("#xzhqx").val("请选择");
}



function check_is_has_user(uid){
    var obj = {
        _path:"/a/wp/org/check_is_has_user",
        _methods:"get",
        param:{
            sid: $.cookie("org_session_id"),
            uid:uid
        }
    };
    ajaxReq(obj,function(data){
//        console.log(data);
        var rt = data.rt;
        if(rt==0){
            var result = data.result;
//            console.log("check is has user result"+result);
            if(result.toString()=="1"){
                addColoredText("uphoneLog","该号码已被注册，请重新选择号码!","red");
            }else{
                addColoredText("uphoneLog","该号码可以使用!","blue");
            }
        }
    });
}


//添加管理员
$("#addmanager").submit(function(event){
    event.preventDefault();

    var uid=$("#xzh").val();
    var pw1=$("#xzhmm1").val();
    var pw2=$("#xzhmm2").val();
    var email=$("#xzhmail").val();
    var phonenumber=$("#xzhphone").val();
    var ou= $("#xzhqx").val();

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
    if(ou=="请选择")
    {
        loadingStatus("操作员权限不能为空！");
        return false;
    }

    //存入数据库（用于login检测）
    var obj={
        _path:"/a/wp/org/add_master",
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
            loadingStatus("管理员添加成功");
            resetAddMasterLog();
        }
        else if(data.rt==12){
            loadingStatus("管理员已存在");
        }
    },"正在提交...");

});

Array.prototype.in_array = function(e){
    for(var i=0;i<this.length;i++)
    {
        if(this[i] == e)
            return true;
    }
    return false;
};

function get_admin_contact_ous(ou,target_id){
    //ou是该管理员的管控权限，在此与通信权限进行对比
    var content = document.getElementById(target_id);
    var items = $(".qxlabel",content);
    var oudns = new Array();
    for(var i=0;i<items.length;i++){
        var oudn = $(items[i]).attr("oudn");
        if(oudn.indexOf(ou)>=0){
            if(!oudns.in_array(ou)){
                oudns.push(ou);
            }
        }else{
            oudns.push(oudn);
        }
    }
    return oudns;
}

function show_contact_ous(admin_contact_ous,admin_right){
    var txqx_list_str = "";
    for(var i=0;i<admin_contact_ous.length;i++){
        if(admin_contact_ous[i]==admin_right){continue;}
        else{
            var qx_item = create_new_qx_item(get_oudn_name(admin_contact_ous[i]),admin_contact_ous[i]);
            $("#txqx_list")[0].appendChild(qx_item);
            txqx_list_str+=get_oudn_name(admin_contact_ous[i])+"——";
        }
    }
    txqx_list_str = txqx_list_str.substr(0,txqx_list_str.length-2);
    $("#admintxqx").html(txqx_list_str);
//    mod_txqx_list = new RightList("mod_txqx",[ldap_base_dn]);
    //将通信权限中管理权限条目禁止移除
    var glqx_item = $("#txqx_list [oudn='"+admin_right+"']")[0];
    if(glqx_item){
        //将管理权限对应的条目button禁用
        glqx_item.parentNode.childNodes[1].disabled = true;
    }
}

function checkpwrule(pw){
    var hasLetter = new RegExp("[a-zA-Z]");
    var hasNum = new RegExp("[0-9]");
    var hasSymbol = new RegExp("[~!@#$%^&*()-+_=:?,.]");
    if(pw.length<15 || !hasLetter.test(pw) || !hasNum.test(pw) || !hasSymbol.test(pw))
    {
        return false;
    }else{
        return true;
    }
}

function checkemail(email){
    var rg = new RegExp('^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])');
    if( !rg.test(email))
         return false;
    return true;
}

//+++ 20150608 修改密码重新登录
function relogin(){
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
        if(rt==0){
            sessionStorage.clear();
            loadingStatus("正在退出...",0);
            $.cookie("org_session_id",null);
            $.cookie("configStatus",null);
            location.href="/f_org_login";
        }else{
            loadingStatus("操作失败!",0);
        }
    },"正在退出...");
}

//+++20150828 失去焦点时去数据库检查当前密码输入是否正确
$("#dma").blur(function(event){
    var dma = $("#dma").val();
    if(dma.trim()==""){
        $("#dmaLog").html("");
    }else{
        var sid = $.cookie("org_session_id");
        var obj = {
            _path:"/a/wp/org/check_old_psw",
            _methods:"get",
            param:{
                sid:sid,
                psw:dma
            }
        };
        ajaxReq(obj,function(data){
            var rt = data.rt;
            if(rt==0){
                var result = data.result;
                //console.log("查看旧密码的结果"+result);
                if(result.toString()=="1"){
                    addColoredText("dmaLog","当前密码输入正确，可以修改密码！","blue");
                }else{
                    addColoredText("dmaLog","当前密码输入错误，请重新输入！","red");
                }
            }
        });
    }

});
//判断新密码输入合法性
var xmaValid = false;
$("#xma").keyup(function(event){
    var psw = $("#xma").val();
    if(!checkpwrule(psw)){
        addColoredText("xmaLog","密码至少为15位且必须为字母数字特殊符号的组合！","red");
        xmaValid = false;
//        $("#qxma").attr("readOnly",true);
    }else{
        if(psw.length>30){
            addColoredText("xmaLog","密码长度不要超过30位！","red");
            xmaValid = false;
//            $("#qxma").attr("readOnly",true);
        }else{
            addColoredText("xmaLog","密码合法！","blue");
            xmaValid = true;
//            $("#qxma").attr("readOnly",false);
        }
    }
});

$("#xma").blur(function(){
    var psw = $("#xma").val();
    if(psw.trim()==""){
        $("#xmaLog").html("");
    }
});
var sameInput = false;


$("#qxma").keyup(function(event){
    var psw = $("#xma").val();
    var pswEnsure = $("#qxma").val();
    if(psw!=""&&pswEnsure!=psw){
        addColoredText("qxmaLog","两次输入密码不一致，请重新输入!","red");
        sameInput = false;
    }else{
        addColoredText("qxmaLog","两次输入密码一致!","blue");
        sameInput = true;
    }
});


$("#qxma").blur(function(){
    var pswEnsure = $("#qxma").val();
    if(pswEnsure.trim()==""){
        $("#qxmaLog").html("");
    }else{
        if(!sameInput){
            addColoredText("qxmaLog","两次输入密码不一致，请重新输入!","red");
        }
    }
});

function addColoredText(labelID,text,color){
    $("label[id='"+labelID+"']").html(text);
    $("label[id='"+labelID+"']").css({"color":color});
}

//#########################################三元分立##########################################
//20161013---三元分立添加管理员用户名
$("#xzh").blur(function(){
    //取出当前值
    var adminID = $("#xzh").val();
    //检测一下用户名是否合法
    if(adminID.trim()==""){
        $("#adminIDLog").html("");
    }
    if(adminID==""){
        addColoredText("adminIDLog","用户名不得为空!","red");
    }else{
        if(adminID.TextFilter()!=adminID){
            addColoredText("adminIDLog","用户名不得含有特殊字符!","red");
        }else{
            //去后台检测一下是否存在该用户名
            var sid = $.cookie("org_session_id");
            var obj = {
                _path:"/a/wp/org/is_has_admin",
                _methods:"post",
                param:{
                    sid:sid,
                    adminID:adminID
                }
            };
            ajaxReq(obj,function(data){
                var rt = data.rt;
                if(rt==0){
                    var result = data.result;
                    //console.log("返回结果值为:"+result);
                    if(result.toString()=="1"){
                        addColoredText("adminIDLog","用户名已存在!","red");
                    }else{
                        addColoredText("adminIDLog","该用户名合法!","blue");
                    }
                }
            });
        }
    }
});
//20161013---三元分立添加管理员第一次输入密码
var xzhmmValid = false;
$("#xzhmm1").keyup(function(event){
    var psw = $("#xzhmm1").val();
    if(!checkpwrule(psw)){
        addColoredText("adminPwLog","密码至少为15位且必须为字母数字特殊符号的组合！","red");
        xzhmmValid = false;
//        $("#xzhmm2").attr("readOnly",true);
    }else{
        if(psw.length>30){
            addColoredText("adminPwLog","密码长度不要超过30位！","red");
            xzhmmValid = false;
//            $("#xzhmm2").attr("readOnly",true);
        }else{
            addColoredText("adminPwLog","密码合法！","blue");
            xzhmmValid = true;
//            $("#xzhmm2").attr("readOnly",false);
        }
    }
});
$("#xzhmm1").blur(function(){
    var psw = $("#xzhmm1").val();
    if(psw.trim()==""){
        $("#adminPwLog").html("");
    }
    if (psw==""){
        addColoredText("adminPwLog","密码不能为空！","red");
    }
});
var xzhSameInput = false;
//20161013---三元分立添加管理员密码确认
$("#xzhmm2").keyup(function(event){
    var psw = $("#xzhmm1").val();
    var pswEnsure = $("#xzhmm2").val();
    if(psw!=""&&pswEnsure!=psw){
        addColoredText("ensureLog","两次输入密码不一致，请重新输入!","red");
        xzhSameInput = false;
    }else{
        addColoredText("ensureLog","两次输入密码一致!!","blue");
        xzhSameInput = true;
    }
});
$("#xzhmm2").blur(function(){
    var pswEnsure = $("#xzhmm2").val();
    if(pswEnsure.trim()==""){
        $("#ensureLog").html("");
    }
    if(pswEnsure==""){
        addColoredText("ensureLog","确认密码不能为空！" ,"red");
    }
});
//20161013---三元分立添加管理员手机号
$("#xzhphone").blur(function(){
    //触发被选元素的 blur 事件
    //$(selector).blur()
    //$.trim()去掉字符串首尾空格。
    var pnumber=$("#xzhphone").val();
    var reg = new RegExp('^[1][3-8]+\\d{9}');
    if (pnumber==""){
        addColoredText("uphoneLog", "电话号码不能为空!", "red")
    }else{
        if (!checkphone(pnumber)) {
            addColoredText("uphoneLog", "电话号码格式无效!", "red");
        } else {
            addColoredText("uphoneLog", "电话号码格式正确!", "blue");
            check_is_has_user(pnumber);
        }
    }
});
//20161013---三元分立添加管理员邮箱
$("#xzhmail").blur(function(){
    //取出当前值
    var adminEM = $("#xzhmail").val();
    //检测一下用户名是否合法
    if(adminEM.trim()==""){
        $("#adminEMLog").html("");
    }
    if(!checkemail(adminEM)) {
        addColoredText("adminEMLog", "邮箱格式不对！", "red")
    }else{
        addColoredText("adminEMLog","邮箱格式正确！","blue");
    }
});
//20161013---三元分立添加操作员姓名
$("#adname").blur(function(){
    //取出当前值
    var adminID = $("#adname").val();
    //检测一下用户名是否合法
    if(adminID.trim()==""){
        $("#adIDLog").html("");
    }
    if(adminID==""){
        addColoredText("adIDLog", "用户名不得为空!", "red")
    }else{
        if(adminID.TextFilter()!=adminID) {
            addColoredText("adIDLog", "用户名不得含有特殊字符!", "red")
        }else{
            addColoredText("adIDLog","该用户名合法!","blue");
        }
    }

});
//20161013---三元分立添加操作员第一次输入密码
var xzhmmValid = false;
$("#adpw1").keyup(function(event){
    var psw = $("#adpw1").val();
    if(!checkpwrule(psw)){
        addColoredText("adPwLog","密码至少为15位且必须为字母数字特殊符号的组合！","red");
        xzhmmValid = false;
//        $("#xzhmm2").attr("readOnly",true);
    }else{
        if(psw.length>30){
            addColoredText("adPwLog","密码长度不要超过30位！","red");
            xzhmmValid = false;
//            $("#xzhmm2").attr("readOnly",true);
        }else{
            addColoredText("adPwLog","密码合法！","blue");
            xzhmmValid = true;
//            $("#xzhmm2").attr("readOnly",false);
        }
    }
});
$("#adpw1").blur(function(){
    var psw = $("#adpw1").val();
    if(psw.trim()==""){
        $("#adPwLog").html("");
    }
    if(psw==""){
        addColoredText("adPwLog","密码不能为空！","red");
    }
});
//20161013---三元分立添加操作员密码确认
$("#adpw2").keyup(function(event){
    var psw = $("#adpw1").val();
    var pswEnsure = $("#adpw2").val();
    if(psw!=""&&pswEnsure!=psw){
        addColoredText("adLog","两次输入密码不一致，请重新输入!","red");
        xzhSameInput = false;
    }else{
        addColoredText("adLog","两次输入密码一致!!","blue");
        xzhSameInput = true;
    }
});
$("#adpw2").blur(function(){
    var pswEnsure = $("#adpw2").val();
    if(pswEnsure.trim()==""){
        $("#adLog").html("");
    }
    if(pswEnsure==""){
        addColoredText("adLog","确认密码不能为空！","red");
    }
});
//20161013---三元分立添加操作员邮箱
$("#admail").blur(function(){
    //取出当前值
    var adminEM = $("#admail").val();
    //检测一下用户名是否合法
    if(adminEM.trim()==""){
        $("#adEMLog").html("");
    }
    if(!checkemail(adminEM)) {
        addColoredText("adEMLog", "邮箱格式不对！", "red")
    }else{
        addColoredText("adEMLog","邮箱格式正确！","blue");
    }
});
//20161013---三元分立添加操作员手机号
$("#adphone").blur(function(){
    //触发被选元素的 blur 事件
    //$(selector).blur()
    //$.trim()去掉字符串首尾空格。
    var pnumber=$("#adphone").val();
    var reg = new RegExp('^[1][3-8]+\\d{9}');
    if(pnumber==""){
        addColoredText("aduphoneLog", "电话号码不能为空!", "red");
    }else{
        if (!checkphone(pnumber)) {
            addColoredText("aduphoneLog", "电话号码格式无效!", "red");
            //console.log("111111111111111");
        } else {
            addColoredText("aduphoneLog", "电话号码格式正确!", "blue");
            check_is_has_user(pnumber);
        }
    }
});
