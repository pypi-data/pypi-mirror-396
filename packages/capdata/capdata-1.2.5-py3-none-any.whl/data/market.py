import request.request as rq
import pandas

def get_hist_mkt(inst, start, end, fields, window=None, mkt=None, freq="d", clazz: str = None):
    """
    获取历史行情数据
    :param inst: array
        (必填) 产品编码列表 ['200310.IB', '190008.IB']
    :param start: string
        (必填) 开始时间  2024-05-09
    :param end: string
        (必填) 结束时间  2024-05-10
    :param fields: array
        (必填) 需要返回的字段(open、close、high、low、pre_adj_close、post_adj_close、volume、turnover、num_trades、settlement、
    open_interest、bid、ask、bid_size、ask_size、trade、trade_size、level1、level2、level2_5、level2_10、lix)  ['bid','ask']
    :param fields: string
        (必填) 频率( 1m,1h, d, w)
    :param window: array
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :par(必填) am mkt: string
        (可选) 市场
    :return: 历史行情数据
    """
    data_json = {'inst': inst, 'start': start, 'end': end, 'freq': freq, 'window': window, 'mkt': mkt,
                 'fields': fields}
    result = rq.post_token("/capdata/get/hist/mkt", data_json)
    df = pandas.DataFrame(result)
    if len(df) > 0:
        df['date'] = pandas.to_datetime(df['date'])
        df = df.sort_values(by='date')
        if freq == 'd' or freq == 'w':
            col = ['inst', 'date'] + fields
            df = df.reindex(columns=col)
        else:
            col = ['inst', 'date', 'time'] + fields
            df = df.reindex(columns=col)
            df['time'] = df['date'].dt.time
        df['date'] = df['date'].dt.date
        return df
    else:
        return df


def get_live_mkt(inst, fields, mkt=""):
    """
    获取日内实时行情数据
    :param inst: array
        (必填) 产品编码列表 ['200310.IB', '190008.IB']
    :param fields: array
        (必填) 需要返回的字段(bid、ask、level1、level2、level2_5、level2_10、lix)  ['bid','ask']
    :param mkt: string
        (可选) 市场
    :return: 日内实时行情数据
    """
    data_json = {'inst': inst, 'mkt': mkt, 'fields': fields}
    result = rq.post_token("/capdata/get/live/mkt", data_json)
    df = pandas.DataFrame(result)
    if len(df) > 0:
        df['date'] = pandas.to_datetime(df['date'])
        df = df.sort_values(by='date')
        col = ['inst', 'date', 'time'] + fields
        df = df.reindex(columns=col)
        df['time'] = df['date'].dt.time
        df['date'] = df['date'].dt.date
        return df
    else:
        return df
