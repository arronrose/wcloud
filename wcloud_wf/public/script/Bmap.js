// JavaScript Document
//创建和初始化地图函数：
function initMap(){
    createMap();//创建地图
    setMapEvent();//设置地图事件
    addMapControl();//向地图添加控件
    //addMarker();
}
    
    //创建地图函数：
    function createMap(){
        var map = new BMap.Map("dituContent");//在百度地图容器中创建一个地图
        var point = new BMap.Point(113.351021,23.131864);//定义一个中心点坐标
        map.centerAndZoom(point,10);//设定地图的中心点和坐标并将地图显示在地图容器中
        window.map = map;//将map变量存储在全局
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
     //标注点数组
   // var markerArr = [{title:"设备",content:"我在这里",point:{lot:116.498515,lat:39.269008},isOpen:1,icon:{w:21,h:21,l:0,t:0,x:6,lb:5}}//
    //     ];
    var markerArr = [];
    var strmarkerArr = [];// {title:"策略"+i,desc:"作用中心："+strategys[i].desc,radius:"半径："+strategys[i].radius,point:{lot:parseFloat(strategys[i].lon),
//                                lat:parseFloat(strategys[i].lat)},isOpen:1,icon:{w:25,h:25,l:45,t:21,x:6,lb:5}};
    //创建marker
    function addMarker(){
//        if(window.marker)
//        {
//          map.removeOverlay(window.marker);          //当marker存在时，定义下一个位置的时候，首先删除原来的marker
//        }
        map.clearOverlays();

        //如果策略信息为空，则需要去数据库中加载
        if(strmarkerArr.length==0)
        {
            getlocs();
        }
        else{
            addstrcircles();
        }

        //添加策略
        for(var i=0;i<markerArr.length;i++){
            var json = markerArr[i];
            var p0 = json.point.lot;
            var p1 = json.point.lat;
            var point = new BMap.Point(p0,p1);
            var iconImg = createIcon(json.icon);
           // var iconImg = createIcon({w:21,h:21,l:0,t:0,x:6,lb:5});
//            if(window.marker)
//            {
//                map.removeOverlay(window.marker);          //当marker存在时，定义下一个位置的时候，首先删除远来的marker
//            }
            var marker = new BMap.Marker(point,{icon:iconImg});
//            window.marker=marker;       //将marker共享到全局。
            var iw = createInfoWindow(i);
            var label = new BMap.Label(json.title,{"offset":new BMap.Size(json.icon.lb-json.icon.x+10,-20)});
            marker.setLabel(label);
            map.panTo(point);       //添加标记之后，视图跳转（point中心点）
            map.addOverlay(marker);
            label.setStyle({
                        borderColor:"#808080",
                        color:"#333",
                        cursor:"pointer"
            });
            
            (function(){
                var index = i;
                var _iw = createInfoWindow(i);
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
                    //_marker.openInfoWindow(_iw);
                }
            })()
        }
    }
    function addstrcircles()
    {
//        alert(strmarkerArr.length);
        for(var i=0;i<strmarkerArr.length;i++){
            var json = strmarkerArr[i];
            var p0 = json.point.lot;
            var p1 = json.point.lat;
            var point = new BMap.Point(p0,p1);
            var iconImg = createIcon(json.icon);
            var marker = new BMap.Marker(point,{icon:iconImg});
            var label = new BMap.Label(json.title,{"offset":new BMap.Size(json.icon.lb-json.icon.x+10,-20)});
            marker.setLabel(label);
            map.panTo(point);       //添加标记之后，视图跳转（point中心点）
            map.addOverlay(marker);
            label.setStyle({
                borderColor:"#808080",
                color:"#333",
                cursor:"pointer"
            });
            var circle1 = new BMap.Circle(point,json.radius,{fillColor:"blue", strokeWeight: 1 ,fillOpacity: 0.3, strokeOpacity: 0.3});
            map.addOverlay(circle1);

            (function(){
//                var index = i;
                var _iw = createInfoWindow1(json);
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
                    //_marker.openInfoWindow(_iw);
                }
            })()
        }
    }
    //创建InfoWindow
    function createInfoWindow(i){
        var json = markerArr[i];
        var iw = new BMap.InfoWindow("<b class='iw_poi_title' title='" + json.title + "'>" + json.title + "</b><div class='iw_poi_content'>"+json.content+"</div>");
        return iw;
    }
    function createInfoWindow(json){
//    var json = markerArr[i];
    var iw = new BMap.InfoWindow("<b class='iw_poi_title' title='" + json.title + "'>" + json.title + "</b><div class='iw_poi_content'>"+json.content+"</div>");
    return iw;
}
    function createInfoWindow1(json){
//        var json = markerArr[i];
//        alert("createInfoWindow1");
        var str ="<b class='iw_poi_title' title='" + json.title + "'>" + json.title + "</b>";
        str+="<div class='iw_poi_desc'>"+"作用地点："+json.desc+"</div>";
        str+="<div class='iw_poi_radius'>"+"作用半径："+json.radius+"米"+"</div>";
        str+="<div class='iw_poi_start'>"+"开始时间："+json.start+"</div>";
        str+="<div class='iw_poi_radius'>"+"结束时间："+json.end+"</div>";
        str+="<div style='font-size: 12px; color: red'>"+"(更多详细信息请查看策略配置...)"+"</div>"
        var iw = new BMap.InfoWindow(str);
//        var iw = new BMap.InfoWindow("<b class='iw_poi_title' title='" + json.title + "'>" + json.title + "</b><div class='iw_poi_desc'>"+"作用地点："+json.desc+"</div><div class='iw_poi_radius'>"+"作用半径："+json.radius+"</div>");
        return iw;
    }
    //创建一个Icon
    function createIcon(json){
        var icon = new BMap.Icon("http://app.baidu.com/map/images/us_mk_icon.png", new BMap.Size(json.w,json.h),{imageOffset: new BMap.Size(-json.l,-json.t),infoWindowOffset:new BMap.Size(json.lb+5,1),offset:new BMap.Size(json.x,json.h)})
        return icon;
    }
    
    initMap();//创建和初始化地图

    function showdialog() {
        window.prompt('URL','');
    }