/**
 * Created by GCY on 2016/2/22.
 * 作为工具模块处理一些常用的请求
 */
var ldap_base_dn = "dc=test,dc=com";
function get_user_by_uid(uid){
    var user = null;
    var obj = {
        _path:"/a/wp/org/get_user_by_uid",
        _methods:"get",
        param:{
            sid: $.cookie("org_session_id"),
            uid:uid
        }
    };
    ajaxReq1(obj,function(data){
        var rt = data.rt;
        if(rt==0){
            user = data.user;
        }
    });
    return user;
}

function get_dev_by_id(dev_id){
    var dev = null;
    var obj = {
        _path:"/a/wp/org/get_dev_by_id",
        _methods:"get",
        param:{
            sid: $.cookie("org_session_id"),
            dev_id:dev_id
        }
    };
    ajaxReq1(obj,function(data){
        var rt = data.rt;
        if(rt==0){
            dev = data.dev;
        }
    });
    return dev;
}

//+++20160219 获取管理员的权限数据
function get_admin_right(sid){
    var oudn = "";//这个之后可以扩展成数组
    var obj = {
        _path:"/a/wp/org/ldap_get_ou_by_sid",
        _methods:"get",
        param:{
            sid: sid
        }
    };
    ajaxReq1(obj,function(data){
//        console.log(data);
        var rt = data.rt;
        if(rt==0){
            oudn = data.dn;
        }
    });
    return oudn;
}

//+++20161026 根据oudn获取友好的群组名称
function get_oudn_name(oudn){
    var friendly_name = "";
    if(oudn==ldap_base_dn){
        friendly_name = "所有用户";
    }else{
        var fenjie = oudn.split(',');
        for (var i = fenjie.length - 1; i >= 0; i--) {
            if (fenjie[i].substring(0, 2) == 'ou') {
                friendly_name += fenjie[i].substring(3) + '/';
            }
        }
        friendly_name = friendly_name.slice(0, -1);
    }
    return friendly_name;
}

////+++20160223 根据系统指定格式的ou名称获取oudn
//function get_ou_dn(ou){
//    var oudn = "";
//    if(ou=="admin"||ou=="所有用户"){
//        oudn = ldap_base_dn;
//    }else if(ou.indexOf(",")>=0){
//        var ou_names = ou.split(",");
//        for(var i=ou_names.length-1;i>=0;i--){
//            oudn+= "ou="+ou_names[i]+",";
//        }
//        oudn+= ldap_base_dn;
//    }else{
//        oudn = "ou="+ou+","+ldap_base_dn;
//    }
//    return oudn;
//}
//20161026 根据系统指定格式的ou名称获取oudn
function get_ou_dn(ou){
    var oudn = "";
    if(ou=="admin"||ou=="所有用户"){
        oudn = ldap_base_dn;
    }else {
        for(var i= 0; i<=ou.length-1;i++){
            fenjie= ou[i].split(',');
            for(var k=fenjie.length-1;k>=0;k--){
                if(fenjie[k].substring(0,2) =='ou'){
                    oudn+= fenjie[k].substring(3)+'/';
                }
            }
        }
        oudn=oudn.slice(0,-1);
    }
    return oudn;
}

//为label添加颜色
function addColoredText(labelID,text,color){
    $("label[id='"+labelID+"']").html(text);
    $("label[id='"+labelID+"']").css({"color":color});
}

//权限选择可扩展列表组件
function RightList(id,oudn_list){
    this.parent_id = id;
    this.init(oudn_list);
}

RightList.prototype.right_friendly_name = function(){
    var friendly_name = "";
    friendly_name = get_oudn_name(this.oudn());
    return friendly_name;
};

RightList.prototype.oudn = function(){
    var oudn_str = "";
    var parent = document.getElementById(this.parent_id);
    var selects = parent.childNodes;
    if(selects.length==1&&selects[0].value=="请选择"){
        oudn_str = "";
    }else{
        for(var i=selects.length-1;i>=0;i--){
            var select_option = selects[i].options[selects[i].selectedIndex];
            if($(select_option).attr("oudn")){
                oudn_str = $(select_option).attr("oudn");
                break;
        }
    }}

    return oudn_str;
};

RightList.prototype.show_oudn = function(qx,oudn){
    var parent = $(document.getElementById(this.parent_id));
    //要从管理员的权限节点到该用户的群组节点完全展开
    var qx_array = qx.split(",").reverse();
    var oudn_array = oudn.split(",").reverse();
    var this_level_select_class = "root"; //当前层级的select_class
    var step_ou = qx;
    for(var i=qx_array.length-1;i<oudn_array.length;i++){
        var this_select=null;
        if(parent.children("select").length==1){
            this_select = parent.children("select")[0];
            this_select.value = step_ou.split(",")[0].split("=")[1];
            $(this_select).trigger("change");
        }else{
            this_select = $("select[class='"+this_level_select_class+"']")[0];
            this_select.value = step_ou.split(",")[0].split("=")[1];
            $(this_select).trigger("change");
        }
        this_level_select_class = step_ou;
        step_ou=oudn_array[i+1]+","+step_ou;
    }
};

RightList.prototype.get_html = function(){
    var html = "";
    return html;
};

RightList.prototype.init = function(oudn_list){
    this.oudn_list = oudn_list;
    var select = document.createElement("SELECT");
    select.options.add(new Option("请选择","请选择"));
    select.className = "root";
    $(select).change(function(event){
        change_select_ou(event);
    });
    if(oudn_list.length==1){
        //单权限用户直接加载下一级群组
        var oudn = oudn_list[0];
        var ous = [{dn:oudn,ou:oudn.substr(0,oudn.indexOf(",")).split("=")[1]}];
        if(oudn==ldap_base_dn){
            ous = get_next_level_ous(oudn)
        }
        ous.forEach(function(item){
            var first_ou = item['ou'];
            var option = document.createElement("OPTION");
            option.value = first_ou;
            option.text = first_ou;
            $(option).attr("oudn",item['dn']);
            select.options.add(option);
        });
    }else if(oudn_list.length>1){
        //多权限用户需要在最初进行权限的选择
        oudn_list.forEach(function(item){
            var ou_name = "";
            if(item==ldap_base_dn){
                ou_name = "所有用户";
            }else{
                ou_name = item.substr(0,item.indexOf(",")).split("=")[1];
            }
            var option = document.createElement("OPTION");
            option.value = ou_name;
            option.text = ou_name;
            $(option).attr("oudn",item);
            select.options.add(option);
        });
    }
    document.getElementById(this.parent_id).appendChild(select);
};


RightList.prototype.reset = function(){
    var parent = document.getElementById(this.parent_id);
    var selects = parent.getElementsByTagName("SELECT");
    for(var i=selects.length-1;i>=0;i--){
        if(selects[i].className!="root"){
            parent.removeChild(selects[i]);
        }
    }
    parent.getElementsByClassName("root")[0].value = "请选择";
};


function load_next_ous(oudn){
    var ous = get_next_level_ous(oudn);
    if(ous.length>0){
        var select = document.createElement("SELECT");
        select.className=oudn;
        select.options.add(new Option("请选择","请选择"));
        ous.forEach(function(ou){
            var option = document.createElement("OPTION");
            option.value = ou['ou'];
            option.text = ou['ou'];
            $(option).attr("oudn",ou['dn']);
            select.options.add(option);
        });
        $(select).change(function(event) {
            change_select_ou(event);
        });
        return select;
    }else{
        return null;
    }
}

function change_select_ou(event){
    var select_oudn = $(event.target.options[event.target.selectedIndex]).attr("oudn");
    //获取容器节点
    var parent = event.target.parentNode;
    //要将后面的旧select remove掉
    var selects = parent.childNodes;
    if(select_oudn){
        //获取容器节点
        for(var i=selects.length-1;i>0;i--){
            if(selects[i].className!=select_oudn&&selects[i].className!=event.target.className){
                parent.removeChild(selects[i]);
            }else{
                break;
            }
        }
        //获取并添加新的select
        var newselect = load_next_ous(select_oudn);
        if(newselect){
            parent.appendChild(newselect);
        }
    }else{
        var select_class = event.target.className;
        if(select_class!=selects[selects.length-1].className){
            for(var i=selects.length-1;i>0;i--){
                var item = selects[i];
                if(selects[i].className!=select_oudn&&selects[i].className!=event.target.className){
                    parent.removeChild(item);
                }
                else{
                    break;
                }
            }
        }
    }
}

function get_next_level_ous(oudn){
    var ous = [];
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
        ous=data.ous;
    });
    return ous;
}/*end for RightList*/
//去除输入框的空格、tab键等特殊字符
if(!String.prototype.trim){
    String.prototype.trim = function(){
        return this.replace(/\s/g, '');
    }
}