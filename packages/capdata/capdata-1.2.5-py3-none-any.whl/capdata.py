#! /usr/bin/env python
#coding=utf-8
import request.request as rq

def init(name, pwd):
    """
    capdata 认证
    :param name: 用户名
    :param pwd: 密码
    :return:
    """
    auth_json = {'account': name, 'pwd': pwd}
    token = rq.post_no_token("/capdata/auth", auth_json)
    rq.save_token(token)
    print('登录成功')

# 从data目录导入所有模块的函数
from data.curve import *
from data.market import *
from data.pricing import *
from data.risk import *
from data.refer import *

# 定义模块的公共接口
__all__ = [
    'init',
    # curve模块的函数
    'get_bond_yield_curve',
    'get_bond_spread_curve',
    'get_ir_yield_curve',
    'get_dividend_curve',
    'get_vol_surface',
    # market模块的函数
    'get_hist_mkt',
    'get_live_mkt',
    # pricing模块的函数
    'get_pricing',
    'get_valuation',
    # risk模块的函数
    'get_sim_bond_yield_curve',
    'get_hist_sim_ir_curve',
    'get_hist_sim_credit_curve',
    'get_hist_stressed_ir_curve',
    'get_hist_stressed_credit_curve',
    'get_inst_sim_pnl',
    'get_inst_stressed_pnl',
    'get_inst_var',
    # refer模块的函数
    'get_holidays',
    'get_ir_index',
    'get_ir_index_definition',
    'get_ir_curve_list',
    'get_ir_curve_definition',
    'get_bond_yield_curve_list',
    'get_bond_yield_curve_definition',
    'get_bond_credit_curve_list',
    'get_bond_credit_curve_definition',
    'get_bond',
    'get_bond_definition',
    'get_bond_credit_info',
    'get_bond_issue_info',
    'get_bond_mkt_info',
    'get_bond_class_info',
    'get_bond_fee_info',
    'get_risk_factor_definition',
    'get_risk_factor_group_definition',
    'get_ir_vanilla_instrument_definition',
    'get_ir_vanilla_swap_list',
    'get_ir_depo_list',
    'get_xccy_swap_list'
]