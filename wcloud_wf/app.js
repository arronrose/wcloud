
/**
 * Module dependencies.
 */

var express = require('express');
var routes = require('./routes');
var user = require('./routes/user');
var http = require('http');
var path = require('path');
var config=require('./routes/config');



var app = express();

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));

//app.use(express.bodyParser({uploadDir: './public/files' }));
app.use(express.bodyParser({uploadDir: __dirname + '/public/files' }));
app.use(express.limit(1000000000));

app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}
/*个人版入口*/
app.get('/f_personal_login', routes.perLogin);	//登陆界面
app.get('/f_personal_device',routes.perDevice);	//device,设备管理页面
/*企业版个人入口*/
app.get('/f_per_login', routes.login);	//登陆界面
app.get('/f_per_device',routes.device);	//device,设备管理页面

/*企业入口*/
app.get('/',routes.qiyeLogin);		//企业入口。
app.get('/f_org_login',routes.qiyeLogin);		//企业入口。
app.get('/f_org_acc',routes.acc);
app.get('/f_org_mapp',routes.mapp);
app.get('/f_org_setLDAP',routes.setLDAP);
app.get('/f_org_strategy',routes.strategy);
app.get('/f_org_contacts',routes.contacts);
app.get('/f_org_trace',routes.trace);
app.get('/f_org_home',routes.home);
app.get('/f_org_log',routes.log);   //+++20151106加入日志入口
app.get('/f_org_statistics',routes.statistics);   //+++20151106加入数据统计入口
app.get('/f_org_control',routes.control);
app.get('/f_org_controlInfo',routes.controlInfo);
/*市场*/
app.get('/f_appStore', routes.appStore);
app.post('/f_login',routes.doLogin);		//nodejs发送请求给webserver

//文件上传
app.post('/f_updateLogo',routes.updateLogo);
app.post('/f_upApp',routes.upApp);
//+++ 20150603
app.post('/f_upcel',routes.upcel);
//+++ 20150713 文件备份
app.post('/f_backup',routes.backup);
//+++ 20150717 验证码
app.get('/captcha',routes.getCaptcha);
//+++ 20150803 手机伴侣 和 系统更新的上传
app.post('/f_up_secphone',routes.upSecphone);

/*管理员入口*/
app.get('/f_org_master',routes.master);
app.get('/f_org_master_list',routes.masterlist);
app.get('/f_org_admin_list',routes.adminlist);
app.get('/f_org_setLDAP',routes.setLDAP);

/*安全员入口*/
app.get('/f_org_sa',routes.sa);
app.get('/f_org_sa_list',routes.salist);

/*审计员入口*/
app.get('/f_org_auditor',routes.auditor);
app.get('/f_org_auditor_list',routes.auditorlist);
app.get('/f_org_auditlog',routes.auditlog);

app.get('/f_org_wifi',routes.wifi);
http.createServer(app).listen(config.config.localport, function(){
  console.log('Express server listening on port ' + config.config.localport);
});