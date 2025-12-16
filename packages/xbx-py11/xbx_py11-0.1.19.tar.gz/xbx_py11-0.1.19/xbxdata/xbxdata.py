import time
from urllib.request import urlopen  # python自带爬虫库
import pandas as pd
import requests
from xtquant import xtdata  # 导入qmt库


def _request_stock_data(url, max_try_num=10, sleep_time=5):
    headers = {
        'Referer': 'http://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'
    }
    for i in range(max_try_num):
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response
        else:
            print("链接失败", response)
            time.sleep(sleep_time)


def get_stock_from_sina(code_list):
    """
    从新浪获取当日最新的股票数据
    :param code_list: 股票列表集合，例如：['sh600000', 'sh600002', 'sh600004']
    :return:当日最新的股票数据
    """
    url = "https://hq.sinajs.cn/list=" + ",".join(code_list)

    # =====抓取数据
    content = _request_stock_data(url).text  # 使用python自带的库，从网络上获取信息

    # =====将数据转换成DataFrame
    content = content.strip()  # 去掉文本前后的空格、回车等
    data_line = content.split('\n')  # 每行是一个股票的数据
    data_line = [i.replace('var hq_str_', '').split(',') for i in data_line]
    df = pd.DataFrame(data_line)  #

    # =====对DataFrame进行整理
    df[0] = df[0].str.split('="')
    df['stock_code'] = df[0].str[0].str.strip()
    df['stock_name'] = df[0].str[-1].str.strip()
    df['candle_end_time'] = df[30] + ' ' + df[31]  # 股票市场的K线，是普遍以当跟K线结束时间来命名的
    df['candle_end_time'] = pd.to_datetime(df['candle_end_time'])

    rename_dict = {1: 'open', 2: 'pre_close', 3: 'close', 4: 'high', 5: 'low', 6: 'buy1', 7: 'sell1',
                   8: 'amount', 9: 'volume', 32: 'status'}  # 自己去对比数据，会有新的返现
    # 其中amount单位是股，volume单位是元
    df.rename(columns=rename_dict, inplace=True)
    df['status'] = df['status'].str.strip('";')
    df = df[['stock_code', 'stock_name', 'candle_end_time', 'open', 'high', 'low', 'close', 'pre_close', 'amount',
             'volume', 'buy1', 'sell1', 'status']]

    # 将下面的列转换成数值类型
    for col in ['open', 'high', 'low', 'close', 'pre_close', 'amount', 'volume', 'buy1', 'sell1', 'status']:
        df[col] = df[col].astype(float)

    return df


def get_stock_from_qmt(code, period, start_time='', end_time=''):
    """
    从QMT获取最新的股票数据
    :param code: 股票代码，上交所股票：600000.SH，深交所股票：000001.SZ
    :param period: 数据周期，可以是：tick，1m，5m，1d
    :param start_time: 数据开始时间，如果不给，默认是今天的开盘时间（9点15分）
    :param end_time: 数据的截止时间，如果不给，默认是今天的收盘时间（15点30分）
    :return:
    """
    if start_time == '':
        # 开始时间是每天的9点15分，这样可以拿到早盘集合竞价的数据
        start_time = time.strftime("%Y%m%d091500", time.localtime())
    if end_time == '':
        # 截止时间是每天的15点30分，因为部分股票有盘后交易，且债券是15点30收盘
        end_time = time.strftime("%Y%m%d153000", time.localtime())

    # 因为我们是订阅模式，所以需要先订阅数据。详见文档xtdata.pdf，Page3
    sub_id = xtdata.subscribe_quote(code, period, count=-1)

    if end_time != '':
        # 下载历史数据，到本地。详见文档xtdata.pdf，Page8
        xtdata.download_history_data(code, period, start_time, end_time)
    # 获取数据 。详见文档xtdata.pdf，Page5
    mkt_data = xtdata.get_market_data([], [code], period, start_time, end_time)
    # tick数据的格式和1m的数据格式完全不一样，所以需要根据数据类型来转换
    if period == 'tick':
        mkt_df = pd.DataFrame(mkt_data[code])
    else:
        mkt_df = pd.concat(mkt_data).reset_index(level=1)
        mkt_df = mkt_df.drop(columns=['level_1']).T.reset_index(drop=True)
    mkt_df['time'] = mkt_df['time'].apply(lambda x: pd.to_datetime(x, unit='ms') + pd.to_timedelta('8h'))  # 时间戳转换为时间格式

    # 取消订阅。详见文档xtdata.pdf，Page4
    xtdata.unsubscribe_quote(sub_id)

    return mkt_df
