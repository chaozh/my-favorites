#!/usr/bin/env python
#-*- coding:utf-8 -*-

import zhihu
import os, sys, logging
from ConfigParser import ConfigParser
from pymongo import MongoClient

logger = logging.getLogger()

class MongoStore:
    def __init__(self, dbname='zhihu_spider'):
        ip, port = read_from_config_file()
        self.client = MongoClient(ip, port)
        self.db = client[dbname]

    def read_from_config_file(self, config_file="config.ini"):
            cf = ConfigParser()
            if os.path.exists(config_file) and os.path.isfile(config_file):
                cf.read(config_file)

                ip = cf.get("mongo", "ip")
                port = cf.get("mongo", "port")
                if ip == "" or port == "":
                    logger.warn(u"帐号信息无效")
                    return (None, None)
                else:
                    return (ip, port)
            else:
                logger.error(u"配置文件加载失败！")
                return (None, None)

    def store_user_collections(name):
        # could try multi-thread
        user = zhihu.User('https://www.zhihu.com/people/' + uname + '/')
        for collection in user.get_collections():
            col_set = db[collection.id] # chinese
            
            for answer in collection.get_all_answers():
                author = answer.get_author()
                # also deal with post
                if isinstance(answer, zhihu.Answer):
                    # http://www.zhihu.com/question/40044307/answer/139159233
                    question = answer.get_question()
                    # check if exists
                    if col_set.find_one({"q_title": question.get_title()}):
                        continue

                    ans_obj = { 
                        "col_name": collection.get_name(),
                        "a_type": "answer",
                        "q_title":  question.get_title(), 
                        "q_answers_num": question.get_answers_num(),
                        "q_followers_num": question.get_followers_num(),
                        "q_topics": question.get_topics(),
                        "a_author": author.get_user_id(),
                        "a_upvote": answer.get_upvote(),
                        "a_content": str(answer.get_content())
                    }
                else:
                    column = answer.get_column()
                    # check if exists
                    if col_set.find_one({"q_title": answer.get_title()}):
                        continue

                    if column != None:
                        q_topics = column.get_topics()
                        q_followers_num = column.get_followers_num()
                    else:
                        q_followers_num = 0
                        q_topics = []

                    ans_obj = { 
                        "col_name": collection.get_name(),
                        "a_type": "post",
                        "q_title":  answer.get_title(),
                        "q_followers_num": q_followers_num,
                        "q_topics": q_topics,
                        "a_author": author.get_user_id(),
                        "a_upvote": answer.get_likes(),
                        "a_content": answer.get_content()
                    }
                
                col_set.save(ans_obj)

def main():
    mstore = MongoStore('zhihu_zheng-chuan-jun')
    mstore.store_user_collections('zheng-chuan-jun')

if __name__=='__main__':
    main()
