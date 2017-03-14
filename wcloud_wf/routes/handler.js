var http=require('http');
var qs=require('querystring');

var config=require("./config");

function handler(req,res)		//req是请求 res是响应
{
	var content=qs.stringify(req.body.param);
	var host,port;
	host=config.config.host;
	port=config.config.port;
	var opt=
	{
		host:host,		//主机名
		port:port,		//端口号码
		path:req.body._path,		//路径
		method:req.body._methods,	//方法post或者get
	    headers:{
	    'Content-Type':'application/x-www-form-urlencoded',
	    'Content-Length':content.length
	    }
	};
	if(req.body._methods=='get')		//如果是发送get请求，将centent附加在path后面。
	{
		if(!!content){
			opt.path=req.body._path+'?'+content;
		}else{
			opt.path=req.body._path;
		}
		opt.headers=null;
		content=null;
	}
	//console.log(req.body);
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
exports.handler = handler;