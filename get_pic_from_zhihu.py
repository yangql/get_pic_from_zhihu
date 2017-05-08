#!/usr/bin/env python
#-*- coding:utf-8 -*-
import re
import requests
import os
from urlparse import urlsplit
from os.path import basename

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    'Accept-Encoding': 'gzip, deflate'}


def mkdir(path):
    if not os.path.exists(path):
        print '新建文件夹:', path
        os.makedirs(path)
        return True
    else:
        print u"图片存放于:", os.getcwd() + os.sep + path
        return False


def download_pic(img_lists, dir_name):
    print "一共有 {num} 张照片".format(num=len(img_lists))
    for image_url in img_lists:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image = response.content
        else:
            continue
        file_name = dir_name + os.sep + basename(urlsplit(image_url)[2])
        try:
            with open(file_name, "wb") as picture:
                picture.write(image)
        except IOError:
            print("IO Error\n")
            continue
        finally:
            picture.close
            print "下载 {pic_name} 完成!".format(pic_name=file_name)


def get_image_url(qid, headers):
    # 利用正则表达式把源代码中的图片地址过滤出来
    #reg = r'data-actualsrc="(.*?)">'
    tmp_url = "https://www.zhihu.com/node/QuestionAnswerListV2"
    size = 10
    image_urls = []
    session = requests.Session()
    while True:
        postdata = {'method': 'next', 'params': '{"url_token":' +
                    str(qid) + ',"pagesize": "10",' + '"offset":' + str(size) + "}"}
        page = session.post(tmp_url, headers=headers, data=postdata)
        ret = eval(page.text)
        answers = ret['msg']
        print u"答案数 : %d " % (len(answers))
        size += 10
        if not answers:
            print "图片URL获取完毕, 页数: ", (size - 10) / 10
            return image_urls
        #reg = r'https://pic\d.zhimg.com/[a-fA-F0-9]{5,32}_\w+.jpg'
        imgreg = re.compile('data-original="(.*?)"', re.S)
        for answer in answers:
            tmp_list = []
            url_items = re.findall(imgreg, answer)
            for item in url_items:  # 这里去掉得到的图片URL中的转义字符'\\'
                image_url = item.replace("\\", "")
                tmp_list.append(image_url)
            # 清理掉头像和去重 获取data-original的内容
            tmp_list = list(set(tmp_list))  # 去重
            for item in tmp_list:
                if item.endswith('r.jpg'):
                    print item
                    image_urls.append(item)
        print 'size: %d, num : %d' % (size, len(image_urls))


if __name__ == '__main__':
    question_id = 26037846
    zhihu_url = "https://www.zhihu.com/question/{qid}".format(qid=question_id)
    path = 'zhihu_pic'
    mkdir(path)  # 创建本地文件夹
    img_list = get_image_url(question_id, headers)  # 获取图片的地址列表
    download_pic(img_list, path)  # 保存图片
