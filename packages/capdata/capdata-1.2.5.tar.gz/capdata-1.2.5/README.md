# capdata

Python 金融数据接口库

官网地址：https://www.caprisktech.com/

## 安装

```bash
pip install capdata
```

## 使用方法

### 1. 登录认证

```python
import capdata
capdata.init("用户名", "密码")
```

### 2. 调用数据接口

```python
# 获取节假日数据
holidays = capdata.get_holidays('CFETS')

# 获取债券收益率曲线
curve_data = capdata.get_bond_yield_curve("CNY_FR007", "2024-01-01", "2024-01-31")

# 获取历史行情数据
market_data = capdata.get_hist_mkt(["200310.IB"], "2024-01-01", "2024-01-31", ["open", "close"])
```

## 发布到PyPI的步骤

1. 安装必要的工具：
   ```bash
   pip install twine setuptools wheel
   ```

2. 构建包：
   ```bash
   python setup.py sdist bdist_wheel
   ```

3. 上传包：
   ```bash
   twine upload dist/*
   ```