/**
 * Created by arron_rose on 2017/2/21.
 */
//初始化地图空间
function initMap(){
    createMap();//创建地图
    citywifiinfos();
    //addpoint(cityname);
}
//创建地图函数
function createMap(){
    var cityname = document.getElementById("choosecity").value;
    var map = new BMap.Map("mainMap");//在百度地图容器中创建一个地图
    var point = new BMap.Point(116.403936,39.915125);//定义中心点坐标，天安门广场
    map.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中，10指的是缩放的比例，0-19 一般取15
    map.setCurrentCity("北京市");// 右下角小地图的图示为（北京市）
    window.map = map;//将map变量存储在全
    setMapEvent();//设置地图事件
    addMapControl();//向地图添加控件
    addpoint(cityname);
}

//地图事件设置函数：
function setMapEvent(){
    map.enableDragging();//启用地图拖拽事件，默认启用(可不写)
    map.enableScrollWheelZoom();//启用地图滚轮放大缩小
    map.enableDoubleClickZoom();//启用鼠标双击放大，默认启用(可不写)
    map.enableKeyboard();//启用键盘上下左右键移动地图
}
//地图控件添加函数：
function addMapControl(){
    //向地图中添加缩放控件
    var ctrl_nav = new BMap.NavigationControl({anchor:BMAP_ANCHOR_TOP_LEFT,type:BMAP_NAVIGATION_CONTROL_LARGE});
    map.addControl(ctrl_nav);
    //向地图中添加缩略图控件
    var ctrl_ove = new BMap.OverviewMapControl({anchor:BMAP_ANCHOR_BOTTOM_RIGHT,isOpen:1});
    map.addControl(ctrl_ove);
    //向地图中添加比例尺控件
    var ctrl_sca = new BMap.ScaleControl({anchor:BMAP_ANCHOR_BOTTOM_LEFT});
    map.addControl(ctrl_sca);
}

$("#choosecity").change(function(){
    var cityname = document.getElementById("choosecity").value;
    if(cityname=="qingdao"){
        var map = new BMap.Map("mainMap");//在百度地图容器中创建一个地图
        var point = new BMap.Point(120.377835,36.065988);//定义中心点坐标，天安门广场
        map.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中，10指的是缩放的比例，0-19 一般取15
        map.setCurrentCity("青岛市");// 右下角小地图的图示为（北京市）
        window.map = map;//将map变量存储在全局
        setMapEvent();//设置地图事件
        addMapControl();//向地图添加控件
        addpoint(cityname)
    }
    if(cityname=="guangzhou"){
        var map = new BMap.Map("mainMap");//在百度地图容器中创建一个地图
        var point = new BMap.Point(113.259029,23.131735);//定义中心点坐标，天安门广场
        map.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中，10指的是缩放的比例，0-19 一般取15
        map.setCurrentCity("广州市");// 右下角小地图的图示为（北京市）
        window.map = map;//将map变量存储在全局
        setMapEvent();//设置地图事件
        addMapControl();//向地图添加控件
        addpoint(cityname)
    }
    if(cityname=="beijing"){
        var map = new BMap.Map("mainMap");//在百度地图容器中创建一个地图
        var point = new BMap.Point(116.403936,39.915125);//定义中心点坐标，天安门广场
        map.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中，10指的是缩放的比例，0-19 一般取15
        map.setCurrentCity("北京市");// 右下角小地图的图示为（北京市）
        window.map = map;//将map变量存储在全
        setMapEvent();//设置地图事件
        addMapControl();//向地图添加控件
        addpoint(cityname);
    }
});
function addpoint(cityname){
    var obj={
        _path:"/a/wp/org/citywifiinfos1",
        _methods:"get",
        param:{
            city:cityname
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all_all = data.all_all;
        var all_danger = data.all_danger;
        if (rt != 0) {
            loadingStatus("获取wifi信息失败！", 0);
        } else {
            loadingStatus("成功获取wifi信息！", 0);
            a=all_danger.length;
            b=all_all.length;
            document.getElementById("detailMapPubDan").innerHTML=a;
            document.getElementById("detailMapPubSafe").innerHTML=b;
            document.getElementById("detailMapAll").innerHTML=a+b;
            for(i=0;i<all_all.length;i++){
                beijingall(all_all[i]);
            }
            for(i=0;i<all_danger.length;i++) {
                beijingdanger(all_danger[i]);
            }

        }
    },"正在获取wifi信息!");
}
//wifi
//function citywifiinfos(cityname){
//    var obj={
//        _path:"/a/wp/org/citywifiinfos",
//        _methods:"get",
//        param:{
//            city:cityname
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt = data.rt;
//        var all_all = data.all_all;
//        var all_danger = data.all_danger;
//        if (rt != 0) {
//            loadingStatus("获取wifi信息失败！", 0);
//        } else {
//            loadingStatus("成功获取wifi信息！", 0);
//            a=all_danger.length;
//            b=all_all.length;
//            document.getElementById("detailMapPubDan").innerHTML=a;
//            document.getElementById("detailMapPubSafe").innerHTML=b;
//            document.getElementById("detailMapAll").innerHTML=a+b;
//            for(i=0;i<all_all.length;i++){
//                beijingall(all_all[i]);
//            }
//            for(i=0;i<all_danger.length;i++) {
//                beijingdanger(all_danger[i]);
//            }
//
//            }
//    },"正在获取wifi信息!");
//}
//危险
function beijingdanger(info){
    lon=parseFloat(info[2]);
    lat=parseFloat(info[3]);
    ssid=info[0];
    mac=info[1];
    var icons='images/danger.png';
    var point = new BMap.Point(lon,lat);
    var marker = new BMap.Marker(point);
    var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
    marker.setIcon(icon);
    var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
    marker.addEventListener("click", function(){
        this.openInfoWindow(infoWindow);
    });
    map.addOverlay(marker);
}
//全部wifi显示
function beijingall(info){
    if(info[0]!=''){
        lon=parseFloat(info[2]);
        lat=parseFloat(info[3]);
        ssid=info[0];
        mac=info[1];
        var icons='images/safe.png';
        var point = new BMap.Point(lon,lat);
        var marker = new BMap.Marker(point);
        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
        marker.setIcon(icon);
        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
        marker.addEventListener("click", function(){
            this.openInfoWindow(infoWindow);
        });
        map.addOverlay(marker);
    }else{
        lon=parseFloat(info[2]);
        lat=parseFloat(info[3]);
        ssid="unknown";
        mac=info[1];
        var icons='images/unknown.png';
        var point = new BMap.Point(lon,lat);
        var marker = new BMap.Marker(point);
        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
        marker.setIcon(icon);
        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
        marker.addEventListener("click", function(){
            this.openInfoWindow(infoWindow);
        });
        map.addOverlay(marker);
    }
}



////青岛
//function citywifiinfos2(cityname){
//    var obj={
//        _path:"/a/wp/org/citywifiinfos2",
//        _methods:"get",
//        param:{
//            city:cityname
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt = data.rt;
//        var all_all = data.all_all;
//        var all_danger = data.all_danger;
//        if (rt != 0) {
//            loadingStatus("获取wifi信息失败！", 0);
//        } else {
//            loadingStatus("成功获取wifi信息！", 0);
//            a=all_danger.length;
//            b=all_all.length;
//            document.getElementById("qdPubDan").innerHTML=a;
//            document.getElementById("qdPubSafe").innerHTML=b;
//            document.getElementById("qdAll").innerHTML=a+b;
//            for(i=0;i<all_all.length;i++){
//                qingdaoall(all_all[i]);
//            }
//            for(i=0;i<all_danger.length;i++) {
//                qingdaodanger(all_danger[i]);
//            }
//
//        }
//    },"正在获取wifi信息!");
//}
////青岛危险
//function qingdaodanger(info){
//    lon=parseFloat(info[2]);
//    lat=parseFloat(info[3]);
//    ssid=info[0];
//    mac=info[1];
//    var icons='images/danger.png';
//    var point = new BMap.Point(lon,lat);
//    var marker = new BMap.Marker(point);
//    var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//    marker.setIcon(icon);
//    var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//    marker.addEventListener("click", function(){
//        this.openInfoWindow(infoWindow);
//    });
//    map1.addOverlay(marker);
//}
////青岛的全部wifi显示
//function qingdaoall(info){
//    if(info[0]!=''){
//        lon=parseFloat(info[2]);
//        lat=parseFloat(info[3]);
//        ssid=info[0];
//        mac=info[1];
//        var icons='images/safe.png';
//        var point = new BMap.Point(lon,lat);
//        var marker = new BMap.Marker(point);
//        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//        marker.setIcon(icon);
//        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//        marker.addEventListener("click", function(){
//            this.openInfoWindow(infoWindow);
//        });
//        map1.addOverlay(marker);
//    }else{
//        lon=parseFloat(info[2]);
//        lat=parseFloat(info[3]);
//        ssid="unknown";
//        mac=info[1];
//        var icons='images/unknown.png';
//        var point = new BMap.Point(lon,lat);
//        var marker = new BMap.Marker(point);
//        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//        marker.setIcon(icon);
//        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//        marker.addEventListener("click", function(){
//            this.openInfoWindow(infoWindow);
//        });
//        map1.addOverlay(marker);
//    }
//}
//
//
////广州
//function citywifiinfos3(cityname){
//    var obj={
//        _path:"/a/wp/org/citywifiinfos3",
//        _methods:"get",
//        param:{
//            city:cityname
//        }
//    };
//    ajaxReq(obj,function(data){
//        var rt = data.rt;
//        var all_all = data.all_all;
//        var all_danger = data.all_danger;
//        if (rt != 0) {
//            loadingStatus("获取wifi信息失败！", 0);
//        } else {
//            loadingStatus("成功获取wifi信息！", 0);
//            a=all_danger.length;
//            b=all_all.length;
//            document.getElementById("gzPubDan").innerHTML=a;
//            document.getElementById("gzPubSafe").innerHTML=b;
//            document.getElementById("gzAll").innerHTML=a+b;
//            for(i=0;i<all_all.length;i++){
//                guangzhouall(all_all[i]);
//            }
//            for(i=0;i<all_danger.length;i++) {
//                guangzhoudanger(all_danger[i]);
//            }
//
//        }
//    },"正在获取wifi信息!");
//}
////广州的危险wifi显示
//function guangzhoudanger(info){
//    lon=parseFloat(info[2]);
//    lat=parseFloat(info[3]);
//    ssid=info[0];
//    mac=info[1];
//    var icons='images/danger.png';
//    var point = new BMap.Point(lon,lat);
//    var marker = new BMap.Marker(point);
//    var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//    marker.setIcon(icon);
//    var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//    marker.addEventListener("click", function(){
//        this.openInfoWindow(infoWindow);
//    });
//    map2.addOverlay(marker);
//}
////广州的全部wifi显示
//function guangzhouall(info){
//    if(info[0]!=''){
//        lon=parseFloat(info[2]);
//        lat=parseFloat(info[3]);
//        ssid=info[0];
//        mac=info[1];
//        var icons='images/safe.png';
//        var point = new BMap.Point(lon,lat);
//        var marker = new BMap.Marker(point);
//        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//        marker.setIcon(icon);
//        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//        marker.addEventListener("click", function(){
//            this.openInfoWindow(infoWindow);
//        });
//        map2.addOverlay(marker);
//    }else{
//        lon=parseFloat(info[2]);
//        lat=parseFloat(info[3]);
//        ssid="unknown";
//        mac=info[1];
//        var icons='images/unknown.png';
//        var point = new BMap.Point(lon,lat);
//        var marker = new BMap.Marker(point);
//        var icon = new BMap.Icon(icons, new BMap.Size(30, 25));
//        marker.setIcon(icon);
//        var infoWindow = new BMap.InfoWindow("<p style='font-size:14px;'>"+ssid+' : '+mac+"</p>");
//        marker.addEventListener("click", function(){
//            this.openInfoWindow(infoWindow);
//        });
//        map2.addOverlay(marker);
//    }
//}

initMap();




//全国的
function citywifiinfos(){
    var obj={
        _path:"/a/wp/org/citywifiinfos",
        _methods:"get",
        param:{
            city:"all"
        }
    };
    ajaxReq(obj,function(data){
        var rt = data.rt;
        var all=data.all;
        var all_dangerous=data.all_dangerous;
        nationalmap(all);
        if (rt != 0) {
            loadingStatus("获取wifi信息失败！", 0);
        } else {
            loadingStatus("成功获取wifi信息！", 0);
            //所有的统计数据：
            document.getElementById("wholeAll").innerHTML=all['all'][0];
            document.getElementById("wholePubSafe").innerHTML=all['all'][1];
            document.getElementById("wholePubDan").innerHTML=all['all'][2];
            a=0
            for(i=0;i<Number(all['all'][2]);i++){
                a++;
                var txt;
                txt = "";
                txt += '<tr class="' + uid + '">';
                txt += '<td class="xuhao" style="width=20%">' + a + '</td>';
                txt += '<td class="uid" style="width=30%">' +all_dangerous[i][0] + '</td>';
                txt += '<td class="mac" style="width=40%">'+all_dangerous[i][1]+'</td></tr>';
                $("#yglb tbody").append(txt);

            }
            $("#shebeiB").mCustomScrollbar("update");

        }
    },"正在获取wifi信息!");
}





//20170227全国wifi分布情
function nationalmap(all){
    console.log(all);
    a=all['beijing'][0];
    b=all['qingdao'][0];
    c=all['guangzhou'][0];
    sum=a+b+c;
    sum2=all['beijing'][1]+all['qingdao'][1]+all['guangzhou'][1];
    sum3=all['beijing'][2]+all['qingdao'][2]+all['guangzhou'][2];

    //value1=(a/sum)*200;
    //value2=(b/sum)*200;
    //value3=(c/sum)*200;
    value1=40;
    value2=80;
    value3=120;
    var myChart = echarts.init(document.getElementById('chinaMap'));

    var data = [
        {name: '北京', value: value1,},
        {name: '青岛', value: value2,},
        {name: '广州', value: value3,}
    ];
    var geoCoordMap = {
        '北京':[116.46,39.92],
        '青岛':[120.38,36.07],
        '广州':[113.26,23.13]
    };
    var convertData = function (data) {
        var res = [];
        for (var i = 0; i < data.length; i++) {
            var geoCoord = geoCoordMap[data[i].name];
            if (geoCoord) {
                res.push({
                    name: data[i].name,
                    value: geoCoord.concat(data[i].value)
                });
            }
        }
        return res;
    };
    option = {
        backgroundColor: '#404a59',
        title: {
            text: 'Wi-Fi主要城市分布',
            //subtext: 'data from PM25.in',
            //sublink: 'http://www.pm25.in',
            left: 'center',
            textStyle: {
                color: '#fff'//白色
            }
        },
        tooltip : {
            trigger: 'item'
        },
        geo: {
            map: 'china',
            label: {
                emphasis: {
                    show: false
                }
            },
            roam: true,
            itemStyle: {
                normal: {
                    areaColor: '#323c48',
                    borderColor: '#111'
                },
                emphasis: {
                    areaColor: '#2a333d'
                }
            }
        },
        series : [
            {
                type: 'effectScatter',
                coordinateSystem: 'geo',
                data: convertData(data.sort(function (a, b) {
                    return b.value - a.value;
                }).slice(0, 6)),
                symbolSize: function (val) {
                    return val[2] / 10;
                },
                showEffectOn: 'render',
                rippleEffect: {
                    brushType: 'stroke'
                },
                hoverAnimation: true,
                label: {
                    normal: {
                        formatter: '{b}',
                        position: 'right',
                        show: true
                    }
                },
                itemStyle: {
                    normal: {
                        color: '#f4e925',//黄色
                        shadowBlur: 10,
                        shadowColor: '#333'

                    }
                },
                zlevel: 1
            }
        ],
        visualMap: [
            {
                left: 'right',
                bottom: '5%',
                dimension: 2,
                min: 0,
                max:200,
                itemHeight: 120,
                calculable: true,
                precision: 0.1,
                text: ['高','低'],
                textGap: 30,
                textStyle: {
                    color: 'yellow'
                },
                inRange: {
                    colorLightness: [1, 0.5]
                },
                //outOfRange: {
                //    color: ['rgba(255,255,255,.2)']
                //},
                controller: {
                    inRange: {
                        //color: ['#c23531']//朱红色
                        color: ['yellow']//朱红色
                    },
                    //outOfRange: {
                    //    //color: ['#444']//深蓝色
                    //    color: ['red']
                    //}
                }
            }
        ],
    };
    myChart.setOption(option);


};






