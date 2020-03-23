#!/usr/bin/python
# coding=utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import jieba
import jieba.analyse
import os
import time
import pyecharts.options as opts
from pyecharts.charts import Bar
from pyecharts.charts import WordCloud as eWordCloud
from pyecharts.render import make_snapshot
# 使用 snapshot-selenium 渲染图片
from snapshot_selenium import snapshot
from wordcloud import WordCloud
import logging

jieba.setLogLevel(logging.INFO)
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

if not os.path.exists('analyse_data'):
    os.mkdir('analyse_data')

def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def comment_cut_list(filename):
    """
    对一部影片的所有影评分词
    :param filename: 文件路径
    :return: segments -> list -> [{'word': '镜头', 'count': 1}, .....]
    """
    pd.set_option('max_colwidth', 500)
    rows = pd.read_csv(filename, encoding='utf-8', dtype=str)
    to_drop = ['用户', '是否看过', '评分', '评论时间', '有用数']
    rows.drop(to_drop, axis=1, inplace=True)
    segments = []
    for index, row in rows.iterrows():
        content = row[0]
        words = jieba.analyse.textrank(content, topK=20, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
        for word in words:
            segments.append({'word': word, 'count': 1})
    return segments


def make_frequencies_df(segments):
    """
    传入分词list并返回词频统计后的 pandas.DataFrame对象
    :param segments: list -> [{'word': '镜头', 'count': 1}, .....]
    :return: pandas.DataFrame对象
    """
    dfSg = pd.DataFrame(segments)
    dfWord = dfSg.groupby('word')['count'].sum()
    return dfWord


def wordcloud_save_to_file(dfword, title):
    """
    生成词云并保存为filename.jpg
    :param dfword: 词频统计后的 pandas.DataFrame对象
    :param title: 文件名
    :return:
    """
    filename = title + '.jpg'
    filepath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", filename))
    wordcloud = WordCloud(background_color='white', max_font_size=80,
                          min_font_size=8, mode='RGBA',
                          font_path='simhei.ttf', scale=10)
    word_frequence = {k: v for k, v in dfword.items()}
    wordcloud = wordcloud.fit_words(word_frequence)
    title = '电影"' + title + '"影评高频词云'
    plt.title(title, fontsize=18)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.margins(0, 0)
    plt.savefig(filepath, bbox_inches='tight', dpi=200)


def make_echarts_to_flask(dfword, title):
    """
    利用pyecharts生成词云
    :param dfword: 词频统计后的 pandas.DataFrame对象
    :param title:
    :return:
    """
    target_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "wordcloud_pic")
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    print("分析结果保存在 ", target_dir, " 文件夹下...")
    htmlName = title + '.html'
    pngName = title + '.png'
    htmlPath = os.path.join(target_dir, htmlName)
    pngPath = os.path.join(target_dir, pngName)
    word_frequence = [(k, v) for k, v in dfword.items()]
    # print(word_frequence)
    wc = eWordCloud()
    wc.add(series_name="word", data_pair=word_frequence, word_size_range=[20, 100])
    wc.set_global_opts(title_opts=opts.TitleOpts(
                title=title, pos_left="center", title_textstyle_opts=opts.TextStyleOpts(font_size=23)),
                tooltip_opts=opts.TooltipOpts(is_show=True))
    wc.render(htmlPath)
    # make_snapshot(snapshot, wc.render(htmlPath), pngPath)

def make_bar_rating(filename):
    # 定义各个文件名
    # title = filename.split('/')[-1].split('.')[0]
    title = os.path.basename(filename).split('.')[0]
    target_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "bar_echarts_pic")
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    print("分析结果保存在 ", target_dir, " 文件夹下...")
    htmlName = title + '.html'
    pngName = title + '.png'
    htmlPath = os.path.join(target_dir, htmlName)
    pngPath = os.path.join(target_dir, pngName)
    # 导入数据，并删除无关列
    rows = pd.read_csv(filename, encoding='utf-8', dtype=str)
    to_drop = ['用户', '是否看过', '评论时间', '有用数', '评论']
    rows.drop(to_drop, axis=1, inplace=True)
    # 数据清洗
    rows = rows[rows['评分'].isin(['力荐', '推荐', '还行', '较差', '很差'])]
    # 数据统计
    result_rating = rows.groupby('评分')['评分'].count()
    # 转换类型 pd.Series -> py.dict
    values = {i: v for i, v in result_rating.items()}
    # pyecharts 生成柱状图
    bar = Bar()
    bar.add_xaxis(['力荐', '推荐', '还行', '较差', '很差'])
    bar.add_yaxis(title, [values['力荐'], values['推荐'], values['还行'], values['较差'], values['很差']])
    bar.render(htmlPath)
    # make_snapshot(snapshot, bar.render(htmlPath), pngPath)


def make_bar_voter_star(filename):
    """
    生成水平直方图，根据影评有用数
    :param filename:
    :return:
    """
    # 定义各个文件名
    # title = filename.split('/')[-1].split('.')[0]
    title = os.path.basename(filename).split('.')[0]
    target_dir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "bar_voter_star_pic")
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    print("分析结果保存在 ", target_dir, " 文件夹下...")
    htmlName = title + '.html'
    pngName = title + '.png'
    htmlPath = os.path.join(target_dir, htmlName)
    pngPath = os.path.join(target_dir, pngName)
    # 导入数据，并删除无关列
    rows = pd.read_csv(filename, encoding='utf-8', dtype=str)
    to_drop=['是否看过', '评论时间', '评分', '评论']
    rows.drop(to_drop, axis=1, inplace=True)
    # 数据清洗
    rows['有用数'] = rows['有用数'].astype('int')
    # 数据统计
    result_voter_star = rows.sort_values(by='有用数', ascending=True).tail(15)
    # 转换类型 pd.Series -> py.list
    values = [(i[1], i[2]) for i in result_voter_star.itertuples()]
    # pyecharts 生成水平柱状图
    bar = Bar()
    bar.add_xaxis([i[0] for i in values])
    bar.add_yaxis('影评者获认同数', [i[1] for i in values])
    bar.reversal_axis()
    bar.set_global_opts(title_opts=opts.TitleOpts(title="电影<" + title + ">影评者影响力排行"))
    bar.render(htmlPath)
    # make_snapshot(snapshot, bar.render(htmlPath), pngPath)

def main():
    # base_dir = '../comments/each_comment/'
    base_dir = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "comment_data"))
    all_files = [os.path.join(base_dir, i) for i in os.listdir(base_dir) if os.path.splitext(i)[1] == '.csv']
    print('====================>> Start time: ' + get_current_time() + ' <<====================')
    print('========================>> 共' + str(len(all_files)) + ' 部影片 <<========================')
    number = 1
    for file in all_files:
        # title = file.split('/')[-1].split('.')[0]
        title = os.path.basename(file).split('.')[0]
        print(get_current_time() + '| ----->> 正在绘图 ' + str(number) + '. (' + title + ')...')
        number += 1
        try:
            ###### WordCloud 生成词云 ######
            # segments = comment_cut_list(file)
            # wordcloud_save_to_file(make_frequencies_df(segments), title)
            ###### pyecharts 生成词云 ######
            segments = comment_cut_list(file)
            make_echarts_to_flask(make_frequencies_df(segments), title)
            ###### pyecharts 生成bar 根据评分######
            make_bar_rating(file)
            ###### pyecharts 生成水平bar 根据有用数######
            make_bar_voter_star(file)
        except Exception as e:
            print(e)
            print(get_current_time() + '| ----->> 生成结果失败' + str(number) + '.(' + title + ')...')
    print('====================>> Finsh time: ' + get_current_time() + ' <<====================')


if __name__ == '__main__':
    main()
