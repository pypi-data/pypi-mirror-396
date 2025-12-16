import request.request as rq

def get_bond_yield_curve(curve, start, end, freq='d', window=None, parse_proto=True):
    """
    获取债券收益率曲线
    :param curve: srt
        (必填) 曲线编码
    :param start: srt
        (必填) 开始时间
    :param end: srt
        (必填) 结束时间
    :param freq: srt
        (必填) 频率(1m, d, w)
    :param window: List[str]
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :param parse_proto: bool
        (可选) 是否转化曲线,默认True
    :return: 债券收益率曲线
    """
    data_json = {'curve': curve, 'start': start, 'end': end, 'freq': freq, 'window': window, 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/bond/curve", data_json)


def get_bond_spread_curve(curve, start, end, freq='d', window=None, parse_proto=True):
    """
    获取信用利差曲线
    :param curve: srt
        (必填) 曲线编码
    :param start: srt
        (必填) 开始时间
    :param end: srt
        (必填) 结束时间
    :param freq: srt
        (可选) 频率(1m, d, w)
    :param window: List[str]
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :param parse_proto: bool
        (必填) 是否转化曲线,默认True
    :return: 信用利差曲线
    """
    data_json = {'curve': curve, 'start': start, 'end': end, 'freq': freq, 'window': window, 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/credit/curve", data_json)


def get_ir_yield_curve(curve, start, end, freq='d', window=None, parse_proto=True):
    """
    获取利率收益率曲线
    :param curve: srt
        (必填) 曲线编码
    :param start: srt
        (必填) 开始时间
    :param end: srt
        (必填) 结束时间
    :param freq: srt
        (必填) 频率(1m, d, w)
    :param window: List[str]
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :param parse_proto: bool
        (可选) 是否转化曲线,默认True
    :return: 利率收益率曲线
    """
    data_json = {'curve': curve, 'start': start, 'end': end, 'freq': freq, 'window': window, 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/ir/curve", data_json)


def get_dividend_curve(curve, start, end, freq='d', window=None, parse_proto=True):
    """
    获取股息分红率曲线
    :param curve: srt
        (必填) 曲线编码
    :param start: srt
        (必填) 开始时间
    :param end: srt
        (必填) 结束时间
    :param freq: srt
        (必填) 频率(1m, d, w)
    :param window: List[str]
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :param parse_proto: bool
        (可选) 是否转化曲线,默认True
    :return: 股息分红率曲线
    """
    data_json = {'curve': curve, 'start': start, 'end': end, 'freq': freq, 'window': window, 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/dividend/curve", data_json)


def get_vol_surface(surface, start, end, freq='d', window=None):
    """
    获取波动率曲面数据
    :param surface: srt
        (必填) 波动率曲面编码
    :param start: srt
        (必填) 开始时间
    :param end: srt
        (必填) 结束时间
    :param freq: srt
        (必填) 频率(1m, d, w)
    :param window: List[str]
        (可选) 时间窗口 ['10:00:00','10:30:00']
    :return: 波动率曲面数据
    """
    data_json = {'surface': surface, 'start': start, 'end': end, 'freq': freq, 'window': window}
    return rq.post_token("/capdata/get/fx/vol/surface", data_json)
