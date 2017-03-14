/**
 * Created by gcynewstart on 14-3-24.
 */
var codeArray = {
    '保密局':'01',
    '中科院信工所':'02',
    '办公室':'01',
    '科技处':'02',
    '行政资产处':'03',
    '人事教育处':'04',
    '财务处':'05',
    '质量安保处':'06',
    '一室':'07',
    '二室':'08',
    '三室':'09',
    '四室':'10',
    '五室':'11',
    '工程部':'12',

    '电磁组':'01',
    '无线组':'02',
    '攻防组':'03',
    '网络组':'04',
    '通信组':'05',
    '应用组':'06',


    '所长':'00',
    '副所长':'01',

    '局长':'00',
    '副局长':'01',

    '主任':'02',
    '副主任':'03',

    '组长':'04',
    '副组长':'05',

    '研究员':'02',
    '正高级工程师':'02',
    '副研究员':'03',
    '工程师':'03',
    '助理研究员':'04',
    '助理工程师':'05'
}

function getTitleCode(title){
    //alert("进入code.js文件");
    //alert(department);
    //alert(title);
    //传入参数的格式是‘中科院信工所/四室/无线组’,主任/正高级工程师或者是 工程师
    //部门是比较好编码的，但是加上职位就不太好分了，这的逻辑是给每个部门的正副领导留出00，01两个位置，其余再接着排

    var tcode = '';

    var titles = title.split('/');
    if(titles.length==1){
        tcode= '99'+codeArray[title];
    }
    else{
        for(var i=0;i<titles.length;i++){
            tcode+= codeArray[titles[i]];
        }
    }
    if(tcode==''){
        tcode='9999';//如果一个人的职称编号不知道，就置其为最大
    }
    //alert({'dcode':dcode,'tcode':tcode});
    return tcode;
}

function getDeCode(department){
    var dcode = '';
    var departments = department.split('/');
    for(var i=0;i<departments.length;i++){
        dcode+= codeArray[departments[i]];
    }
    return dcode;
}