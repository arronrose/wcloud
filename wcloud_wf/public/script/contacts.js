/**
 * Created by GCY on 2016/1/7.
 */
var contactsPerPageGlobal=20;
//***从内存中加载
function showTree() {
    var obj = {
        //input:
        //    sid: sesssion id
        //output:
        //    rt: error code
        //    dn: oudn
        //    contacts: [...]
        //
        _path: "/a/wp/org/ldap_get_ou_by_sid",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        //rootdn即管理权限：ou=海信测试群组,dc=test,dc=com
        var rootdn = data.dn;
        //rootcon即通信权限：["ou=海信测试群组,dc=test,dc=com"]
        var rootcon = data.contacts;
        //+++ 20150731 确保用户unchecked
        for(var i=0;i<rootcon.length;i++) {
            changeContactSelectedUsersUidHideTree(rootcon[i],rootdn, "contact del", "ou");
        }
        var ou = rootdn.split(",")[0].split("=")[1];
        //console.log(ou);ou:海信测试群组
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            loadingStatus("成功获取用户信息！", 0);
            var initNode = "";
            //判断管理权限是否为所有用户
            if (rootdn.split(",")[0].split("=")[0] == "dc") {
                //此函数并没有用到

                ou = '所有用户';
                initNode += '<div class="div_label">';
                //勾选框
                initNode += '<span id="' + "out:" + rootdn + '"class="checkbox checkbox_uncheck" onclick="select_ou_node(this.id)"></span>';
                //图标
                initNode += '<img src="images/group.png"/>';
                //超链接到管理权限的人员列表
                initNode += '<a href="javascript:;" title="t' + rootdn + '" onclick="showContactDiv(this.title)">';
                initNode += ou;
                initNode += '</a>';
                initNode += '</div>';
                //下拉框的管理权限列表展示
                initNode += '<div class="div_container" id="t' + rootdn + '">';
            } else {

                //在管理权限不是所用用户的情况下，管理权限不是所有用户的条件下
                for(var i=0;i<rootcon.length;i++){
                    // 取通信权限列表里的 每一个ou的值
                    var con = rootcon[i].split(",")[0].split("=")[1];
                    //判断通信权限是否为所有用户，con:海信测试群组
                    if (rootcon[i].split(",")[0].split("=")[0] == "dc") {
                        con = '所有用户';
                    }
                    initNode += '<div class="div_label">';
                    //勾选框
                    initNode += '<span id="' + "out:" + rootcon[i] + '" value="' + rootdn + '" class="checkbox checkbox_uncheck" onclick="select_ou_node_uid_hide(this)"></span>';
                    //图标
                    initNode += '<img src="images/group.png"/>';
                    //超链接到管理权限的人员列表（通信权限的名字，管理权限的值）
                    initNode += '<a href="javascript:;" title="t' + rootcon[i] + '" value="' + rootdn + '" onclick="showContactDivUidHide(this)">';
                    initNode += con;
                    initNode += '</a>';
                    initNode += '</div>';
                    //下拉框的通信权限列表展示（通信权限）
                    initNode += '<div class="div_container" id="t' + rootcon[i] + '"/>';
                }
            }
            $("#tree").html(initNode);
        }
    }, "正在获取用户信息!");
}

function showContactDiv(title) {
    var content = document.getElementById(title).innerHTML;
    //console.log(content);
    var oudn = title;
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,title.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel",
            _methods: "get",
            param: {
                oudn: oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq(obj, function (data) {
            var rt = data.rt;
            if (rt != 0) {
                loadingStatus("获取用户信息失败！", 0);
            } else {
                loadingStatus("成功获取用户信息！", 0);
                var sons = showContactOuSons(data);
                document.getElementById(title).innerHTML = sons;	//添加一个账户
            }
        }, "正在获取用户信息!");
    } else {
        //控制群组的展开和闭合
        var div = document.getElementById(title);
        if (div.style.display == "none") {
            div.style.display = "block";
        }
        else {
            div.style.display = "none";
        }
    }
}
function showContactOuSons(all) {
    var html = "";
    loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['dn'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("out:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div class="div_label">';
        html += '<span id="' + "out:" + dn + '"class="' + checkStatus + '" onclick="select_ou_node(this.id)"></span>';
        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="t' + dn + '" onclick="showContactDiv(this.title)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div class="div_container" id="t' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '" class="user_node">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "ust:" + users[j]['dn'] +
            '" class="' + checkStatus + '"  onclick="select_user_node(this,this.title,this.id)"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' +
            "ust:" + users[j]['dn'] + '" title="' + users[j]['uid'] + '" href="javascript:;" ' +
            'onclick="select_user_node(this,this.title,this.name)">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}
//20161008展开要下发联系人列表的隐藏项（即其所包含的具体用户列表）
function showContactDivUidHide(element) {
    //title="t' + rootcon[i] + '"
    var oudn = element.title;
    //value=rootdn
    var rootdn = $(element).attr("value");
    ////tou=海信测试群组,dc=test,dc=com
    //console.log(oudn);
    ////ou=通信权限测试组，dc=test,dc=com
    //console.log(rootdn);
    var content = document.getElementById(element.title).innerHTML;
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,element.title.length-1);
        //console.log("######"+oudn);
        //######ou=海信测试群组,dc=test,dc=com
    }
    if (content == "") {
        //console.log("content里面内容为空");
        var obj = {
            _path: "/a/wp/org/ldap_onelevel_uid_hide",
            _methods: "get",
            param: {
                oudn:rootdn,
                contacts:oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq(obj, function (data) {
            //console.log(data);
            var rt = data.rt;
            //console.log(rt);
            if (rt != 0) {
                loadingStatus("获取用户信息失败！", 0);
            } else {
                loadingStatus("成功获取用户信息！", 0);
                var sons = showContactOuSonsUidHide(data);
                //console.log(sons);
                document.getElementById(element.title).innerHTML = sons;	//添加一个账户
            }
        }, "正在获取用户信息!");
    } else {
        //控制群组的展开和闭合
        var div = document.getElementById(element.title);
        if (div.style.display == "none") {
            div.style.display = "block";
        }
        else {
            div.style.display = "none";
        }
    }
}
//点击下发联系人列表的群组名所触发的函数
function showContactOuSonsUidHide(all) {
    var html = "";
    loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['oudn'];
    var dn = all['contacts'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("out:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div class="div_label">';
        html += '<span id="' + "out:" + dn + '" value="' + rootdn + '" class="' + checkStatus + '" onclick="select_ou_node_uid_hide(this)"></span>';
        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="t' + dn + '" value="' + rootdn + '" onclick="showContactDivUidHide(this)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div class="div_container" id="t' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '" class="user_node">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "ust:" + users[j]['dn'] +
            '" value="' + rootdn + '" key="' + users[j]['key'] + '" class="' + checkStatus + '"  onclick="select_user_node_uid_hide(this,this.id)"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' +
            "ust:" + users[j]['dn'] + '" value="' + rootdn + '" key="' + users[j]['key'] + '" title="' + users[j]['uid'] + '" href="javascript:;" ' +
            'onclick="select_user_node_uid_hide(this,this.name)">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}

//+++ 20150724 为了不影响其他页面，主界面的事件响应函数需要改变
function select_ou_node(dn) {
    //获取进行选择操作的checkbox,并将此群组下的所有checkbox的属性设置为选中
    //如果listen选项为真，才进行加载用户信息的操作
    var oudn = dn.substring(4);
    var div_id = "t"+oudn;
    var span = document.getElementById(dn);
    var status = span.className;
    var changeTo = "";

    if (status == "checkbox checkbox_uncheck") {
        changeTo = "checkbox checkbox_checked";
        changeContactSelectedUsers(dn, "contact add", "ou");
    } else {
        changeTo = "checkbox checkbox_uncheck";
        changeContactSelectedUsers(dn, "contact del", "ou");
    }

    var div = document.getElementById(div_id);  //获取群组所在的div
    var checkboxs = div.getElementsByTagName("span");
    for (var i = 0; i < checkboxs.length; i++) {
        checkboxs[i].setAttribute("class", changeTo);
    }
}
//方框选择框点击是时发生的动作
function select_ou_node_uid_hide(element) {
    //console.log(element);
    var dn = element.id;
    var rootdn = $(element).attr("value");
    //console.log(dn);
    //console.log(rootdn);

    //获取进行选择操作的checkbox,并将此群组下的所有checkbox的属性设置为选中
    //如果listen选项为真，才进行加载用户信息的操作
    var oudn = dn.substring(4);
    var div_id = "t"+oudn;
    var span = document.getElementById(dn);
    var status = span.className;
    var changeTo = "";

    if (status == "checkbox checkbox_uncheck") {
        changeTo = "checkbox checkbox_checked";
        changeContactSelectedUsersUidHide(dn,rootdn, "contact add", "ou");
    } else {
        changeTo = "checkbox checkbox_uncheck";
        changeContactSelectedUsersUidHide(dn,rootdn, "contact del", "ou");
    }

    var div = document.getElementById(div_id);  //获取群组所在的div
    var checkboxs = div.getElementsByTagName("span");
    for (var i = 0; i < checkboxs.length; i++) {
        checkboxs[i].setAttribute("class", changeTo);
    }
}

//+++20150729 用户节点checkbox在发生变化时做的操作
function select_user_node($Element, uid, sdn) {
    if (($Element).tagName == "A")    //如果点击的是文字连接a
    {
        var sp = document.getElementById(sdn);   //获取id=sdn的object span
        if (sp.className == "checkbox checkbox_checked") {
            sp.setAttribute("class", "checkbox checkbox_uncheck");
            changeContactSelectedUsers(uid, "contact del", "user");
        }
        else {
            sp.setAttribute("class", "checkbox checkbox_checked");
            changeContactSelectedUsers(uid, "contact add", "user");
        }
    }
    if (($Element).tagName == "SPAN") {
        if (($Element).className == "checkbox checkbox_checked") {
            changeContactSelectedUsers(uid, "contact del", "user");
        } else {
            changeContactSelectedUsers(uid, "contact add", "user");
        }
    }
}

function select_user_node_uid_hide($Element, sdn) {
    var rootdn = $($Element).attr("value");
    var key = $($Element).attr("key");

    if (($Element).tagName == "A")    //如果点击的是文字连接a
    {
        var sp = document.getElementById(sdn);   //获取id=sdn的object span
        if (sp.className == "checkbox checkbox_checked") {
            sp.setAttribute("class", "checkbox checkbox_uncheck");
            changeContactSelectedUsersUidHide(key,rootdn, "contact del", "user");
        }
        else {
            sp.setAttribute("class", "checkbox checkbox_checked");
            changeContactSelectedUsersUidHide(key,rootdn, "contact add", "user");
        }
    }
    if (($Element).tagName == "SPAN") {
        if (($Element).className == "checkbox checkbox_checked") {
            changeContactSelectedUsersUidHide(key,rootdn, "contact del", "user");
        } else {
            changeContactSelectedUsersUidHide(key,rootdn, "contact add", "user");
        }
    }
}

// +++ 20150728 用户更改选择的节点
// 传入dn为被操作span的id
function changeContactSelectedUsers(dn, type, node) {
    var id = "";
    if (node == "ou") {
        id = dn.substr(4);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            type: type,
            node: node,
            size: contactsPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq(obj, function (data) {
        //console.log(data);
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        setContactPage(userNumber, cur_page, contactsPerPageGlobal);   //显示第一页
        clear_contact_table();
        showContactList(users);

    });
}

function changeContactSelectedUsersUidHide(dn,rootdn, type, node) {
    var id = "";
    if (node == "ou") {
        id = dn.substr(4);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users_uid_hide",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            rootdn:rootdn,
            type: type,
            node: node,
            size: contactsPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq(obj, function (data) {
        //console.log(data);
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        setContactPage(userNumber, cur_page, contactsPerPageGlobal);   //显示第一页
        clear_contact_table();
        showContactList(users);

    });
}

function changeContactSelectedUsersUidHideTree(dn,rootdn, type, node) {
    var id = "";
    if (node == "ou") {
        id = dn.substr(4);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users_uid_hide",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            rootdn:rootdn,
            type: type,
            node: node,
            size: contactsPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq(obj, function (data) {
        //console.log(data);
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        //setContactPage(userNumber, cur_page, contactsPerPageGlobal);   //显示第一页
        clear_contact_table();
        //showContactList(users);

    });
}

function showContactList(users){
    var html = "";
    for(var i=0;i<users.length;i++){
        html+=generate_contact_str(users[i]);
    }
    $("#ccN tbody").append(html);
    $("#contacts_cN").mCustomScrollbar("update");
}
//将联系人表中的用户数据清空
function clear_contact_table(){
    $("#ccN tbody").html("");
}

function get_department_friendly_name(oudn){
    var department = "";
    var fenjie = oudn.split(',');
    for (var i = fenjie.length - 1; i >= 0; i--) {
        if (fenjie[i].substring(0, 2) == 'ou') {
            department += fenjie[i].substring(3) + '/';
        }
    }
    department = department.substring(0, department.length - 1);
    return department;
}

function generate_contact_str(user_data){
    var txt;
    txt = "";
    txt += '<tr class="' + user_data['uid'] + '">';
    txt += '<td>' + user_data['username'] + '</td>';
    txt += '<td>' + user_data['title'] + '</td>';
    txt += '<td>' + get_department_friendly_name(user_data['oudn']) + '</td>';
    txt += '<td class="Pnumber">' + user_data['uid'] + '</td>';
    txt += '</tr>';
    return txt;
}

//设置page信息，首次
function setContactPage(userNumber, page, userPerPage) {
    var userPerPage = userPerPage;
    var pageNumber = Math.ceil(userNumber / userPerPage);
    //for page change
    $("#total_page_num").html(pageNumber);
    $("#total_count").html(userNumber);
    $("#contact_page_number").val(page);

    $("#contacts_perpage").html("(每页"+userPerPage+"条)");
}

//首页
$("#contact_first_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#contact_page_number").val());
    if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }
    $("#contact_page_number").val(1);
    //+++20150826 脚本触发页数变化
    $("#contact_page_number").change();
});
//末页
$("#contact_end_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#contact_page_number").val());
    if (cur_page < 1) {
        return;
    } else if ($("#total_page_num").html() == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }
    $("#contact_page_number").val($("#total_page_num").html());
    //+++20150826 脚本触发页数变化
    $("#contact_page_number").change();
});
//上一页
$("#contact_pre_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#contact_page_number").val());
    if (cur_page < 1) {
        return;
    } else if (cur_page == 1) {
        loadingStatus("当前已经是第一页!");
        return;
    }
    //记住本页第一条的uid
    var obj = {
        _path: "/a/wp/org/get_page_users_uid_hide",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id"),
            page: cur_page-1,
            size: contactsPerPageGlobal,      //需要加入页面用户数
            contact: 1
        }
    };
    ajaxReq(obj, function (data) {
        var users = data.users;
        modContactPage(cur_page - 1);
        clear_contact_table();
        showContactList(users.reverse());
    });
});
//下一页
$("#contact_next_page").click(function () {
    //获取现在页数
    var cur_page = Number($("#contact_page_number").val());
    if (cur_page < 1) {
        return;
    } else if ($("#total_page_num").html() == cur_page) {
        loadingStatus("当前已经是最后一页!");
        return;
    }
    //记住本页最后一条的uid
    var cur_user_number = $("#yglb tbody tr").length;
    var obj = {
        _path: "/a/wp/org/get_page_users_uid_hide",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id"),
            page: cur_page + 1,
//            last_user: last_user,
            size: contactsPerPageGlobal,      //需要加入页面用户数
            contact: 1
        }
    };
    ajaxReq(obj, function (data) {
        var users = data.users;
        modContactPage(cur_page + 1);
        clear_contact_table();
        showContactList(users);
    });
});
//输入页数
function contact_page_change(cur_page) {
    var totalPages = parseInt($("#total_page_num").html());
    if (totalPages < 1) {
        //+++20150824 如果用户不满1页，应显示成1页
        $("#contact_page_number").val(0);
        return;
    }
    //判断当前输入页数是否合法,不合法则返回当前页
    if (isNaN(cur_page)) {
        loadingStatus("非法输入，请输入数字！");
        $("#contact_page_number").focus();
        return;
    }
    //+++20150824 加入对于输入页数0的限制
    if (cur_page <= 0 || cur_page > totalPages) {
        loadingStatus("当前输入超出页数范围，请重新输入！");
        return;
    }
    getPageContacts(cur_page);
};
//根据当前页数获取联系人信息
function getPageContacts(page_num){
    var sid = $.cookie("org_session_id");
    var obj = {
        _path:"/a/wp/org/get_page_users_uid_hide",
        _methods:"get",
        param:{
            sid:sid,
            page:page_num,
            size:contactsPerPageGlobal,
            contact: 1
        }
    };
    ajaxReq(obj,function(data){
        var rt= data.rt;
        if(rt==0){
            var users = data.users;
            if (users.length <= 0) {
                page_num = 0;
            }
            modPage(Number(page_num));
            clear_contact_table();
            showContactList(users);
        }else{
            loadingStatus("获取联系人信息失败",0);
        }

    });
}
function modContactPage(page) {
    $("#contact_page_number").val(page);
    $("#contact_page_number").attr('value', page);
}

//联系人下发功能中选择电话号码树的方法
//function tcheck(dn) {
//    //获取进行选择操作的checkbox,并将此群组下的所有checkbox的属性设置为选中
//    var oudn = dn.substring(4);//这是取得的群组dn
//    var span = document.getElementById(dn);//获得子群组的span
//    var div = document.getElementById('t' + oudn);  //获取群组所在的div
//    var checkboxs = div.getElementsByTagName("span");
//    //找到checkbox对应的a
//    var a = document.getElementsByName(dn)[0];
//    a.style.color = '#336C98';
//    for (var i = 0; i < checkboxs.length; i++) {
//        var type = checkboxs[i].id.substring(0, 2);
//        var pnumber = checkboxs[i].parentNode.getElementsByTagName("a")[0].className.split(":")[1];
//        if (span.className == "checkbox checkbox_uncheck") {
//            checkboxs[i].setAttribute("class", "checkbox checkbox_checked");
//            //如果是群组的话，不做出动作
//
//            if (type == 'us') {
//                var sdn = checkboxs[i].id;
//                var uid = checkboxs[i].title;
//                delContacts(pnumber);
//                addContacts(sdn, uid);
//                //添加联系人到右边的显示框
//            }
//
//        } else {
//            checkboxs[i].setAttribute("class", "checkbox checkbox_uncheck");
//            delContacts(pnumber);//将联系人从右边的显示框移除
//        }
//
//
//    }
//}

//function showcontacts($Element, uid, sdn) {
//    var jh = sdn.substr(0, 2);
//    var dn = sdn.substr(4);
//    var pnumber = '';
//    if (($Element).tagName == "A")    //如果点击的是文字连接a
//    {
//        pnumber = ($Element).className.split(":")[1];
//        ($Element).style.color = '#336C98';
//        var sp = document.getElementById(sdn);   //获取id=sdn的object span
//        if (sp.className == "checkbox checkbox_checked") {
//            sp.setAttribute("class", "checkbox checkbox_uncheck");
//            delContacts(pnumber);
//            return;
//        }
//        else {
//            sp.setAttribute("class", "checkbox checkbox_checked");
//            delContacts(pnumber);
//            addContacts(sdn, uid);
//        }
//    }
//    if (($Element).tagName == "SPAN") {
//        var a = document.getElementsByName(sdn)[0];
//        a.style.color = '#336C98';
//    }
//    if (($Element).tagName == "SPAN" && ($Element).className == "checkbox checkbox_checked")   //如果点击的是span
//    {
//        var a = document.getElementsByName(sdn)[0];
//        a.style.color = '#336C98';
//        pnumber = a.className.split(":")[1];
//        delContacts(pnumber);
//        return;
//    }
//    else {
//        var a = document.getElementsByName(sdn)[0];
//        a.style.color = '#336C98';
//        pnumber = a.className.split(":")[1];
//        delContacts(pnumber);
//        addContacts(sdn, uid);
//    }
//}

//function addContacts(sdn, uid) {
//    //将选中的联系人信息添加到右边的显示框，需要显示的信息
//    //姓名、职位、所属部门、电话号码
//    var a = document.getElementsByName(sdn)[0];
//    var username = a.innerHTML;
//    var job = a.className.split(':')[0];
//    var pnumber = a.className.split(':')[1];
//    var department = '';
//    var fenjie = sdn.split(',');
//    for (var i = fenjie.length - 1; i >= 0; i--) {
//        if (fenjie[i].substring(0, 2) == 'ou') {
//            department += fenjie[i].substring(3) + '/';
//        }
//    }
//    department = department.substring(0, department.length - 1);
//    //勾选显示用户信息
//    var txt;
//    txt = "";
//    txt += '<tr class="' + uid + '">';
//    txt += '<td><span class="checkbox checkbox_checked"></span></td>';
//    txt += '<td>' + username + '</td>';
//    txt += '<td>' + job + '</td>';
//    txt += '<td>' + department + '</td>';
//    txt += '<td class="Pnumber">' + pnumber + '</td>';
//    txt += '</tr>';
//    $("#ccN tbody").append(txt);
//    $("#contacts_cN").mCustomScrollbar("update");
//    set_selected_contacts();
//    return;
//}

//function delContacts(pnumber) {
//    //将联系人从右边的显示框移除
//    $("#ccN tbody tr").each(function (index, element) {
//        var Pnumber = $(".Pnumber", $(element)).html();
//        if (Pnumber == pnumber) {
//            $(element).remove();
//        }
//    });
//    set_selected_contacts();
//}

//+++20151030 监控联系人表格，填充下面的联系人总数量提示
//function set_selected_contacts(){
//    var selected = 0;
//    var total = 0;
//    $("#ccN tbody tr .checkbox").each(function(index,element){
//        total+=1;
//        if(element.className=="checkbox checkbox_checked"){
//            selected+=1;
//        }
//    });
//
//    $("#selected_count").html(selected);
//    $("#total_count").html(total);
//}

//function change_selected_counts(addnum){
//    var total = parseInt($("#total_count").html());
//    var now_selected = parseInt($("#selected_count").html());
//    var after_selected = now_selected+ addnum;
//    if(after_selected>=total){
//        after_selected=total;
//    }else if(after_selected<=0){
//        after_selected = 0;
//    }
//    $("#selected_count").html(after_selected);
//}

//+++20150804 点击每一个联系人所在的表格的时候做出相应操作
//$("#ccN tbody tr").live("click", function (event) {
//    event.preventDefault();
//    if (event.toElement.tagName == "SPAN") {
//        if (event.toElement.className == "checkbox checkbox_uncheck") {
//            change_selected_counts(-1);
//        }
//        else {
//            change_selected_counts(1);
//        }
//    } else {
//        var checkbox = this.getElementsByTagName("span")[0];
//
//        if (checkbox.className == "checkbox checkbox_checked") {
//            checkbox.className = "checkbox checkbox_uncheck";
//            change_selected_counts(-1);
//        }
//        else {
//            checkbox.className = "checkbox checkbox_checked";
//            change_selected_counts(1);
//        }
//    }
//
//});

//function selectAll(id) {
//    var span = document.getElementById(id);
//    var checkboxs = $("#ccN tbody tr .checkbox");
//    if (span.className == 'checkbox checkbox_uncheck') {
//        $("#ccN tbody tr .checkbox").removeClass("checkbox_uncheck").addClass("checkbox_checked");
//        change_selected_counts(checkboxs.length);
//    }
//    else {
//        $("#ccN tbody tr .checkbox").removeClass("checkbox_checked").addClass("checkbox_uncheck");
//        change_selected_counts(-checkboxs.length);
//    }
//}

//联系人查询
//function search() {
//    var input = document.getElementById("search").value;
//    if (input == '') {
//        alert("请输入查询内容");
//    } else if (input.TextFilter() != input) {
//        alert("您输入了非法字符，请重新输入！");
//    } else {
//        var elements = document.getElementById("tree");
//        elements.innerHTML = '';
//        showTree();
//        //取到用户输入的数据，去遍历整个contacts_list容器中的所有a
//        var contacts_list = document.getElementById("tree");
//
//        var a_list = contacts_list.getElementsByTagName("a");
//        setTimeout(function () {
//            for (var i = 0; i < a_list.length; i++) {
//                var a = a_list[i];
//                if (a.innerHTML == input) {
//
//                    var name = a.name;
//                    var type = name.substring(0, 2);
//                    //以上获取了找到的a的name和类型，只要根据类型进行操作即可
//                    var parent = a.parentNode;
//                    while (parent.tagName != 'SECTION') {
//
//                        parent.style.display = 'block';
//                        parent = parent.parentNode;
//                    }
//                    a.style.color = '#ff0402';
//                }
//            }
//        }, 500);
//    }
//}

/*下发联系人部分*/
function sendcontacts() {
    //+++ 20150824 不再从前台向后台传递选中用户
//    var users = JSON.stringify(contactlist);
    //+++20160111 从后台获取用户联系人的选中状态，前台只需查看是否有选中联系人
    if(check_selected_uids()&&check_selected_contacts()){
        var users = JSON.stringify([]);
        var flag = get_flag();
        var uids = JSON.stringify([]);
        sendcon(flag,uids, users);
    }
}
//+++20160111 加入查看是否有选中用户的逻辑
function check_selected_uids(){
    var ids = [];
    $("#yic .checkbox_checked").each(function (index, element1) {
//        var type = element1.id.substring(0, 2);
//        if (type == 'us') {
        ids.push(element1.title);
//            sendcon(element1.title,users);
//        }
    });
    if(ids.length==0){
        alert("请在左侧选择将要收到电话簿的用户");
        return false;
    }
    return true;
}

//20161008选择下发联系人的每一项的前面的小方框所触发的函数
function check_selected_contacts(){
    var ids = [];
    $("#tree .checkbox_checked").each(function (index, element1) {
//        var type = element1.id.substring(0, 2);
//        if (type == 'us') {
        ids.push(element1.title);
//            sendcon(element1.title,users);
//        }
    });
    if(ids.length==0){
        alert("请在右侧选择需要下发的通讯录");
        return false;
    }
    return true;
}
//+++20151102 加入所下发联系人的群组，从联系人树中获取
function get_formated_contacts(){
    var contacts = [];
    var first_div = $("#tree div[id]")[0];
    //+++ 20151123 right side selected users
    var need_del_users = [];
    $("#ccN tr").each(function(index,element){
        if(element.childNodes[0].childNodes[0].className=="checkbox checkbox_uncheck"){
            need_del_users.push(element.className);
        }
    });
    var tree = get_ou_selected_tree(first_div.id,need_del_users);
    //+++20151116 加入群组树剪枝的过程
    while(tree!={}){
        if(tree['ous'].length==1&&tree['users']==0){
            tree = tree['ous'][0];
        }else{
            break;
        }
    }
    return tree;
}
function get_ou_selected_tree(ou_id,need_del_users){
    var div = document.getElementById(ou_id);
//    console.log(div.childNodes);
    var children = div.childNodes;
    var sonusers = [];
    var sonous = [];
    for(var i=0;i<children.length;i++){
        if(children[i].tagName=="DIV"){
            if(children[i].id==""){
                continue;
            }else{
                var ou_tree =get_ou_selected_tree(children[i].id,need_del_users);
                if(ou_tree==null){
                    continue;
                }else{
                    sonous.push(ou_tree);
                }
            }
        }else if(children[i].tagName=="LI"){
            var span = children[i].childNodes[0];
            var a = children[i].childNodes[2];
            var checked = span.className;
            if(checked=="checkbox checkbox_checked"){
                if(need_del_users.indexOf(children[i].title)<0){
                    sonusers.push({"uid":children[i].title,"name": a.innerHTML});
                }
            }
        }
    }

    if(sonous.length==0&&sonusers.length==0){
        return null;
    }else{
        return {"oudn":ou_id.substr(1),"users":sonusers,"ous":sonous};
    }
}
//+++20151019 获取强制覆盖联系人标志位值
function get_flag(){
    var flag = 0;//默认添加机制
    if($("#forceWrite").attr("class")=="checkbox checkbox_checked"){
        flag = 1;//强制覆盖联系人
    }
    return flag;
}
//+++ 改20151019 加入强制覆盖标志位作为输入参数
function sendcon(flag, uids, users) {
    var org_session_id = $.cookie("org_session_id");
    var obj = {
        _path: '/a/wp/user/send_contacts',
        _methods: 'post',
        param: {
            sid: org_session_id,
            flag: flag,
            uids: uids,
            users: users
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        if (rt == 0) {
            loadingStatus("成功下发联系人信息",0);
            alert("同步联系人指令已成功下发，请确保手机在线，从而接收联系人信息");
        } else {
            loadingStatus("下发联系人失败",0);
            alert("网络异常，请重试！");
        }
    }, "正在下发联系人");
}

$().ready(function() {
    var obj = {
        _path: "/a/wp/org/auto_search_by_sid",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var users = data.users;
        //console.log(users);

        $("#search").autocomplete(users,{
            minChars: 1,
            max: 5,
            autoFill: false,
            mustMatch: false,
            matchContains: true,
            scrollHeight: 220,
            formatItem: function(data, i, total) {
                return data[0];
            },
            formatMatch: function(data, i, total) {
                return data[0];
            },
            formatResult: function(data) {
                return data[0];
            }
        });
    });
});

function search() {
    clear_contact_table();
    var t = document.getElementById('tree');
    var span = t.getElementsByTagName("span");
    for(var i=0;i<span.length;i++) {
        span[i].className = "checkbox checkbox_uncheck";
    }
    var input = document.getElementById("search").value;
    if (input == '') {
        alert("请输入查询内容");
    } else if (input.TextFilter() != input) {
        alert("您输入了非法字符，请重新输入！");
    } else {
        var obj = {
            _path: "/a/wp/org/auto_selected_by_sid",
            _methods: "get",
            param: {
                sid: $.cookie("org_session_id"),
                username: input
            }
        };

        ajaxReq(obj, function (data) {
            var rt = data.rt;
            var rootdn = data.dn;
            var rootcon = data.contacts;
			var count = data.count;
			var user_result =data.user;
			var block=0;
            //var user_oudn = data.user_oudn;
            //var user_key = data.user_key;
            //var user_uid = data.user_uid;
            if (rt != 0||count==0) {
                //loadingStatus("查询的用户不存在！", 0);
                alert("查询的用户不存在！");
            } else {
				for(var m=0;m<count;m++){
					var user_oudn = user_result[m].user_oudn;
					var user_uid =user_result[m].user_id;
					var user_key =user_result[m].user_key;
					
					//loadingStatus("成功获取用户信息！", 0);
					if (rootdn.split(",")[0].split("=")[0] == "dc") {
						var id = "ust:cn=" + input + "," + user_oudn;
						var a = t.getElementsByTagName("a");
						for(var i=0;i<a.length;i++) {
							var t_a = a[i].title;
							if(t_a[0]=="t"){
								var diva = document.getElementById(t_a);
								var stra = t_a.substring(1,t_a.length);
								if(user_oudn.indexOf(stra) <= -1){
									
									if(block==0){
										diva.style.display = "none";
										block=1;
									}
								} else {
									
									diva.style.display = "block";
								}
								autoshowContactDiv(t_a);
							}
						}
						auto_select_user_node(user_uid,id);
					
					} else {
						var id = "ust:cn=" + input + "," + user_oudn;
						var a = t.getElementsByTagName("a");
						for(var i=0;i<a.length;i++) {
							var t_a = a[i].title;
							if(t_a[0]=="t"){
								var diva = document.getElementById(t_a);
								var stra = t_a.substring(1,t_a.length);
								if(user_oudn.indexOf(stra) <= -1){
									if(block==0){
										diva.style.display = "none";
										block=1;
									}
								} else {
									diva.style.display = "block";
								}
								autoshowContactDivUidHide(t_a,rootdn);
							}
						}
						auto_select_user_node_uid_hide(user_key,rootdn,id);
						block=1;
					}
				}
				
            }
        });
    }
}

function autoshowContactDiv(title) {
    var content = document.getElementById(title).innerHTML;
    //console.log(content);
    var oudn = title;
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,title.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel",
            _methods: "get",
            param: {
                oudn: oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq1(obj, function (data) {
            var rt = data.rt;
            if (rt != 0) {
                //loadingStatus("获取用户信息失败！", 0);
            } else {
                //loadingStatus("成功获取用户信息！", 0);
                var sons = autoshowContactOuSons(data);
                document.getElementById(title).innerHTML = sons;	//添加一个账户
            }
        });
    }
}

function autoshowContactOuSons(all) {
    var html = "";
    //loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['dn'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("out:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div class="div_label">';
        html += '<span id="' + "out:" + dn + '"class="' + checkStatus + '" onclick="select_ou_node(this.id)"></span>';
        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="t' + dn + '" onclick="showContactDiv(this.title)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div class="div_container" id="t' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '" class="user_node">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "ust:" + users[j]['dn'] +
            '" class="' + checkStatus + '"  onclick="select_user_node(this,this.title,this.id)"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' +
            "ust:" + users[j]['dn'] + '" title="' + users[j]['uid'] + '" href="javascript:;" ' +
            'onclick="select_user_node(this,this.title,this.name)">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}

function auto_select_user_node(uid,sdn) {
    var sp = document.getElementById(sdn);
    sp.className = "checkbox checkbox_checked";
    autochangeContactSelectedUsers(uid, "contact add", "user");
}

function autochangeContactSelectedUsers(dn, type, node) {
    var id = "";
    if (node == "ou") {
        id = dn.substr(4);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            type: type,
            node: node,
            size: contactsPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq1(obj, function (data) {
        //console.log(data);
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        setContactPage(userNumber, cur_page, contactsPerPageGlobal);   //显示第一页
        clear_contact_table();
        showContactList(users);
    });
}

function autoshowContactDivUidHide(title,value) {
    var oudn = title;
    var rootdn = value;
    var content = document.getElementById(title).innerHTML;
    //console.log(content);
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,title.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel_uid_hide",
            _methods: "get",
            param: {
                oudn:rootdn,
                contacts:oudn,
                sid: $.cookie("org_session_id")
            }
        };
        ajaxReq1(obj, function (data) {
            //console.log(data);
            var rt = data.rt;
            if (rt != 0) {
                //loadingStatus("获取用户信息失败！", 0);
            } else {
                //loadingStatus("成功获取用户信息！", 0);
                var sons = autoshowContactOuSonsUidHide(data);
                //console.log(sons);
                document.getElementById(title).innerHTML = sons;	//添加一个账户
            }
        });
    }
}

function autoshowContactOuSonsUidHide(all) {
    var html = "";
    //loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['oudn'];
    var dn = all['contacts'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("out:" + rootdn);
    var checkStatus = parentOuSpan.className;

    //获取页面相关参数，确定是否监听和显示右侧用户
    var page = location.href;
    var listen = true;
    if (page.indexOf("home") > -1) {
        listen = true;
    } else {
        listen = false;
    }
//    html+='<div style="margin-left:20px;display:block;" id="'+rootdn+'">';
    //每一个群组要进行的操作
    for (var i = 0; i < ous.length; i++) {
        var ou = ous[i]['ou'];
        var dn = ous[i]['dn'];
        html += '<div class="div_label">';
        html += '<span id="' + "out:" + dn + '" value="' + rootdn + '" class="' + checkStatus + '" onclick="select_ou_node_uid_hide(this)"></span>';
        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="t' + dn + '" value="' + rootdn + '" onclick="showContactDivUidHide(this)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div class="div_container" id="t' + dn + '">';
        html += '</div>';
    }

    for (var j = 0; j < users.length; j++) {
        html += '<li title="' + users[j]['uid'] + '" class="user_node">';
        html += '<span title="' + users[j]['uid'] + '" id="' + "ust:" + users[j]['dn'] +
            '" value="' + rootdn + '" key="' + users[j]['key'] + '" class="' + checkStatus + '"  onclick="select_user_node_uid_hide(this,this.id)"></span>';
        //这里的id是为了寻找span,class是控制前面的checkbox
        html += '<img src="images/unline.png"/>';
        html += '<a class="' + users[j]['job'] + ":" + users[j]['email'] + '"name="' +
            "ust:" + users[j]['dn'] + '" value="' + rootdn + '" key="' + users[j]['key'] + '" title="' + users[j]['uid'] + '" href="javascript:;" ' +
            'onclick="select_user_node_uid_hide(this,this.name)">';
        //这里的属性name是为了寻找此标签对应的span，title是想指向用户的时候显示用户的邮箱信息
        html += users[j]['username'];
        html += '</a>';
        html += '</li>';
    }
//    html+="</div>"
    return html;
}

function auto_select_user_node_uid_hide(user_key,rootdn,sdn) {
    var sp = document.getElementById(sdn);
    sp.className = "checkbox checkbox_checked";
    autochangeContactSelectedUsersUidHide(user_key,rootdn, "contact add", "user");
}

function autochangeContactSelectedUsersUidHide(dn,rootdn, type, node) {
    var id = "";
    if (node == "ou") {
        id = dn.substr(4);
    } else {
        id = dn;
    }

    var obj = {
        _path: "/a/wp/org/change_selected_users_uid_hide",
        _methods: "post",
        param: {
            sid: $.cookie("org_session_id"),
            users: id,
            rootdn:rootdn,
            type: type,
            node: node,
            size: contactsPerPageGlobal      //需要加入页面用户数
        }
    };
    ajaxReq(obj, function (data) {
        //console.log(data);
        var users = data.users;
        var userNumber = data.selected_count;
        $.cookie('totalUsersNumber', userNumber);
        var page = location.href;
        var cur_page = 0;
        if (users.length > 0) {
            cur_page = 1;
        }
        setContactPage(userNumber, cur_page, contactsPerPageGlobal);   //显示第一页
        clear_contact_table();
        showContactList(users);
    });
}
