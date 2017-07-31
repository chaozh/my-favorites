#!/usr/bin/env python
#-*- coding:utf-8 -*-

from zhihu import User
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
    user = User('https://www.zhihu.com/people/' + uname + '/')
    for collection in user.get_collections():
        col_set = db[collection.id] # chinese
        
        for answer in collection.get_all_answers():
            # also deal with post
            question = answer.get_question()
            author = answer.get_author()

            ans_obj = { 
                "col_name": collection.get_name(), 
                "q_title":  question.get_title(), 
                "q_answers_num": question.get_answers_num(),
                "q_followers_num": question.get_followers_num(),
                "a_author": author.get_user_id(),
                "a_upvote": answer.get_upvote(),
                "a_content": str(answer.get_content())
            }
            col_set.save(ans_obj)

    # collection = Collection('https://www.zhihu.com/collection/40878489', requests)


if __name__=='__main__':
    main()