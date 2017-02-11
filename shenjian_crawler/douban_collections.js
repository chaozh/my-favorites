/*
  实时获取近5、10、30、60日个股上榜统计数据。包括上榜次数、累积购买额、累积卖出额、净额、买入席位数和卖出席位数。
*/
var uid = "";//@input(uid,查询的身份证号)
var pwd = "";//@input(pwd,社保查询密码，登录地址：http://www.bjrbj.gov.cn/csibiz/indinfo/login.jsp)
var year = "";//@input(year,查询年份)

var days="5";//@input(days,统计周期,5、10、30和60日，默认为5日)

var configs = {
    domains: ["finance.sina.com.cn"],
    scanUrls: [],
    fields: [ // API只抽取scanurls中的网页，并且不会再自动发现新链接
        {
            name: "items",
            selector: "//table[@id='dataTable']//tr", 
            repeated: true,
            children: [
              {
                  name: "code",
                  alias: "股票代码",
                  selector: "//td[1]/a/text()", 
                  required: true 
              },
              {
                  name: "name",
                  alias: "股票名称",
                  selector: "//td[2]/a/text()",
                  required: true 
              },
              {
                  name: "count",
                  alias: "上榜次数",
                  selector: "//td[3]" 
              },
              {
                  name: "bamount",
                  alias: "累积购买额(万)",
                  selector: "//td[4]" 
              },
              {
                  name: "samount",
                  alias: "累积卖出额(万)",
                  selector: "//td[5]" 
              },
              {
                  name: "net",
                  alias: "净额(万)",
                  selector: "//td[6]" 
              },
              {
                  name: "bcount",
                  alias: "买入席位数",
                  selector: "//td[7]" 
              },
              {
                  name: "scount",
                  alias: "卖出席位数",
                  selector: "//td[8]" 
              }
            ]
        }
    ]
};

configs.beforeCrawl = function(site){
  if(uid==="" || uid===null){
    system.exit("请输入要查询的身份证号");
  }
  if(pwd==="" || pwd===null){
    system.exit("请输入社保查询密码");
  }
  if(year==="" || year===null){
    system.exit("请输入要查询的年份");
  }
  // １、识别登录页面的验证码，使用神箭手的内置函数 getCaptcha
  var safecodedata = getCaptcha(52, "http://www.bjrbj.gov.cn/csibiz/indinfo/validationCodeServlet.do");
  var safecode = JSON.parse(safecodedata);  
  if(safecode.ret > 0){
    // 验证码识别结果正常返回后，生成登录请求的post参数
    var options = {
      method: "POST",
      data: {
          type:"1",
          flag:"3",
          j_username: uid,
          j_password: pwd,
          safecode:safecode.result
      }
    };
    // ２、发送登录请求模拟登录。神箭手会自动保存cookie，并在以后的请求中使用之前保存的所有cookie
    site.requestUrl("http://www.bjrbj.gov.cn/csibiz/indinfo/login_check", options);
  
    if(days!=="5" && days!=="10" && days!=="30" && days!=="60"){
      system.exit("输入的统计周期错误。"); // 停止调用，返回自定义错误信息
    }
    // 根据输入值生成要解析的网页url，并添加到scanurl中
    var url = "http://vip.stock.finance.sina.com.cn/q/go.php/vLHBData/kind/ggtj/index.phtml?last="+days+"&p=1";
    site.addScanUrl(url);
};

var fetcher = new Fetcher(configs);
fetcher.start();