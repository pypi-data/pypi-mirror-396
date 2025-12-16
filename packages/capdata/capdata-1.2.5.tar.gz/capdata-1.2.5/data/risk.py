import request.request as rq

def get_sim_bond_yield_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取债券收益率曲线情景模拟数据
    :param curve: str
        (必填) 曲线编码
    :param sim_date: str
        (必填) 情景时间
    :param base_date: str
        (必填) 基础时间
    :param num_start: int
        (必填) 情景开始数
    :param num_end: int
        (必填) 情景结束数
    :param parse_proto: bool
        (可选) 是否转化proto
    :return: 债券收益率曲线情景模拟数据
    """
    data_json = {'curve': curve, 'simDate': sim_date, 'baseDate': base_date, 'numStart': num_start, 'numEnd': num_end,
                 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/sim/bond/yield/curve", data_json)


def get_hist_sim_ir_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取历史模拟的利率收益率曲线数据
    :param curve: str
        (必填) 曲线编码
    :param sim_date: str
        (必填) 情景时间
    :param base_date: str
        (必填) 基础时间
    :param num_start: int
        (必填) 情景开始数
    :param num_end: int
        (必填) 情景结束数
    :param parse_proto: bool
        (可选) 是否转化proto
    :return: 历史模拟的利率收益率曲线数据
    """
    data_json = {'curve': curve, 'simDate': sim_date, 'baseDate': base_date,'numStart': num_start, 'numEnd': num_end,
                 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/sim/ir/curve", data_json)


def get_hist_sim_credit_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取历史模拟的信用利差曲线数据
    :param curve: str
        (必填) 曲线编码
    :param sim_date: str
        (必填) 情景时间
    :param base_date: str
        (必填) 基础时间
    :param num_start: int
        (必填) 情景开始数
    :param num_end: int
        (必填) 情景结束数
    :param parse_proto: bool
        (可选) 是否转化proto
    :return: 历史模拟的信用利差曲线数据
    """
    data_json = {'curve': curve, 'simDate': sim_date, 'baseDate': base_date, 'numStart': num_start, 'numEnd': num_end,
                 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/sim/bond/spread/curve", data_json)


def get_hist_stressed_ir_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取历史压力情景下利率收益率曲线数据
    :param curve: str
        (必填) 曲线编码
    :param sim_date: str
        (必填) 情景时间
    :param base_date: str
        (必填) 基础时间
    :param num_start: int
        (必填) 情景开始数
    :param num_end: int
        (必填) 情景结束数
    :param parse_proto: bool
        (可选) 是否转化proto
    :return: 历史压力情景下利率收益率曲线数据
    """
    data_json = {'curve': curve, 'simDate': sim_date, 'baseDate': base_date, 'numStart': num_start, 'numEnd': num_end,
                 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/sim/stressed/ir/curve", data_json)


def get_hist_stressed_credit_curve(curve, sim_date, base_date, num_start=0, num_end=500, parse_proto=False):
    """
    获取历史压力情景下信用利差曲线数据
    :param curve: str
        (必填) 曲线编码
    :param sim_date: str
        (必填) 情景时间
    :param base_date: str
        (必填) 基础时间
    :param num_start: int
        (必填) 情景开始数
    :param num_end: int
        (必填) 情景结束数
    :param parse_proto: bool
        (可选) 是否转化proto
    :return: 历史压力情景下信用利差曲线数据
    """
    data_json = {'curve': curve, 'simDate': sim_date, 'baseDate': base_date, 'numStart': num_start, 'numEnd': num_end,
                 'parseProto': parse_proto}
    return rq.post_token("/capdata/get/sim/stressed/bond/spread/curve", data_json)


def get_inst_sim_pnl(inst, sim_date, base_date, num_sims=200):
    """
    获取产品模拟情景下损益数据
    :param inst: List[str]
        (必填) 产品编码
    :param sim_date: str
        (必填) 情景时间
    :param num_sims: int
        (必填) 情景数
    :param base_date: str
        (必填) 基础时间
    :return: 产品模拟情景下损益数据
    """
    data_json = {'inst': inst, 'simDate': sim_date, 'baseDate': base_date, 'numSims': num_sims}
    return rq.post_token("/capdata/get/inst/sim/pnl", data_json)


def get_inst_stressed_pnl(inst, sim_date, base_date, num_sims=200):
    """
    获取产品压力情景下损益数据
    :param inst: List[str]
        (必填) 产品编码
    :param sim_date: str
        (必填) 情景时间
    :param num_sims: int
        (必填) 情景数
    :param base_date: str
        (必填) 基础时间
    :return: 产品压力情景下损益数据
    """
    data_json = {'inst': inst, 'simDate': sim_date, 'baseDate': base_date, 'numSims': num_sims}
    return rq.post_token("/capdata/get/inst/stressed/pnl", data_json)


"""
获取产品Value-at-Risk数据
参数:
  inst -- 产品编码  2171035.IB
  sim_date -- 情景时间  2024-05-28 
  base_date -- 基础时间 2024-05-27
  fields -- 响应字段 (var, mirror_var, stressed_var, mirror_stressed_var, es, mirror_es, stressed_es, mirror_stressed_es) ['var','es']
  confidence_interval  -- 置信区间 0.95
"""


def get_inst_var(inst, sim_date, base_date, fields, confidence_interval=0.95):
    """
    获取产品Value-at-Risk数据
    :param inst: str
        (必填) 产品编码
    :param sim_date: str
        (必填)  情景时间
    :param base_date: str
        (必填) 基础时间
    :param fields: List[str]
        (必填) 响应字段
    :param confidence_interval: float
        (必填) 置信区间
    :return: 产品Value-at-Risk数据
    """
    data_json = {'inst': inst, 'simDate': sim_date, 'baseDate': base_date, 'fields': fields,
                 'confidenceInterval': confidence_interval}
    return rq.post_token("/capdata/get/inst/risk/metrics", data_json)
