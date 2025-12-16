import unittest
import data.refer as refer


class TestReferFunctions(unittest.TestCase):
    def test_get_holidays(self):
        calendar = refer.get_holidays('CFETS')
        if calendar is not None:
            print(calendar)
        else:
            print(calendar)

    def test_get_ir_index(self):
        ir_index_data = refer.get_ir_index(['CNY'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_ir_definition(self):
        ir_index_data = refer.get_ir_index_definition(['FR_001'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_ir_curve_list(self):
        ir_index_data = refer.get_ir_curve_list(['CNY'], ['FR_007'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_ir_curve_definition(self):
        ir_index_data = refer.get_ir_curve_definition(['CNY_FR_007'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_bond_yield_curve_list(self):
        ir_index_data = refer.get_bond_yield_curve_list(['CNY'], [], 'MKT')
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_bond_yield_curve_definition(self):
        ir_index_data = refer.get_bond_yield_curve_definition(['CN_RAILWAY_MKT'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_bond_credit_curve_list(self):
        ir_index_data = refer.get_bond_credit_curve_list(['CNY'], [], 'MKT')
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_bond_credit_curve_definition(self):
        ir_index_data = refer.get_bond_credit_curve_definition(['CN_SP_MTN_AA+_SPRD_STD'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_bond(self):
        bond_list = refer.get_bond(['VANILLA_BOND'], ['SOVEREIGN'], ['CNY'], [], [])
        if bond_list is not None:
            for data in bond_list:
                print(data)
        else:
            print(bond_list)

    def test_get_bond_definition(self):
        bond_definition = refer.get_bond_definition(['050220.IB'])
        if bond_definition is not None:
            for data in bond_definition:
                print(data)
        else:
            print(bond_definition)

    def test_get_bond_credit_info(self):
        bond_credit = refer.get_bond_credit_info(['050220.IB'])
        if bond_credit is not None:
            for data in bond_credit:
                print(data)
        else:
            print(bond_credit)

    def test_get_bond_issue_info(self):
        bond_issue = refer.get_bond_issue_info(['050220.IB'])
        if bond_issue is not None:
            for data in bond_issue:
                print(data)
        else:
            print(bond_issue)

    def test_get_bond_mkt_info(self):
        bond_mkt = refer.get_bond_mkt_info(['050220.IB'])
        if bond_mkt is not None:
            for data in bond_mkt:
                print(data)
        else:
            print(bond_mkt)

    def test_get_bond_class_info(self):
        bond_class = refer.get_bond_class_info(['050220.IB'])
        if bond_class is not None:
            for data in bond_class:
                print(data)
        else:
            print(bond_class)

    def test_get_bond_fee_info(self):
        bond_fee = refer.get_bond_fee_info(['050220.IB'])
        if bond_fee is not None:
            for data in bond_fee:
                print(data)
        else:
            print(bond_fee)

    def test_get_risk_factor_definition(self):
        ir_index_data = refer.get_risk_factor_definition(['RF_CN_TREAS_ZERO_1M'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)

    def test_get_risk_factor_group_definition(self):
        ir_index_data = refer.get_risk_factor_group_definition(['FI_BOND_IR_CN_IB_HIST_SIM_SCN_GROUP'])
        if ir_index_data is not None:
            for data in ir_index_data:
                print(data)
        else:
            print(ir_index_data)
