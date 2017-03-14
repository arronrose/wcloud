/**
 * Created by GCY on 2015/12/30.
 */
    // 路径配置
var base_dn = "dc=test,dc=com";

window.onload = function(){
    var href=location.href;
    if(href.indexOf("statistics")>-1){
//        var ctx_pie1 = document.getElementById("pie_chart1").getContext("2d");
//        window.myPie = new Chart(ctx_pie1).Pie(pieData,{
//            segmentStrokeWidth : 4
//        });
//        var ctx_line = document.getElementById("line_chart").getContext("2d");
//        window.myLine = new Chart(ctx_line).Line(lineChartData, {
//            responsive: true,
//            scaleOverlay : false
//        });
        //init_statistics();
        //填充时间统计组件
        init_online_tools();
        check_for_analysis("ou:"+base_dn,"ou");
    }
};

function init_statistics() {
    var obj = {
        _path: "/a/wp/org/ldap_get_ou_by_sid",
        _methods: "get",
        param: {
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        var rootdn = data.dn;
        var ou = rootdn.split(",")[0].split("=")[1];
        if (rt != 0) {
            loadingStatus("获取用户信息失败！", 0);
        } else {
            loadingStatus("成功获取用户信息！", 0);
            var initNode = "";
            if (rootdn.split(",")[0].split("=")[0] == "dc") {
                ou = '所有用户';
            }
            initNode += '<div style="cursor:pointer" style="margin-left:20px">';
            initNode += '<span id="' + "ou:" + rootdn + '"class="checkbox checkbox_uncheck" onclick="check_for_analysis(this.id)"></span>';
            initNode += '<img src="images/group.png"/>';
            initNode += '<a href="javascript:;" title="' + rootdn + '" onclick="show_son_ous(this.title)">';
            initNode += ou;
            initNode += '</a>';
            initNode += '</div>';
            initNode += '<div style="margin-left:20px;display:block;" id="' + rootdn + '">';

            $("#yic").html(initNode);
        }
    }, "正在获取用户信息!");
}

function init_online_tools(){
    var date = new Date();
    var this_year = date.getFullYear();
    var this_month = date.getMonth()+1;
    fill_select_values("year",this_year,this_year,this_year+10);
    fill_select_values("month",1,this_month,12);
}

function fill_select_values(id,start,defaultvalue,endvalue){
    var $select = $("select[id='"+id+"']");
    $select.append("<option value=0>"+"请选择"+"</option>");
    for(var i=start;i<=endvalue;i++){
        var value = i.toString();
        if(i<10)value = "0"+i;
        if(i==defaultvalue){
            $select.append("<option selected='selected' value='"+ value+"'>"+value+"</option>");
        }else{
            $select.append("<option value='"+value+"'>"+value+"</option>");
        }
    }
}

//获取该群组的所有子群组信息
function show_son_ous(oudn){
    var content = document.getElementById(oudn).innerHTML;
//    alert("content:"+content);
    if(oudn[0]=="t"){
        oudn = oudn.substr(1,oudn.length-1);
    }
    if (content == "") {
        var obj = {
            _path: "/a/wp/org/ldap_onelevel_ou",
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
                var sons = showous(data, true);
                document.getElementById(oudn).innerHTML = sons;	//添加一个账户
            }
        }, "正在获取用户信息!");
    } else {
        //控制群组的展开和闭合
        var div = document.getElementById(oudn);
        if (div.style.display == "none") {
            div.style.display = "block";
        }
        else {
            div.style.display = "none";
        }
    }


}
//嵌套获取子群组信息
function showous(all, flag) {
    var html = "";
    loadingStatus("正在获取用户信息!", 0);
    var rootdn = all['dn'];
    var ous = all['ous'];
    var users = all['users'];

    //获取父节点的选中状态
    var parentOuSpan = document.getElementById("ou:" + rootdn);

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
        html += '<div style="cursor:pointer">';
        html += '<span id="' + "ou:" + dn + '"class="checkbox checkbox_uncheck" onclick="check_for_analysis(this.id)"></span>';

        html += '<img src="images/group.png"/>';
        html += '<a href="javascript:;" title="' + dn + '" onclick="show_son_ous(this.title)">';
        html += ou;
        html += '</a>';
        html += '</div>';
        html += '<div style="margin-left:20px;display:block;" id="' + dn + '">';
        html += '</div>';
    }
    return html;
}
//点击进行数据分析展示
/*id:群组的oudn，用户的uid;node:节点的类型*/
function check_for_analysis(id,node){
//    var select_status = $("span[id='"+id+"']").attr("class");
    if(has_select_span()){//这应该是有无选中的选框的判断
        var oudn = base_dn;
        show_base_info(oudn);
        //查看群组中是否有激活用户，有再进行数据的统计,将上面的获取基本信息的过程弄成同步的
        var live_user_count = parseInt($("#live_dev_num").html());
        if(live_user_count==0){
            reset_chart_info();
            alert("该群组没有激活用户，无法统计用户活跃度和用户在线情况");
        }else{
            show_line_info(oudn);
            show_pie_info(oudn);
        }
    }else{
        reset_base_info();
        reset_chart_info();
        reset_tool_bar_info();
    }
}
//判断是否存在选中的span
function has_select_span(){
    var has_select = false;
    var select_spans = $("#yic .checkbox_checked");
    if(select_spans.length>0){
        has_select = true;
    }
    return has_select;
}
//选中框单选，当一个选框选中的时候将其他选框取消选择
function change_select(oudn){
    var ou_id = "ou:"+oudn;
    $(".checkbox").each(function(index,element){
        if(element.id!=ou_id){
            element.className= "checkbox checkbox_uncheck";
        }
    });
}

//显示群组的基本信息
function show_base_info(oudn){
    var obj = {
        _path: "/a/wp/org/get_ou_base_info",
        _methods: "get",
        param: {
//            oudn: oudn,
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        if (rt != 0) {
            loadingStatus("获取群组信息失败！", 0);
        } else {
            loadingStatus("获取群组信息成功！", 0);
            //群组名称
            set_ou_base_info(data['ou_name'],data['user_num'],data['live_dev_num'],data['live_user_num'],
                data['sum_use_days'],data['avg_use_days'],data['sum_live_days'],data['avg_live_days'],
                data['avg_live_percentage'],data['uses_live_beyond_per']
                )
        }
    }, "正在获取群组信息!");
}

function reset_base_info(){
    set_ou_base_info("","","","","","","","","","");
}
//填入群组信息
function set_ou_base_info(ou_name,user_num,live_dev_num,live_user_num,
                          sum_use_days,avg_use_days,sum_live_days,avg_live_days,avg_live_percentage,
                          uses_live_beyond_per){

    $("#ou_name").html(ou_name);
    $("#user_num").html(user_num);
    $("#live_dev_num").html(live_dev_num);
    $("#live_user_num").html(live_user_num);
    $("#avg_use_days").html(avg_use_days);
    $("#sum_use_days").html(sum_use_days);
    $("#avg_live_days").html(avg_live_days);
    $("#sum_live_days").html(sum_live_days);
    if(avg_live_percentage!=""){
        var avg_liveness = (parseFloat(avg_live_percentage)*100).toString();
        var avg_liveness_str = avg_liveness.substr(0,avg_liveness.indexOf(".")+2)+"%";
        $("#avg_liveness").html(avg_liveness_str);
    }else{
        $("#avg_liveness").html(avg_live_percentage);
    }
    $("#above_half_liveness").html(uses_live_beyond_per);
}

function reset_chart_info(){
    $("#pie_chart").html("");
    $("#line_chart").html("");
}
//重置工具栏信息
function reset_tool_bar_info(){
    $("#analysis_rule").val(10);
    $("#target").val("per_day_liveness");
    var myDate = new Date;
    var year = myDate.getFullYear();
    var month = myDate.getMonth()+1;
    if(month<10)month = "0"+month;
    $("#year").val(year);
    $("#month").val(month);
}
//显示群组的折线图信息
function show_line_info(oudn){
    if (has_select_span()) {
        //获取在线情况数据，在这需要读取用户的指定显示区间
        var select_time_option = get_online_target();
        var online_data = get_online_data(oudn, select_time_option);
    }
}

function get_online_data(oudn,select_time_option){
    var online_data = {};
    //发送请求过程,根据用户所选的时间区间进行统计
    var liveness_data = {};
    var obj = {
        _path: "/a/wp/org/get_online_data",
        _methods: "get",
        param: {
//            oudn: oudn,
            target:select_time_option,
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        if (rt != 0) {
            loadingStatus("获取群组用户在线情况失败！", 0);
        } else {
            loadingStatus("获取群组用户在线情况成功！", 0);
            online_data = data.online_data;
            var ou_name = get_friendly_ouname(oudn);
            var line_option = generate_chart_option("line", ou_name, online_data);
            draw_line_chart(line_option);
        }
    }, "正在获取群组用户在线情况!");
    //先模拟数据

    return online_data;
}

//显示下面活跃度信息
function show_pie_info(oudn){
    if (has_select_span()) {
        var analysis_rule = $("#analysis_rule").val();
//        var pie_data = get_liveness_data(oudn, analysis_rule);
        var pie_data = get_liveness_data(oudn, 0);

    }
}

function get_liveness_data(oudn,analysis_rule){
    //解析分析原则，传值到后台
    var liveness_data = {};
    var obj = {
        _path: "/a/wp/org/get_liveness_data",
        _methods: "get",
        param: {
//            oudn: oudn,
            analysis_rule:analysis_rule,
            sid: $.cookie("org_session_id")
        }
    };
    ajaxReq(obj, function (data) {
        var rt = data.rt;
        if (rt != 0) {
            loadingStatus("获取群组活跃度信息失败！", 0);
        } else {
            loadingStatus("获取群组活跃度信息成功！", 0);
            liveness_data = data;
            var ou_name = get_friendly_ouname(oudn);
            var pie_option = generate_chart_option("pie", ou_name, liveness_data);
            draw_pie_chart(pie_option);
        }
    }, "正在获取群组活跃度信息!");

    return liveness_data;
}
//生成pie图中的数据选项
function generate_chart_option(type,ou_name,data){
    var option = {};
    if(type=="pie"){
        var legend = [];
        var pie_data = [];
        var percentages = data['data'];
        for(var i=0;i<percentages.length;i++){
            var percentage = percentages[i]['percentage'];
            var num = parseInt(percentages[i]['num']);
            if(num!=0){
                var per_legend = (parseInt(percentage)-20)+"%~"+percentage+"%";
                legend.push(per_legend);
                pie_data.push({name:per_legend,value:num});
            }
        }
        option = {
//            title : {
//                text: '激活用户活跃度统计图',
//                subtext: ou_name,
//                x:'center'
//            },
            tooltip : {
                trigger: 'item',
                formatter: "{a} <br/>{b} : {c} ({d}%)"
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                data: per_legend
            },
            series : [
                {
                    name: '活跃度占比',
                    type: 'pie',
                    radius : '55%',
                    center: ['50%', '40%'],
                    data:pie_data,
                    itemStyle: {
                        emphasis: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }
            ]
        };
    }else if(type=="line"){
        var $target = $("#target");
        var $year = $("#year");
        var $month = $("#month");
        var xAxis_array = [];
        var num_array = [];

        var myDate = new Date;
        var this_year = myDate.getFullYear();
        var this_month = myDate.getMonth()+1;
        var year = $year.val();
        var month = $month.val();
        if($year.val()=="0"){
            year = this_year;
        }
        if($month.val()=="0"){
            month = this_month;
        }
        //如果是按天算的
        if($target.val()=="per_day_liveness"){

            xAxis_array = get_month_day_array(year,month);
            for(var i=0;i<xAxis_array.length;i++){
                var exist_this_day = false;
                for(var j=0;j<data.length;j++){

                    if(xAxis_array[i]==data[j]['time']){
//                        num_array.push(data[j]['online_users'].length);
                        num_array.push(parseInt(data[j]['online_user_length']));
                        exist_this_day = true;
                    }
                }
                if(!exist_this_day)num_array.push(0);
            }
        }else if($target.val()=="per_month_liveness"){
            xAxis_array = get_month_array(year);
            for(var i=0;i<xAxis_array.length;i++){
                num_array.push(get_month_online_users(xAxis_array[i],data));
            }
        }

        option = {
//            title: {
//                text: '在线情况统计图'
//            },
            tooltip : {
                trigger: 'axis'
            },
            toolbox: {
                feature: {
                    saveAsImage: {}
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '4%',
                containLabel: true
            },
            xAxis : [
                {
                    type : 'category',
                    boundaryGap : false,
                    data : xAxis_array
                }
            ],
            yAxis : [
                {
                    type : 'value'
                }
            ],
            series : [
                {
                    name:'在线人数',
                    type:'line',
                    stack: '总量',
                    areaStyle: {normal: {}},
                    data:num_array
                }
            ],
            color :[
                '#36cac9'
            ]
        };
    }
    return option;
}
//获取某年某月中日期的列表
function get_month_day_array(year,month){
    var day_array = [];
    var myDate = new Date();
    var month_str = parseInt(month);
    var day_length = get_month_length(year,month);
    if(parseInt(month)<10)month_str = "0"+month_str;
    for(var i=1;i<=day_length;i++){
        var day = i;
        if(i<10)day = "0"+i;
        day_array.push(year+"-"+month_str+"-"+day);
    }
    return day_array;
}

function get_month_array(year){
    var month_array = [];
    for(var i=1;i<=12;i++){
        var month_str = i;
        if(i<10)month_str = "0"+i;
        month_array.push(year+"-"+month_str);
    }
    return month_array;
}

function get_month_online_users(year_month,data){
    var online_user_count = 0;
    for(var i=0;i<data.length;i++){
        if(data[i]['time'].indexOf(year_month)>-1){
            online_user_count+=parseInt(data[i]['online_user_length']);
        }
    }
    return online_user_count;
}

function get_month_length(year,month){
    var new_year = parseInt(year);    //取当前的年份
    var new_month = parseInt(month) + 1;//取下一个月的第一天，方便计算（最后一天不固定）
    if(new_month>12)            //如果当前大于12月，则年份转到下一年
    {
        new_month -=12;        //月份减
        new_year++;            //年份增
    }
    var first_day_of_this_month = new Date(parseInt(year),parseInt(month)-1);
    var first_day_of_next_month = new Date(new_year,new_month-1);
    var time_length = first_day_of_next_month.getTime()-first_day_of_this_month.getTime();
    var day_length = time_length/(1000*60*60*24);
    return day_length;//获取当月最后一天日期
}

function draw_pie_chart(option){
    var myChart = echarts.init(document.getElementById('pie_chart'));
    // 为echarts对象加载数据
    myChart.setOption(option);
}

function draw_line_chart(option){
    var myChart = echarts.init(document.getElementById('line_chart'));
    // 为echarts对象加载数据
    myChart.setOption(option);
}

function get_friendly_ouname(oudn){
    var ou_name = "";
//    if(oudn==base_dn){
//        ou_name = "系统所有用户"
//    }else{
//        var name_list = oudn.split(",");
//        var len = name_list.length;
//        for(var i=len-3;i>=0;i--){
//            ou_name+=name_list[i].split("=")[1]+",";
//        }
//        ou_name = ou_name.substr(0,ou_name.length-1);
//    }
    return ou_name;
}

//用户选项区域
$("#analysis_rule").change(function(event){
    //当用户修改了分析原则时进行相应的统计图刷新
    var $oudn = $("#oudn");
    show_pie_info($oudn.val());
});
//用户修改在线人数统计范围
$("#target").change(function(event){
    var target_value = $("#target").val();
    var date = new Date();
    var this_year = date.getFullYear();
    var this_month = date.getMonth()+1;
    var month_str = this_month;
    if(this_month<10)month_str = "0"+this_month;
    //这样讲对象缓存起来的效率高
    var $year_selector = $("#year");
    var $month_selector = $("#month");
    if(target_value=="per_day_liveness"){
        //如果用户选择的是每天的在线人数，默认显示该月的在线情况，前面的选框可选
        $year_selector.val(this_year);
        $month_selector.val(month_str);
        $year_selector.removeAttr("disabled");
        $month_selector.removeAttr("disabled");
    }else if(target_value=="per_week_liveness"||target_value=="per_month_liveness"){
        //如果用户选择的是每周的在线人数，默认显示该年每周的在线情况，前面的月选框不可选
        $year_selector.val(this_year);
        $month_selector.val(0);
        $year_selector.removeAttr("disabled");
        $month_selector.attr("disabled","disabled");
    }

    //修改之后需要根据选项动态展示图表，根据选择框动态生成选择日期范围
    show_line_info($("#oudn").val());

});
$("#year").change(function(event){
    show_line_info($("#oudn").val());
});
$("#month").change(function(event){
    show_line_info($("#oudn").val());
});
//用于校验选框选中时的逻辑问题
function verify_input_time(){

}
//根据用户选择情况获取统计在线时间范围
function get_online_target(){
    var target_time = "";
    var $year_selector = $("#year");
    var $month_selector = $("#month");
    var $target = $("#target");
    //实例化当前时间
    var date = new Date();
    var this_year = date.getFullYear();
    var this_month = date.getMonth()+1;
    var select_year = $year_selector.val();
    var select_month = $month_selector.val();
    if($target.val()=="per_day_liveness"){
        if(select_year=="0")select_year = this_year;
        if(select_month=="0"){
            select_month = this_month;
            if(this_month<10){
                select_month="0"+this_month;
            }
        }
        target_time=select_year+"-"+select_month;
    }else if($target.val()=="per_week_liveness"||$target.val()=="per_month_liveness"){
        if(select_year=="0")select_year = this_year;
        target_time=select_year;
    }
    return target_time;

}
