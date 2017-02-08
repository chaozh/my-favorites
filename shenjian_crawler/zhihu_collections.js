var configs = {
    domains: ["bbs.tianya.cn"],
    scanUrls: ["http://bbs.tianya.cn/hotArticle.jsp"],
    contentUrlRegexes: [], // 该项为空，表示所有待爬队列里的网页都会被当作内容页处理
    helperUrlRegexes: [/http:\/\/bbs\.tianya\.cn\/hotArticle\.jsp(\?pn=\d+)?/],
    fields: [
      {
        name: "items", // items是一个对象数组，数组里的每一项是抽取的一条数据（包括标题、作者和回复时间）
        selector: "//table[contains(@class,'tab-bbs-list')]/tbody/tr",
        repeated: true, // repeated设置为true表示该项是数组
        children: [ // 数组里每个对象包含的子项
          {
              name: "title",
              alias: "标题",
              selector: "//td[contains(@class,'td-title')]//text()",// 相对于父项的路径，xpath必须以//开头
              required: true 
          },
          {
              name: "author",
              alias: "作者",
              selector: "//a[contains(@class,'author')]/text()"
          },
          {
              name:"replied_time",
              alias: "回复时间",
              selector:"//td[last()]"
          }
        ]
      }       
    ]
};

/*
  回调函数onProcessHelperUrl：获取下一页列表页url，并手动添加到待爬队列中
*/
configs.onProcessHelperUrl = function(url, content, site) {
    // 从当前列表页中获取下一页的链接
    var nextUrl = extract(content, "//a[text()[1]='下页']/@href");
    if(nextUrl==="" || nextUrl===null){
      return false; //  如果是最后一页就不发现新链接了
    }
    site.addUrl(nextUrl);
    return false; 
};

/*
  回调函数afterExtractField：对抽取的数据进行处理
*/
configs.afterExtractField = function(fieldName, data, page){
    if(data===null || data==="" || typeof(data)=="undefined"){
      return data;
    }
    if(fieldName=="items.replied_time"){ // 子项的fieldName前面要加上： 父项的fieldName.
      var timestamp = parseDateTime(data); // 回复时间转换成时间戳，parseDateTime可以处理非标准的时间格式，比如：3天前、一个月前等
      return isNaN(timestamp) ? "0" : timestamp/1000 + ""; // 使用神箭手进行数据发布时，默认处理的时间戳是10位。如非特殊，请转换成10位时间戳
    }
    return data;
};

var crawler = new Crawler(configs);
crawler.start();

var configs = {
    domains: ["news.87870.com"],
    scanUrls: ["http://news.87870.com/ajax/ashx/news/2016NewsList.ashx?action=newslist&cid=01&sort=1&pageindex=1&pagesize=8"],
    contentUrlRegexes: [/http:\/\/news\.87870\.com\/xinwennr-\d+\.html/],
    helperUrlRegexes: [/http:\/\/news\.87870\.com\/ajax\/ashx\/news\/2016NewsList\.ashx\?action=newslist&cid=01&sort=1&pageindex=\d+&pagesize=8/],
    fields: [
        {
            name: "article_title",
            alias: "文章标题",
            selector: "//div[contains(@class,'info_wrap')]/h1",
            required: true
        },
        {
            name: "article_summary",
            alias: "文章导读",
            selector: "//div[contains(@class,'info_guide')]"
        },
        {
            name: "article_content",
            alias: "文章正文",
            selector: "//div[contains(@class,'content')]"
        },
        {
            name: "article_publish_time",
            alias: "发布日期",
            selector: "//div[contains(@class,'infofabudate')]/text()[1]"
        },
        {
            name: "article_author",
            alias: "作者",
            selector: "//span[contains(text()[1],'作者')]/em/a/text()"
        },
        {
            name: "article_tags",
            alias: "标签",
            // 3、从之前添加到内容页中的附加数据中抽取文章标签
            sourceType: SourceType.UrlContext, // 将来源设置为UrlContext
            selector: "//div[@id='sjs-tags']"
        }
    ]
};

configs.onProcessScanPage = function(page, content, site){
    return false;
};

configs.onProcessHelperPage = function(page, content, site){
    var matches = /pageindex=(\d+)/.exec(page.url);
    if(!matches){
      return false;
    }
    var json = JSON.parse(content);
    var list = json.list;
    if(list===null || list==="" || typeof(list)=="undefined"){
      return false;
    }
    for(var i=0;i<list.length;i++){
      // 1、获取列表页中每篇文章的tags数据
      var tags = list[i].tags;
      var commonID = list[i].commonID;
      var options = {
        method: "GET",
        contextData: '<div id="sjs-tags">'+tags+'</div>' // 将tags数据添加到options的contextData中
      };
      // 2、将options附加到内容页中，再将内容页链接添加到待爬队列中
      site.addUrl("http://news.87870.com/xinwennr-"+commonID+".html", options);
    }
  
    var nextPage = parseInt(matches[1])+1;
    site.addUrl("http://news.87870.com/ajax/ashx/news/2016NewsList.ashx?action=newslist&cid=01&sort=1&pageindex="+nextPage+"&pagesize=8");
    return false;
};

configs.onProcessContentPage = function(page, content, site){
    return false;
};

configs.afterExtractField = function(fieldName, data, page) {
    if(data===null || data==="" || typeof(data)=="undefined"){
      if(fieldName=="article_author"){
        data = extract(page.raw, "//font[contains(@class,'fabuuser')]"); // 如果没有作者，就抽取发布者作为文章作者
      }
      return data;
    }
    if (fieldName == "article_publish_time") {
      var timestamp = parseDateTime(data.trim());
      return isNaN(timestamp) ? "0" : timestamp/1000 + "";
    }else if(fieldName == "article_summary"){
      return exclude(data, "//span[contains(@class,'tag')]"); // 从抽取的导读内容中去掉不需要的部分数据
    } 
    return data;
};

var crawler = new Crawler(configs);
crawler.start();