from flask import Flask, g, render_template, url_for
from proxypool.storages.redis import RedisClient
from proxypool.setting import API_HOST, API_PORT, API_THREADED
from analyse.movie_analyse import MovieInfoAnalyse

mia = MovieInfoAnalyse()
__all__ = ['app']

app = Flask(__name__)


def get_conn():
    """
    get redis client object
    :return:
    """
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis


@app.route('/')
def index():
    conn = get_conn()
    proxy_all = []
    for x in conn.batch(1, 10):
        proxy_each = str(x.host) + ':' + str(x.port)
        proxy_all.append(proxy_each)
    return render_template('index.html', proxy_count=str(conn.count()), proxy_all=proxy_all)


@app.route('/random')
def get_proxy():
    """
    get a random proxy
    :return: get a random proxy
    """
    conn = get_conn()
    return conn.random().string()


@app.route('/count')
def get_count():
    """
    get the count of proxies
    :return: count, int
    """
    conn = get_conn()
    return str(conn.count())


@app.route('/proxypool')
def proxypool():
    conn = get_conn()
    proxy_all = []
    for x in conn.batch(1, 7):
        proxy_each = str(x.host) + ':' + str(x.port)
        proxy_all.append(proxy_each)
    return render_template('proxypool.html', proxy_all=proxy_all)


@app.route('/wordcloud')
def wordcloud():
    return render_template('wordcloud.html')


@app.route('/analysis')
def analysis():
    return render_template('analysis.html')


@app.route("/make_relase_year_bar")
def get_make_relase_year_bar():
    c = mia.make_relase_year_bar()
    return c.dump_options_with_quotes()


@app.route("/make_pid_charts")
def get_make_pid_charts():
    c = mia.make_pid_charts()
    return c.dump_options_with_quotes()


@app.route("/make_star_treemap")
def get_make_star_treemap():
    c = mia.make_star_treemap()
    return c.dump_options_with_quotes()


@app.route("/make_sentiments_line")
def get_make_sentiments_line():
    c = mia.make_sentiments_line()
    return c.dump_options_with_quotes()

    
if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT, threaded=API_THREADED)
