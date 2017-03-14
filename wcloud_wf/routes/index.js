
/*
 * GET home page.
*/
var http=require('http');
var qs=require('querystring');
var ajax=require('./handler');
var fs=require('fs');
var Path=require('path');

var config=require("./config");

//+++ 20150717 验证码生成
var crypto = require('crypto');
var ccap = require('ccap')({
    width:256,//set width,default is 256
    height:60,//set height,default is 60
    offset:40,//set text spacing,default is 40
    quality:40,//set pic quality,default is 50
    fontsize:57//set font size,default is 57
});//Instantiated ccap class
exports.getCaptcha = function (request, response) {
    var ary = ccap.get();
    var txt = ary[0];
    var buf = ary[1];
    //cookies文本加密(先转换为小写)
    var txt2=txt.toLocaleLowerCase();
    var sha1=crypto.createHash('sha1');
    sha1.update(txt2);
    var encry_captcha=sha1.digest('hex');
    //var session_id=create_session();
    var session_id= '';
    //+++ 20150804 将session在浏览器端设置cookie，若有cookie则不必重新生成
    var Bcookie=request.headers.cookie;
    if(Bcookie){
        var cookieWeb=parseCookie(Bcookie);
        if(!cookieWeb['capSession']){
            session_id=create_session();
            response.cookie('capSession',session_id,{path:'/'});
        }else{
            session_id=cookieWeb['capSession'];
        }
    }else{
        session_id=create_session();
        response.cookie('capSession',session_id,{path:'/'});
    }
    console.log("session_id:"+session_id);
    //将session_id和encry_captcha缓存到数据库中，用做校验
    if(session_id.length>0 && encry_captcha.length>0){
        cacheCookie(session_id,encry_captcha);
    }
    //显示验证码图片
    response.end(buf);
};
//+++ 20150804 create_session
function create_session(){
    var token=Math.random().toString();
    var sha1=crypto.createHash('sha1');
    sha1.update(token);
    var session=sha1.digest('hex');
    return session;
}
//parse cookie
function parseCookie(cookieString){
    var cookies = {};
    var pairs = cookieString.split(/[;,] */);
    for (var i =0; i < pairs.length; i++){
        var idx = pairs[i].indexOf('=');
        var key = pairs[i].substr(0, idx);
        var val = pairs[i].substr(++idx, pairs[i].length).trim();
        cookies[key] = val;
    }
    return cookies;
}
//cache cookie and session to db (via 后台)
function cacheCookie(session_id,captcha){
    var content=qs.stringify({
        session_id: session_id,
        captcha:captcha
    });
    var host,port;
    host=config.config.host;
    port=config.config.port;
    var opt=
    {
        host:host,		//主机名
        port:port,		//端口号码
        path:'/a/wp/org/set_captcha',		//路径
        method:'post',	//方法post或者get
        headers:{
            'Content-Type':'application/x-www-form-urlencoded',
            'Content-Length':content.length
        }
    };
    var body='';
    var requ=http.request(opt,function(resp)
    {
        resp.setEncoding('utf8');
        resp.on('data',function(d)
        {
            body+=d;
        }).on('end',function()
        {
            res.send(body);
        });
    }).on('error',function(e)
    {
        console.log("错误内容："+e.message);
    });
    if(!!content)		//如果是post方法，centent应该不为空。get方法不发送请求主体（已经附加到path中）。
    {
        requ.write(content);
    }
    requ.end();
}
/*************************************/

var rendObj={
	dev_id:"加载中...",
	pnumber:"加载中...",
  title: 'WorkPhone Manager'
};
exports.perLogin = function(req, res){
  res.render('plogin',rendObj);
}
exports.perDevice = function(req, res){
  res.render('pdevice',rendObj);
}

exports.login = function(req, res){
  res.render('login', rendObj);
};
exports.device = function(req, res){
  res.render('device', rendObj);
};
exports.qiyeLogin = function(req, res){
  res.render('qiyeLogin', rendObj);
};
exports.acc = function(req, res){
  res.render('acc', rendObj);
};
exports.mapp = function(req, res){
  res.render('mapp', rendObj);
};
exports.setLDAP = function(req, res){
  res.render('setLDAP', rendObj);
};
exports.strategy = function(req, res){
  res.render('strategy', rendObj);
};
exports.trace = function(req, res){
    res.render('trace', rendObj);
};
exports.contacts = function(req, res){
    res.render('contacts', rendObj);
};
exports.home = function(req, res){
  res.render('home', rendObj);
};
exports.log = function(req, res){
  res.render('log', rendObj);
};

exports.appStore = function(req, res){
  res.render('appStore',rendObj);
};
exports.control = function(req, res){
    res.render('control',rendObj);
};
exports.controlInfo = function(req, res){
    res.render('controlInfo',rendObj);
};
exports.wifi = function(req, res){
    res.render('wifi',rendObj);
};

//+++20151230加入数据统计界面
exports.statistics = function(req,res){
    res.render('statistics',rendObj);
}
exports.doLogin = function(req,res){
  ajax.handler(req,res);
};

exports.master = function(req, res){
    res.render('master', rendObj);
};

exports.masterlist = function(req, res){
    res.render('masterlist', rendObj);
};

exports.orglist = function(req, res){
    res.render('orglist', rendObj);
};

exports.adminlist = function(req, res){
    res.render('adminlist', rendObj);
};

exports.sa = function(req, res){
    res.render('sa', rendObj);
};

exports.salist = function(req, res){
    res.render('salist', rendObj);
};

exports.auditor = function(req, res){
    res.render('auditor', rendObj);
};

exports.auditorlist = function(req, res){
    res.render('auditorlist', rendObj);
};

exports.auditlog = function(req, res){
    res.render('auditlog', rendObj);
};


//上传文件
exports.upApp=function(req,res){
  var type=req.body.lesTy;
  var lei=req.body.lei;
  var path=req.files.apll.path;
  var jq=Path.resolve(__dirname, '..', path);
  var mark=req.body.mark;
  var apptype=req.body.lei;//$("#lei").val();
  var appName=req.body.appName;
  var url=req.body.url;
  if(type=="add"){    //上传应用
        req.body={
          _path:'/a/was/add_native_app',
          _methods:'post',
          param:{
            apk_path: jq,
            remark:mark,
            apptype:apptype
          }
        };
        handler(req,res);
  }else if(type="update"){  //升级本地应用。
    req.body={
      _path:"/a/was/update_native_app",
      _methods:"post",
      param:{
        apk_path:jq,
        remark:mark,
        apptype:apptype
      }
    };
      handler(req,res);
  }
}
exports.updateLogo=function(req,res){
  var pat=req.files.logtu.path;
  var filetype=req.files.logtu.headers['content-type']
  if(filetype=='image/jpeg'||filetype=='image/png'){
    fs.readFile(pat,function(err,data){
      if(err){
        console.log(err);
      }
      var base64=new Buffer(data).toString('base64');
      var sid=req.body.lsid;
      var type='';
      if(filetype=='image/jpeg') type='jpg'
      if(filetype=='image/png') type='png'
      req.body={
        _path:'/a/wp/org/logo',
        _methods:'post',
        param:{
          sid:sid,
          logo_base64:base64,
          img_type:type
        }
      };
      handler(req,res);
    })
  }else{
    res.send('<script>parent.typeerr()</script>');
  }
}

function handler(req,res){   //req是请求 res是响应
  var content=qs.stringify(req.body.param);
  var host,port;
  host=config.config.host;
  port=config.config.port;
  var opt=
  {
    host:host,    //主机名
    port:port,    //端口号码
    path:req.body._path,    //路径
    method:req.body._methods, //方法post或者get
      headers:{
      'Content-Type':'application/x-www-form-urlencoded',
      'Content-Length':content.length
      }
  };
  if(req.body._methods=='get')    //如果是发送get请求，将content附加在path后面。
  {
    if(!!content){
      opt.path=req.body._path+'?'+content;
    }else{
      opt.path=req.body._path;
    }
    opt.headers=null;
    content=null;
  }
  var body='';
  var requ=http.request(opt,function(resp)
  {
      resp.setEncoding('utf8');
      resp.on('data',function(d)
      {
        body+=d;
      }).on('end',function()
      {
        res.send('<script>parent.waitL('+body+');</script>');
      });
  }).on('error',function(e)
  {
      console.log("错误内容："+e.message);
  });
  if(!!content)   //如果是post方法，centent应该不为空。get方法不发送请求主体（已经附加到path中）。
  {
    requ.write(content);
  }
  requ.end();
}

//+++ 20150713 数据备份 单独APP模块
exports.backup=function(req,res){
    //用户名
    var uid=req.body.uid;
    //备份时间戳（整型）
    var backuptime=req.body.backuptime;
    //data_verify校验："file:md5"
    var data_verify=req.body.data_verify;
    //+++20151204加入覆盖类型字段 1代表覆盖，0代表累加
    var backup_type = req.body.backup_type;
    //文件backupdata(文件的ID)的路径
    var path=req.files.backupfile.path;
    var data_path=Path.resolve(__dirname, '..', path);
    //处理上传数据
    req.body={
        _path:'/a/backup/data_backup',
        _methods:'post',
        param:{
            uid:uid,
            backuptime:backuptime,
            data_verify:data_verify,
            backup_type:backup_type,
            data_path: data_path
        }
    };
    backup_handler(req,res);
};
function backup_handler(req,res){
    var content=qs.stringify(req.body.param);
    var host,port;
    host=config.config.host;
    port=config.config.port;
    var opt=
    {
        host:host,    //主机名
        port:port,    //端口号码
        path:req.body._path,    //路径
        method:req.body._methods, //方法post或者get
        headers:{
            'Content-Type':'application/x-www-form-urlencoded',
            'Content-Length':content.length
        }
    };
    if(req.body._methods=='get')    //如果是发送get请求，将content附加在path后面。
    {
        if(!!content){
            opt.path=req.body._path+'?'+content;
        }else{
            opt.path=req.body._path;
        }
        opt.headers=null;
        content=null;
    }
    var body='';
    var requ=http.request(opt,function(resp)
    {
        resp.setEncoding('utf8');
        resp.on('data',function(d)
        {
            body+=d;
        }).on('end',function()
        {
            res.send(body);
        });
    }).on('error',function(e)
    {
        console.log("错误内容："+e.message);
    });
    if(!!content)   //如果是post方法，centent应该不为空。get方法不发送请求主体（已经附加到path中）。
    {
        requ.write(content);
    }
    requ.end();
}

//+++ 20150603 上传excel
exports.upcel=function(req,res){
    var excelpath=req.files.excel.path;
    var ep=Path.resolve(__dirname, '..', excelpath);
    req.body={
        _path:'/a/wp/org/upldap_excel',
        _methods:'post',
        param:{
            excel_path: ep
        }
    };
    upexcel_handler(req,res);
}

function upexcel_handler(req,res){
    var content=qs.stringify(req.body.param);
    var host,port;
    host=config.config.host;
    port=config.config.port;
    var opt=
    {
        host:host,    //主机名
        port:port,    //端口号码
        path:req.body._path,    //路径
        method:req.body._methods, //方法post或者get
        headers:{
            'Content-Type':'application/x-www-form-urlencoded',
            'Content-Length':content.length
        }
    };
    if(req.body._methods=='get')    //如果是发送get请求，将content附加在path后面。
    {
        if(!!content){
            opt.path=req.body._path+'?'+content;
        }else{
            opt.path=req.body._path;
        }
        opt.headers=null;
        content=null;
    }
    var body='';
    var requ=http.request(opt,function(resp)
    {
        resp.setEncoding('utf8');
        resp.on('data',function(d)
        {
            body+=d;
        }).on('end',function()
        {
//            res.send(body);
            res.send('<script>parent.waitexcel('+body+');</script>');
        });
    }).on('error',function(e)
    {
        console.log("错误内容："+e.message);
    });
    if(!!content)   //如果是post方法，centent应该不为空。get方法不发送请求主体（已经附加到path中）。
    {
        requ.write(content);
    }
    requ.end();
}

//+++ 20150803 上传手机伴侣 和 系统更新
exports.upSecphone=function(req,res){
    //备份目的路径
    var dir=req.body.up_dir;
    //partnerfile(文件的ID)的路径
    var path=req.files.partnerfile.path;
    //文件名称
    var filename=req.files.partnerfile.originalFilename;
    var data_path=Path.resolve(__dirname, '..', path);
    //处理上传数据
    var remote_dir='/home/wcloud/opt/org/download/'+dir+'/'+filename;
    var exec = require('child_process').exec;
    var cmdStr = 'scp '+data_path+' 192.168.1.15:'+remote_dir;
    exec(cmdStr, function(err,stdout,stderr){
        if(err) {
            res.send('error:'+stderr);
            console.log('error:'+stderr);
        } else {
            console.log('success');
        }
    });
    res.send("上传成功！");
};