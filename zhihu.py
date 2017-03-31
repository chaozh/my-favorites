#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib
import os, re, random, platform, logging
from time import sleep
# module
# from auth import Auth
# requirements
import requests
from bs4 import BeautifulSoup

# Setting Logging
logger = logging.getLogger()

headers = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    'Host': "www.zhihu.com",
    'Origin': "http://www.zhihu.com",
    'Pragma': "no-cache",
    'Referer': "http://www.zhihu.com/"
}

class Zhihu:
    def __init__(self):
        self.auth = ZhihuAuth()
        self.requests = self.auth.get_requests()

    def login(self):
        self.auth.login()
        if self.auth.islogin() != True:
            logger.error(u"你的身份信息已经失效，请重新生成身份信息( `python auth.py` )。")
            raise Exception("无权限(403)")
    
    def get_requests(self):
        return self.requests

    def get_auth(self):
        return self.auth

class Base:
    def saveImg(self,imageURL,fileName):
        u = urllib.urlopen(imageURL)
        data = u.read()
        f = open(fileName, 'wb')
        f.write(data)
        f.close()

class User:
    user_url = None
    # session = None
    soup = None

    def __init__(self, user_url, user_id=None):
        if user_url == None:
            self.user_id = "匿名用户"
        elif user_url.startswith('www.zhihu.com/people', user_url.index('//') + 2) == False \
        and user_url.startswith('www.zhihu.com/org', user_url.index('//') + 2) == False:
            raise ValueError("\"" + user_url + "\"" + " : it isn't a user url.")
        else:
            self.user_url = user_url
            if user_id != None:
                self.user_id = user_id

    def parser(self):
        r = requests.get(self.user_url, headers=headers, verify=False)
        soup = BeautifulSoup(r.content, "lxml")
        self.soup = soup

    def get_user_id(self):
        if self.user_url == None:
            # print "I'm anonymous user."
            if platform.system() == 'Windows':
                return "匿名用户".decode('utf-8').encode('gbk')
            else:
                return "匿名用户"
        else:
            if hasattr(self, "user_id"):
                if platform.system() == 'Windows':
                    return self.user_id.decode('utf-8').encode('gbk')
                else:
                    return self.user_id
            else:
                if self.soup == None:
                    self.parser()
                soup = self.soup
                user_id = soup.find("div", class_="title-section ellipsis") \
                    .find("span", class_="name").string.encode("utf-8")
                self.user_id = user_id
                if platform.system() == 'Windows':
                    return user_id.decode('utf-8').encode('gbk')
                else:
                    return user_id

    def get_head_img_url(self, scale=4):
        """
            By liuwons (https://github.com/liuwons)
            增加获取知乎识用户的头像url
            scale对应的头像尺寸:
                1 - 25×25
                3 - 75×75
                4 - 100×100
                6 - 150×150
                10 - 250×250
        """
        scale_list = [1, 3, 4, 6, 10]
        scale_name = '0s0ml0t000b'
        if self.user_url == None:
            print "I'm anonymous user."
            return None
        else:
            if scale not in scale_list:
                print 'Illegal scale.'
                return None
            if self.soup == None:
                self.parser()
            soup = self.soup
            url = soup.find("img", class_="Avatar Avatar--l")["src"]
            return url[:-5] + scale_name[scale] + url[-4:]

    def get_data_id(self):
        """
            By yannisxu (https://github.com/yannisxu)
            增加获取知乎 data-id 的方法来确定标识用户的唯一性 #24
            (https://github.com/egrcc/zhihu-python/pull/24)
        """
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            data_id = soup.find("button", class_="zg-btn zg-btn-follow zm-rich-follow-btn")['data-id']
            return data_id

    def get_gender(self):
        """
            By Mukosame (https://github.com/mukosame)
            增加获取知乎识用户的性别
        """
        if self.user_url == None:
            print "I'm anonymous user."
            return 'unknown'
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            try:
                gender = str(soup.find("span",class_="item gender").i)
                if (gender == '<i class="icon icon-profile-female"></i>'):
                    return 'female'
                else:
                    return 'male'
            except:
                return 'unknown'

    def get_collections_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            # print soup.find_all("span", class_="Tabs-meta")
            collections_num = int(soup.find_all("span", class_="Tabs-meta")[3].string)
            return collections_num

    def get_collections(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            collections_num = self.get_collections_num()
            if collections_num == 0:
                return
                yield
            else:
                for i in xrange((collections_num - 1) / 20 + 1):
                    collection_url = self.user_url + "collections?page=" + str(i + 1)
                    r = requests.get(collection_url, headers=headers, verify=False)
                    
                    soup = BeautifulSoup(r.content, "lxml")
                    for collection in soup.find_all("div", class_="FavlistItem-title"):
                        url = "http://www.zhihu.com" + \
                              collection.find("a")["href"]
                        name = collection.find("a").string.encode("utf-8")
                        yield Collection(url, requests, name, self)

class Collection:
    soup = None

    def __init__(self, url, requests, name=None, creator=None):
        self.requests = requests

        if not re.compile(r"(http|https)://www.zhihu.com/collection/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a collection url.")
        else:
            self.url = url
            print 'collection url',url
            if name != None:
                self.name = name
            if creator != None:
                self.creator = creator
        
    def parser(self):
        r = self.requests.get(self.url, headers=headers, verify=False)
        soup = BeautifulSoup(r.content, "lxml")
        self.soup = soup

    def get_name(self):
        if hasattr(self, 'name'):
            if platform.system() == 'Windows':
                return self.name.decode('utf-8').encode('gbk')
            else:
                return self.name
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            self.name = soup.find("h2", id="zh-fav-head-title").string.encode("utf-8").strip()
            if platform.system() == 'Windows':
                return self.name.decode('utf-8').encode('gbk')
            return self.name

    def get_creator(self):
        if hasattr(self, 'creator'):
            return self.creator
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            creator_id = soup.find("h2", class_="zm-list-content-title").a.string.encode("utf-8")
            creator_url = "http://www.zhihu.com" + soup.find("h2", class_="zm-list-content-title").a["href"]
            creator = User(creator_url, creator_id)
            self.creator = creator
            return creator

    def get_answers(self, pageNo):
        if pageNo == 1:
            if self.soup == None:
                self.parser()
            soup = self.soup
        else:
            r = self.requests.get(self.url + "?page=" + str(pageNo), headers=headers, verify=False)
            soup = BeautifulSoup(r.content, "lxml")
            
        answer_list = soup.find_all("div", class_="zm-item")

        if len(answer_list) == 0:
            return
            yield
        else:
            for answer in answer_list:
                
                if not answer.find("p", class_="note"):
                    # judge if answer or post by data-type
                    if answer['data-type'] == 'Answer':
                        question_link = answer.find("h2")
                        if question_link != None:
                            question_url = "http://www.zhihu.com" + question_link.a["href"]
                            question_title = question_link.a.string.encode("utf-8")
                        question = Question(question_url, self.requests, question_title)

                        answer_url = "http://www.zhihu.com" + answer.find("div", class_="zm-item-answer").link[
                            "href"]
                        print answer_url

                        author = None
                        yield Answer(answer_url, self.requests, author, question)
                    
                    elif answer['data-type'] == 'Post':
                        post_link = answer.find("h2")
                        if post_link != None:
                            post_url = post_link.a["href"]

                            print post_url
                            yield Post(post_url)

    def get_all_answers(self):
        i = 1
        # deal with yield
        while True:
            if i == 1:
                if self.soup == None:
                    self.parser()
                soup = self.soup
            else:
                r = self.requests.get(self.url + "?page=" + str(i), headers=headers, verify=False)
                soup = BeautifulSoup(r.content, "lxml")
                
            answer_list = soup.find_all("div", class_="zm-item")

            if len(answer_list) == 0:
                return
                yield
            else:
                for answer in answer_list:
                    if not answer.find("p", class_="note"):
                        # judge if answer or post by data-type
                        if answer['data-type'] == 'Answer':
                            question_link = answer.find("h2")
                            if question_link != None:
                                question_url = "http://www.zhihu.com" + question_link.a["href"]
                                question_title = question_link.a.string[:-1].encode("utf-8")
                            
                            question = Question(question_url, self.requests, question_title)
                            answer_url = "http://www.zhihu.com" + answer.find("div", class_="zm-item-answer").link[
                                "href"]

                            print answer_url

                            author = None
                            yield Answer(answer_url, self.requests, author, question)
                        
                        elif answer['data-type'] == 'Post':
                            post_link = answer.find("h2")
                            if post_link != None:
                                post_url = post_link.a["href"]

                                print post_url
                                yield Post(post_url)
            i = i + 1

class Post:
    url = None
    meta = None
    slug = None

    def __init__(self, url):

        if not re.compile(r"(http|https)://zhuanlan.zhihu.com/p/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
        else:
            self.url = url
            self.slug = re.compile(r"(http|https)://zhuanlan.zhihu.com/p/(\d{8})").match(url).group(2)

    def parser(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "zhuanlan.zhihu.com",
            'Accept': "application/json, text/plain, */*"
        }
        r = requests.get('https://zhuanlan.zhihu.com/api/posts/' + self.slug, headers=headers, verify=False)
        print 'https://zhuanlan.zhihu.com/api/posts/' + self.slug
        self.meta = r.json()

    def get_title(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        title = meta['title']
        self.title = title
        if platform.system() == 'Windows':
            # FIXME
            title = self.title.encode('gbk')
            return title
        else:
            return title

    def get_content(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        content = meta['content']
        if platform.system() == 'Windows':
            content = content.encode('utf-8')
            return content
        else:
            return content
    
    def get_author(self):
        if hasattr(self, "author"):
            return self.author
        else:
            if self.meta == None:
                self.parser()
            meta = self.meta
            author_tag = meta['author']

            if platform.system() == 'Windows':
                author_id = author_tag['name'].encode('utf-8')
            else:
                author_id = author_tag['name']

            author = User(author_tag['profileUrl'], author_id)
            return author

    def get_column(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        column_url = 'https://zhuanlan.zhihu.com/' + meta['column']['slug']
        return Column(column_url, meta['column']['slug'])

    def get_likes(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        return int(meta["likesCount"])

    def get_topics(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        topic_list = []
        for topic in meta['topics']:
            topic_list.append(topic['name'])
        return topic_list

    def to_json(self):
        f = open(self.get_title() + ".json", "wt")
        f.write(self.meta)
        f.close()

    def to_html(self, path=None):
        content = self.get_content()
        if self.get_author().get_user_id() == "匿名用户":
            file_name = self.get_title() + ".html"
        else:
            file_name = self.get_title() + "--" + self.get_author().get_user_id() + ".html"
            #file_name = self.get_author().get_user_id() + ".html"
        #print file_name
        if path != None: file_name = path + '/' + file_name.replace('/','／').replace('\\','＼')
        f = open(file_name, "wt")
        f.write(content)
        f.close()

    def saveImg(self,imageURL,fileName):
        u = urllib.urlopen(imageURL)
        data = u.read()
        f = open(fileName, 'wb')
        f.write(data)
        f.close()
      
class Column:
    url = None
    meta = None

    def __init__(self, url, slug=None):

        if not re.compile(r"(http|https)://zhuanlan.zhihu.com/([0-9a-zA-Z]+)").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
        else:
            self.url = url
            if slug == None:
                self.slug = re.compile(r"(http|https)://zhuanlan.zhihu.com/([0-9a-zA-Z]+)").match(url).group(2)
            else:
                self.slug = slug

    def parser(self):
        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "zhuanlan.zhihu.com",
            'Accept': "application/json, text/plain, */*"
        }
        r = requests.get('https://zhuanlan.zhihu.com/api/columns/' + self.slug, headers=headers, verify=False)
        self.meta = r.json()

    def get_title(self):
        if hasattr(self,"title"):
            if platform.system() == 'Windows':
                title =  self.title #.decode('utf-8').encode('gbk')
                return title
            else:
                return self.title
        else:
            if self.meta == None:
                self.parser()
            meta = self.meta
            title = meta['name']
            self.title = title
            if platform.system() == 'Windows':
                # title = title.decode('utf-8').encode('gbk')
                return title
            else:
                return title

    def get_description(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        description = meta['description']
        if platform.system() == 'Windows':
            description = description.decode('utf-8').encode('gbk')
            return description
        else:
            return description

    def get_followers_num(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        followers_num = int(meta['followersCount'])
        return followers_num

    def get_posts_num(self):
        if self.meta == None:
            self.parser()
        meta = self.meta
        posts_num = int(meta['postsCount'])
        return posts_num

    def get_creator(self):
        if hasattr(self, "creator"):
            return self.creator
        else:
            if self.meta == None:
                self.parser()
            meta = self.meta
            creator_tag = meta['creator']
            creator = User(creator_tag['profileUrl'],creator_tag['slug'])
            return creator

    def get_all_posts(self):
        posts_num = self.get_posts_num()
        if posts_num == 0:
            print "No posts."
            return
            yield
        else:
            for i in xrange((posts_num - 1) / 20 + 1):
                parm = {'limit': 20, 'offset': 20*i}
                url = 'https://zhuanlan.zhihu.com/api/columns/' + self.slug + '/posts'
                r = requests.get(url, params=parm, headers=headers, verify=False)
                posts_list = r.json()
                for p in posts_list:
                    post_url = 'https://zhuanlan.zhihu.com/p/' + str(p['slug'])
                    yield Post(post_url)


class Question:
    soup = None

    def __init__(self, url, requests, title=None):
        self.requests = requests

        if not re.compile(r"(http|https)://www.zhihu.com/question/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a question url.")
        else:
            self.url = url

        if title != None: self.title = title

    def parser(self):
        r = self.requests.get(self.url,headers=headers, verify=False)
        self.soup = BeautifulSoup(r.content, "lxml")

    def get_title(self):
        if hasattr(self, "title"):
            if platform.system() == 'Windows':
                title = self.title.decode('utf-8').encode('gbk')
                return title
            else:
                return self.title
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            title = soup.find("h2", class_="zm-item-title").string.encode("utf-8").replace("\n", "")
            self.title = title
            if platform.system() == 'Windows':
                title = title.decode('utf-8').encode('gbk')
                return title
            else:
                return title

    def get_detail(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        detail = soup.find("div", id="zh-question-detail").div.get_text().encode("utf-8")
        if platform.system() == 'Windows':
            detail = detail.decode('utf-8').encode('gbk')
            return detail
        else:
            return detail

    def get_answers_num(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        answers_num = 0
        if soup.find("h3", id="zh-question-answer-num") != None:
            answers_num = int(soup.find("h3", id="zh-question-answer-num")["data-num"])
        return answers_num

    def get_followers_num(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        followers_num = int(soup.find("div", class_="zg-gray-normal").a.strong.string)
        return followers_num

    def get_topics(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        topic_list = soup.find_all("a", class_="zm-item-tag")
        topics = []
        for i in topic_list:
            topic = i.contents[0].encode("utf-8").replace("\n", "")
            if platform.system() == 'Windows':
                topic = topic.decode('utf-8').encode('gbk')
            topics.append(topic)
        return topics

    def get_visit_times(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        return int(soup.find("meta", itemprop="visitsCount")["content"])

class Answer:
    soup = None

    def __init__(self, answer_url, requests, author=None, question=None, upvote=None, content=None):
        self.answer_url = answer_url
        self.requests = requests

        if author != None:
            self.author = author
        if question != None:
            self.question = question
        if upvote != None:
            self.upvote = upvote
        if content != None:
            self.content = content

    def parser(self):
        r = self.requests.get(self.answer_url, headers=headers, verify=False)
        soup = BeautifulSoup(r.content, "lxml")
        self.soup = soup

    def get_question(self):
        if hasattr(self, "question"):
            return self.question
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            question_link = soup.find("h2", class_="zm-item-title zm-editable-content").a
            url = "http://www.zhihu.com" + question_link["href"]
            title = question_link.string.encode("utf-8")
            question = Question(url, self.requests, title)
            return question

    def get_author(self):
        if hasattr(self, "author"):
            return self.author
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            author = None
            # @TODO: new style changes here
            # author_tag = soup.find("div", class_="zm-item-answer-author-info") or soup.find("div", class_="AuthorInfo")
            # issue: some items cant find author-link esp in windows ???
            author_tag = soup.find("a", class_="author-link") or soup.find("div", class_="AuthorInfo-name").find("a", class_="UserLink-link")
            if author_tag != None:
                if author_tag.get_text(strip='\n') == u"匿名用户":
                    author_url = None
                    author = User(author_url)
                else:
                    author_id = author_tag.string.encode("utf-8")
                    author_url = "http://www.zhihu.com" + author_tag["href"]
                    author = User(author_url, author_id)
            
            return author

    def get_upvote(self):
        if hasattr(self, "upvote"):
            return self.upvote
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            count = soup.find("span", class_="count").string
            if count[-1] == "K":
                upvote = int(count[0:(len(count) - 1)]) * 1000
            elif count[-1] == "W":
                upvote = int(count[0:(len(count) - 1)]) * 10000
            else:
                upvote = int(count)
            return upvote

    def get_content(self):
        if hasattr(self, "content"):
            return self.content
        else:
            if self.soup == None:
                self.parser()
            
            soup = BeautifulSoup(self.soup.encode("utf-8"), "lxml")
            # @TODO: new style changes here
            answer = soup.find("div", class_="zm-editable-content clearfix") or soup.find("div", class_="RichContent-inner")
            # logger.debug(answer)

            soup.body.extract()
            soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
            soup.body.append(answer)
            img_list = soup.find_all("img", class_="content_image lazy")
            for img in img_list:
                img["src"] = img["data-actualsrc"]
            img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
            for img in img_list:
                img["src"] = img["data-actualsrc"]
            noscript_list = soup.find_all("noscript")
            for noscript in noscript_list:
                noscript.extract()
            content = soup
            self.content = content
            return content

    def saveImg(self,imageURL,fileName):
        u = urllib.urlopen(imageURL)
        data = u.read()
        f = open(fileName, 'wb')
        f.write(data)
        f.close()

    def to_html(self, path=None):
        content = self.get_content()
        if self.get_author().get_user_id() == "匿名用户":
            file_name = self.get_question().get_title() + ".html"
        else:
            file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + ".html"
            #file_name = self.get_author().get_user_id() + ".html"
        #print file_name
        if path != None: file_name = path + '/' + file_name.replace('/','／').replace('\\','＼')
        f = open(file_name, "wt")
        f.write(str(content))
        f.close()

    def to_txt(self):

        content = self.get_content()
        body = content.find("body")
        br_list = body.find_all("br")
        for br in br_list:
            br.insert_after(content.new_string("\n"))
        li_list = body.find_all("li")
        for li in li_list:
            li.insert_before(content.new_string("\n"))

        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "text"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write("\n\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write(self.get_question().get_title() + "\n\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "wt")
            f.write(self.get_question().get_title() + "\n\n")
        if platform.system() == 'Windows':
            f.write("作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8').encode('gbk') + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("gbk"))
            link_str = "原链接: ".decode('utf-8').encode('gbk')
            f.write("\n" + link_str + self.answer_url.decode('utf-8').encode('gbk'))
        else:
            f.write("作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("utf-8"))
            f.write("\n" + "原链接: " + self.answer_url)
        f.close()

    def to_md(self):
        content = self.get_content()
        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("# " + self.get_question().get_title() + "\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "wt")
            f.write("# " + self.get_question().get_title() + "\n")
        if platform.system() == 'Windows':
            f.write("### 作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8').encode('gbk') + str(self.get_upvote()) + "\n")
        else:
            f.write("### 作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n")
        text = html2text.html2text(content.decode('utf-8')).encode("utf-8")

        r = re.findall(r'\*\*(.*?)\*\*', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'_(.*)_', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'!\[\]\((?:.*?)\)', text)
        for i in r:
            text = text.replace(i, i + "\n\n")

        if platform.system() == 'Windows':
            f.write(text.decode('utf-8').encode('gbk'))
            link_str = "\n---\n#### 原链接: ".decode('utf-8').encode('gbk')
            f.write(link_str + self.answer_url.decode('utf-8').encode('gbk'))
        else:
            f.write(text)
            f.write("\n---\n#### 原链接: " + self.answer_url)
        f.close()

    def get_visit_times(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        for tag_p in soup.find_all("p"):
            if "所属问题被浏览" in tag_p.contents[0].encode('utf-8'):
                return int(tag_p.contents[1].contents[0])

    def get_voters(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        data_aid = soup.find("div", class_="zm-item-answer  zm-item-expanded")["data-aid"]
        request_url = 'http://www.zhihu.com/node/AnswerFullVoteInfoV2'
        # if session == None:
        #     create_session()
        # s = session
        # r = s.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)})
        r = requests.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)}, headers=headers, verify=False)
        soup = BeautifulSoup(r.content, "lxml")
        voters_info = soup.find_all("span")[1:-1]
        if len(voters_info) == 0:
            return
            yield
        else:
            for voter_info in voters_info:
                if voter_info.string == u"匿名用户、" or voter_info.string == u"匿名用户":
                    voter_url = None
                    yield User(voter_url)
                else:
                    voter_url = "http://www.zhihu.com" + str(voter_info.a["href"])
                    voter_id = voter_info.a["title"].encode("utf-8")
                    yield User(voter_url, voter_id)


def main():
    user = User('https://www.zhihu.com/people/zheng-chuan-jun/')
    #a = Answer('https://www.zhihu.com/question/47883186/answer/151846965', requests)
    #a.to_html()
    for collection in user.get_collections():
        # make collection dir
        path = collection.get_name()
        if not os.path.exists(path):
            os.mkdir(path)

        for answer in collection.get_all_answers():
            answer.to_html(path)
    
if __name__=='__main__':
    main()
