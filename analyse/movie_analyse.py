#!/usr/bin/python
# coding=utf-8

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import jieba
import jieba.analyse
import os
from pyecharts import options as opts
from pyecharts.charts import Map
from pyecharts.charts import Pie
from pyecharts.charts import Bar
from pyecharts.charts import TreeMap
from pyecharts.charts import Line
from pyecharts.faker import Faker
from pyecharts.render import make_snapshot
# 使用 snapshot-selenium 渲染图片
from snapshot_selenium import snapshot
from snownlp import SnowNLP


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


class MovieInfoAnalyse(object):
    """
    TOP500电影信息分析类
    """
    def __init__(self):
        if not os.path.exists('analyse_data'):
            os.mkdir('analyse_data')
        print("所有分析结果保存在 analyse_data 文件夹下...")

    def make_geo_map(self):
        """
        生成世界地图，根据各国电影发行量
        :return:
        """
        # print(get_current_time() + '|-------> 正在生成 世界各国电影发行量 图表...')
        # 导入TOP500电影数据
        csv_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "movie_info_top500.csv"))
        rows = pd.read_csv(csv_path, encoding='utf-8', dtype=str)
        # 分析并统计数据
        col_country = rows['国别'].to_frame()
        res = col_country.groupby('国别')['国别'].count().sort_values(ascending=False)
        raw_data = [i for i in res.items()]

        # 导入映射数据，英文名 -> 中文名
        country_name = pd.read_json('countries_zh_to_en.json', orient='index')
        stand_data = [i for i in country_name[0].items()]

        # 数据转换
        res_code = []
        for raw_country in raw_data:
            for stand_country in stand_data:
                if stand_country[1] in raw_country[0]:
                    res_code.append(stand_country[0])
        code = pd.DataFrame(res_code).groupby(0)[0].count().sort_values(ascending=False)
        data = []
        for k, v in code.items():
            data.append([k, v])

        # 制作图表
        c = Map()
        c.add("电影发行量", data, "world")
        c.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        c.set_global_opts(title_opts=opts.TitleOpts(title="电影TOP500榜单中 - 世界各国电影发行量"),
                          visualmap_opts=opts.VisualMapOpts(max_=55))
        htmlPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "世界各国电影发行量.html"))
        pngPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "世界各国电影发行量.png"))
        # 生成html
        # c.render(htmlPath)
        # 生成png
        # make_snapshot(snapshot, c.render(), pngPath)
        # print(get_current_time() + '|-------> 已生成 世界各国电影发行量 图表...')
        return c

    def make_pid_charts(self):
        """
        根据电影类型生成饼图
        :return:
        """
        # print(get_current_time() + '|-------> 正在生成 各类型占比 图表...')
        # 导入数据并初始化
        csv_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "movie_info_top500.csv"))
        rows = pd.read_csv(csv_path, encoding='utf-8', dtype=str)
        to_drop = ['名称', '导演', '演员', '国别', '年份', '语言', '评分', '评分人数', '五星占比', '四星占比', '三星占比', '二星占比', '一星占比', '短评数',
                   '简介']
        res = rows.drop(to_drop, axis=1)
        # 数据分割
        type_list = []
        for i in res.itertuples():
            for j in i[1].split(','):
                type_list.append(j)
        # 数据统计
        df = pd.DataFrame(type_list, columns=['类型'])
        res = df.groupby('类型')['类型'].count().sort_values(ascending=False)
        res_list = []
        for i in res.items():
            res_list.append(i)
        # 生成饼图
        c = Pie()
        c.add("", res_list, center=["40%", "55%"], )
        c.set_global_opts(
            title_opts=opts.TitleOpts(title="电影TOP500榜单中 - 各类型占比"),
            legend_opts=opts.LegendOpts(type_="scroll", pos_left="80%", orient="vertical"),
        )
        c.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

        htmlPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "各类型占比.html"))
        pngPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "各类型占比.png"))
        # 生成html
        # c.render(htmlPath)
        # 生成png
        # make_snapshot(snapshot, c.render(), pngPath)
        # print(get_current_time() + '|-------> 已生成 各类型占比 图表...')
        return c

    def make_relase_year_bar(self):
        """
        生成各年份电影发行量柱状图
        :return:
        """
        # print(get_current_time() + '|-------> 正在生成 各年份电影发行量 图表...')
        # 导入数据并初始化
        csv_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "movie_info_top500.csv"))
        rows = pd.read_csv(csv_path, encoding='utf-8', dtype=str)
        to_drop = ['名称', '导演', '演员', '国别', '类型', '语言', '评分', '评分人数', '五星占比', '四星占比', '三星占比', '二星占比', '一星占比', '短评数',
                   '简介']
        res = rows.drop(to_drop, axis=1)
        # 数据分析
        res_by = res.groupby('年份')['年份'].count().sort_values(ascending=False)
        res_by2 = res_by.sort_index(ascending=False)
        type(res_by2)
        years = []
        datas = []
        for k, v in res_by2.items():
            years.append(k)
            datas.append(v)
        # 生成图标
        c = Bar()
        c.add_xaxis(years)
        c.add_yaxis("发行电影数量", datas, color=Faker.rand_color())
        c.set_global_opts(
            title_opts=opts.TitleOpts(title="电影TOP500榜单中 - 各年份电影发行量"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        )
        htmlPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "各年份电影发行量.html"))
        pngPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "各年份电影发行量.png"))
        # 生成html
        # c.render(htmlPath)
        # 生成png
        # make_snapshot(snapshot, c.render(), pngPath)
        # print(get_current_time() + '|-------> 已生成 各年份电影发行量 图表...')
        return c

    def make_star_treemap(self):
        """
        根据演员参演电影数生成矩形树图
        :return:
        """
        # print(get_current_time() + '|-------> 正在生成 演员参演电影数 图表...')
        # 导入数据并初始化
        csv_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "movie_info_top500.csv"))
        rows = pd.read_csv(csv_path, encoding='utf-8', dtype=str)
        # rows = pd.read_csv('../comments/movie_info_top500.csv', encoding='utf-8', dtype=str)
        to_drop = ['名称', '导演', '年份', '国别', '类型', '语言', '评分', '评分人数', '五星占比', '四星占比', '三星占比', '二星占比', '一星占比', '短评数',
                   '简介']
        res = rows.drop(to_drop, axis=1)
        # 数据分割
        all_star_list = []
        for i in res.itertuples():
            #     print(i[1] + '\n')
            for j in i[1].split(','):
                all_star_list.append(j)
        # 数据统计
        df = pd.DataFrame(all_star_list, columns=['演员'])
        res = df.groupby('演员')['演员'].count().sort_values(ascending=False)
        all_star_list = []
        for i in res.items():
            if i[1] > 4:
                all_star_list.append({"value": i[1], "name": i[0]})
        # 生成图标
        c = TreeMap()
        c.add("参演电影数", all_star_list)
        c.set_global_opts(title_opts=opts.TitleOpts(title="电影TOP500榜单中 - 演员参演电影数", subtitle="至少参演5部影评以上"))

        htmlPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "演员参演电影数.html"))
        pngPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "演员参演电影数.png"))
        # 生成html
        c.render(htmlPath)
        # 生成png
        make_snapshot(snapshot, c.render(), pngPath)
        # print(get_current_time() + '|-------> 已生成 演员参演电影数 图表...')
        return c

    def make_sentiments_line(self):
        csv_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir, "moviespider", "comment_data", "极速车王.csv"))
        df = pd.read_csv(csv_path)
        to_drop = ['用户', '是否看过', '评分', '评论时间', '有用数']
        df.drop(to_drop, axis=1, inplace=True)
        str = df.to_string(index=False, columns=['评论'], header=False)
        str = [i.strip() for i in str.split('\n')]
        sentimentslist = []
        for i in str:
            s = SnowNLP(i)
            sentimentslist.append(s.sentiments - 0.5)
        c = (
            Line()
                .add_xaxis([x for x in range(len(sentimentslist))])
                .add_yaxis("情感积极度", sentimentslist, is_smooth=True)
                .set_series_opts(
                areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
                label_opts=opts.LabelOpts(is_show=False),
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(title="《极速车王》影评情感分析", subtitle="接近0.5为积极，接近-0.5为消极"),
                xaxis_opts=opts.AxisOpts(
                    axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                    is_scale=False,
                    boundary_gap=False,
                ),
            )
        )
        htmlPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "《极速车王》影评情感分析.html"))
        pngPath = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "analyse_data", "《极速车王》影评情感分析.png"))
        # 生成html
        # c.render(htmlPath)
        # 生成png
        # make_snapshot(snapshot, c.render(), pngPath)
        return c

if __name__ == '__main__':
    m = MovieInfoAnalyse()
    # m.make_geo_map()
    # m.make_pid_charts()
    # m.make_relase_year_bar()
    # m.make_star_treemap()
    m.make_sentiments_line()
