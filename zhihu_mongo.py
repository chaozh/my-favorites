#!/usr/bin/env python
#-*- coding:utf-8 -*-

import zhihu
from pymongo import MongoClient

import logging

logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)

def main():
    # mongo client
    uname = 'zheng-chuan-jun'
    ip = '192.168.31.131'
    port = 27017
    client = MongoClient(ip, port)
    db_name = 'zhihu_' + uname
    db = client[db_name]
    # could try multi-thread
    user = zhihu.User('https://www.zhihu.com/people/' + uname + '/')
    for collection in user.get_collections():
        col_set = db[collection.id] # chinese
        
        for answer in collection.get_all_answers():
            author = answer.get_author()
            # also deal with post
            if isinstance(answer, zhihu.Answer):
                question = answer.get_question()
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

    # collection = Collection('https://www.zhihu.com/collection/40878489', requests)


if __name__=='__main__':
    main()