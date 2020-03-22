#!/usr/bin/python
# coding=utf-8
import re
import requests
import pandas as pd
import time
import random
from lxml import etree
from requests import exceptions


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_source_page(url):
    '''
    使用 Session 能够跨请求保持某些参数。
    它也会在同一个 Session 实例发出的所有请求之间保持 cookie
    '''
    timeout = 5

    UserAgent_List = [
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
    ]

    header = {
        'User-agent': random.choice(UserAgent_List),
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/subject/24773958/?from=showing',
    }

    ############ 本地免费代理服务器 start
    proxypool_url = 'http://localhost:5000/random'
    proxy = requests.get(proxypool_url).text.strip()
    proxies = {'http': 'http://' + proxy}
    # ############ 本地免费代理服务器 end


    # ############ 付费代理服务器 start
    # proxyHost = "http-dyn.abuyun.com"
    # proxyPort = "9020"
    # # 代理隧道验证信息
    # proxyUser = "H4X81482X044H26D"
    # proxyPass = "2B38E7AF47CE2838"
    # proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    #     "host": proxyHost,
    #     "port": proxyPort,
    #     "user": proxyUser,
    #     "pass": proxyPass,
    # }
    # proxies = {
    #     "http": proxyMeta,
    #     "https": proxyMeta,
    # }
    ############ 付费代理服务器 end

    session = requests.Session()

    cookie = {
        'cookie': "你的 cookie 值",
    }

    # time.sleep(random.randint(5, 15))
    # response = requests.get(url, headers=header, proxies=proxies, cookies=cookie_nologin, timeout=timeout)
    try:
        response = requests.get(url, headers=header, proxies=proxies, timeout=timeout)
    except exceptions.Timeout as e:
        print('请求超时, 正在跳过...', e)
        response = None
    except exceptions.ProxyError as e:
        print('代理错误, 正在更换代理...', e)
        response = None
    return response


def get_hot_movies_id(movie_sum, movie_tag):
    """
    获取影片名和影片ID
    :param movie_sum: 指定爬取电影的数量，范围 1~500
    :param movie_tag: 指定电影排行tag， 范围 '热门' or '豆瓣高分'
    :return:
    """
    movie_tags = {'热门': '%E7%83%AD%E9%97%A8', '豆瓣高分': '%E8%B1%86%E7%93%A3%E9%AB%98%E5%88%86'}
    tag = movie_tags[movie_tag]
    hot_page_url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=' + tag + '&sort=recommend' \
                    '&page_limit=' + str(movie_sum) + '&page_start=0'
    try:
        response = get_source_page(hot_page_url).json()['subjects']  # type: list
    except Exception as e:
        print(get_current_time() + '===========>> 正在重试...')
        response = get_source_page(hot_page_url).json()['subjects']  # type: list
    host_movies_id_and_title = {}
    for each_movie in response:
        host_movies_id_and_title[each_movie['id']] = each_movie['title']
    # print(host_movies_id_and_title)
    print('====================>> Start time: ' + get_current_time() + ' <<====================')
    print('========================>> 共' + str(movie_sum) + ' 部影片 <<========================')
    # for mid, mtitle in host_movies_id_and_title.items():
    #     print(mid + ' --> ' + mtitle)
    return host_movies_id_and_title


def start_spider_movies_info(movies_id_and_title_dict):
    """
    指定需要爬取的影片
    :param movies_id_and_title_dict:
    :return:
    """

    all_movie_urls = ['https://movie.douban.com/subject/{}'.format(k) for k, v in movies_id_and_title_dict.items()]
    movies_all = []
    sum = 1
    for each_page in all_movie_urls:
        movie_id = each_page.split('/')[-1]
        print(get_current_time() + ' ----->> 正在爬取第 ' + str(sum) + '部影片( ' + movies_id_and_title_dict[movie_id] + ' )')
        sum += 1
        try:
            html = get_source_page(each_page)
            selector = etree.HTML(html.text)
            movies_all.append(get_movie_info(selector))
        except Exception as e:
            print(get_current_time() + "------> 爬取失败, 正在跳过...")
            continue
    data = pd.DataFrame(movies_all)
    filename = 'movie_info_top500.csv'
    number = 1
    if number == 1:
        info_headers = ['名称', '年份', '导演', '演员', '类型', '国别', '语言', '评分', '评分人数', '五星占比', '四星占比', '三星占比',
                        '二星占比', '一星占比', '短评数', '简介']
        data.to_csv(filename, header=info_headers, index=False, mode='a+', encoding="utf-8")
        number += 1
    else:
        data.to_csv(filename, header=False, index=False, mode='a+', encoding="utf-8")

    data = []
    print('====================>> Finsh time: ' + get_current_time() + ' <<====================')


def start_spider_comment(movies_id_and_title_dict):
    """
    指定需要爬取影评的影片
    :param movies_id_and_title_dict:
    :return:
    """
    number = 1
    for movie_id, movie_name in movies_id_and_title_dict.items():
        print(get_current_time() + ' ----->> 正在爬取第 ' + str(number) + '部影片( ' + movie_name + ' )')
        get_comment_info_to_cvs(movie_id, movie_name)
        # get_comment_info_to_txt(movie_id, movie_name)
        number += 1
    print('====================>> Finsh time: ' + get_current_time() + ' <<====================')


def get_comments(eachComment):
    commentlist = []
    user = eachComment.xpath("./h3/span[@class='comment-info']/a/text()")[0]  # 用户
    watched = eachComment.xpath("./h3/span[@class='comment-info']/span[1]/text()")[0]  # 是否看过
    rating = eachComment.xpath("./h3/span[@class='comment-info']/span[2]/@title")  # 五星评分
    if len(rating) > 0:
        rating = rating[0]

    comment_time = eachComment.xpath("./h3/span[@class='comment-info']/span[3]/@title")  # 评论时间
    if len(comment_time) > 0:
        comment_time = comment_time[0]
    else:
        comment_time = ' '

    votes = eachComment.xpath("./h3/span[@class='comment-vote']/span/text()")[0]  # "有用"数
    content = eachComment.xpath("./p/span/text()")[0]  # 评论内容

    commentlist.append(user)
    commentlist.append(watched)
    commentlist.append(rating)
    commentlist.append(comment_time)
    commentlist.append(votes)
    commentlist.append(content.strip())
    print(commentlist)
    return commentlist


def get_movie_info(eachMovie):
    movie_info = []
    # movie_id = movie_id
    movie_name = eachMovie.xpath('//span[@property="v:itemreviewed"]/text()')[0]
    release_year = eachMovie.xpath('//span[@class="year"]/text()')[0].strip('()')
    director = eachMovie.xpath('//div[@id="info"]/span[1]/span[@class="attrs"]/a/text()')[0]
    starring = eachMovie.xpath('//span[@class="actor"]//span[@class="attrs"]/a/text()')
    starring = ",".join(starring)
    genre = eachMovie.xpath('//span[@property="v:genre"]/text()')
    genre = ",".join(genre)
    info = eachMovie.xpath('//div[@id="info"]//text()')
    for i in range(0, len(info)):
        if str(info[i]).find('语言') != -1:
            languages = info[i + 1].replace(' / ', ',').strip()
        if str(info[i]).find('制片国家') != -1:
            country = info[i + 1].replace(' / ', ',').strip()
    country = country
    languages = languages
    rating_num = eachMovie.xpath('//strong[@property="v:average"]/text()')[0]
    vote_num = eachMovie.xpath('//span[@property="v:votes"]/text()')[0]
    rating_per_stars5 = eachMovie.xpath('//span[@class="rating_per"]/text()')[0]
    rating_per_stars4 = eachMovie.xpath('//span[@class="rating_per"]/text()')[1]
    rating_per_stars3 = eachMovie.xpath('//span[@class="rating_per"]/text()')[2]
    rating_per_stars2 = eachMovie.xpath('//span[@class="rating_per"]/text()')[3]
    rating_per_stars1 = eachMovie.xpath('//span[@class="rating_per"]/text()')[4]
    introduction = eachMovie.xpath('//span[@property="v:summary"]/text()')[0].strip()
    comment_num = eachMovie.xpath('//div[@id="comments-section"]/div[@class="mod-hd"]/h2//a/text()')[0]
    comment_num = re.findall('\d+', comment_num)[0]
    movie_info.extend([movie_name, release_year, director, starring, genre, country, languages,
                       rating_num, vote_num, rating_per_stars5, rating_per_stars4, rating_per_stars3,
                       rating_per_stars2, rating_per_stars1, comment_num, introduction])
    return movie_info


def get_comment_info_to_txt(movie_id, movie_name):
    """
    爬取指定影片的短评并写入txt文件（文件以影片名命名）
    :param movie_id:
    :param movie_name:
    :return:
    """
    base_url = 'https://movie.douban.com/subject/' + str(movie_id) + '/comments?start='
    all_page_comments = [base_url + '{}'.format(x) for x in range(0, 201, 20)]
    filename = movie_name + '.txt'
    for each_page in all_page_comments:
        try:
            html = get_source_page(each_page)
            selector = etree.HTML(html.text)
            comments = selector.xpath("//div[@class='comment']")
            comments_all = []
            for each in comments:
                # comments_all.append(get_comments(each))
                each_comment = get_comments(each)
                with open(filename, 'a', encoding='utf-8') as f:
                    # f.write(movie_name + '->' + str(movie_id) + '\n')
                    f.write(each_comment[0] + "\t" + each_comment[1] + "\t" + each_comment[2] + "\t" + each_comment[3] \
                            + "\t" + each_comment[4] + "\t" + each_comment[5] + "\n")
        except:
            # print('跳过一个页面')
            continue


def get_comment_info_to_cvs(movie_id, movie_name):
    """
    爬取指定影片的短评并写入csv文件（文件以影片名命名）
    :param movie_id:
    :param movie_name:
    :return:
    """
    base_url = 'https://movie.douban.com/subject/' + str(movie_id) + '/comments?start='
    all_page_comments = [base_url + '{}'.format(x) for x in range(0, 201, 20)]
    filename = movie_name + '.csv'
    number = 1
    for each_page in all_page_comments:
        try:
            html = get_source_page(each_page)
            selector = etree.HTML(html.text)
            comments = selector.xpath("//div[@class='comment']")
            comments_all = []
            for each in comments:
                comments_all.append(get_comments(each))
            data = pd.DataFrame(comments_all)
            print(data)
            exit()
            # 写入csv文件
            try:
                if number == 1:
                    csv_headers = ['用户', '是否看过', '评分', '评论时间', '有用数', '评论']
                    data.to_csv(filename, header=csv_headers, index=False, mode='a+', encoding="utf-8")
                    number += 1
                else:
                    data.to_csv(filename, header=False, index=False, mode='a+', encoding="utf-8")
            except UnicodeEncodeError:
                print("编码错误, 跳过...")
            data = []
        except:
            # print('跳过一个页面')
            continue


if __name__ == '__main__':
    ## 爬取影评
    # movies_id_and_title = get_hot_movies_id(1, '豆瓣高分')
    """
    :param movie_sum: 指定爬取电影的数量，范围 1~500
    :param movie_tag: 指定电影排行tag， 范围 '热门' or '豆瓣高分'
    """
    # start_spider_comment(movies_id_and_title)


    ## 爬取影片信息
    movies_id_and_title = get_hot_movies_id(10, '豆瓣高分')
    """
    :param movie_sum: 指定爬取电影的数量，范围 1~500
    :param movie_tag: 指定电影排行tag， 范围 '热门' or '豆瓣高分'
    """
    start_spider_movies_info(movies_id_and_title)
