import os
import akshare as ak
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
from . import db

# 创建股票估值蓝图
stock_bp = Blueprint('stock', __name__, url_prefix='/stock')


def token_required(f):
    """JWT token验证装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '缺少token'}), 401

        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'token无效'}), 401

        return f(*args, **kwargs)

    return decorated


class DCFValuation:
    """DCF估值模型类"""

    def __init__(self):
        self.risk_free_rate = 0.03  # 无风险利率，默认3%

    def fcf_by_net_income(self, net_income, interest_exp, amort, deprec, change_wc, cap_exp):
        """
        根据净利润计算自由现金流
        FCF = 净利润 + 利息费用 + 摊销 + 折旧 - 营运资本变动 - 资本支出
        """
        try:
            fcf = net_income + interest_exp + amort + deprec - change_wc - cap_exp
            return fcf
        except Exception as e:
            print(f"计算FCF时出错: {e}")
            return 0

    def common_dcf(self, fcf, discount_rate, stage1_years=5, stage1_growth=0.1,
                   stage2_years=5, stage2_growth=0.05, stage3_years=0, stage3_growth=0.02):
        """
        通用DCF计算方法，支持多阶段增长
        """
        try:
            total_value = 0
            current_fcf = fcf

            # 第一阶段：高增长期
            if stage1_years > 0:
                for year in range(1, stage1_years + 1):
                    current_fcf = current_fcf * (1 + stage1_growth)
                    pv = current_fcf / ((1 + discount_rate) ** year)
                    total_value += pv

            # 第二阶段：中期增长
            if stage2_years > 0:
                stage2_start_year = stage1_years + 1
                for year in range(stage2_start_year, stage2_start_year + stage2_years):
                    current_fcf = current_fcf * (1 + stage2_growth)
                    pv = current_fcf / ((1 + discount_rate) ** year)
                    total_value += pv

            # 第三阶段：永续增长或稳定期
            if stage3_years == 0:  # 永续增长
                terminal_year = stage1_years + stage2_years + 1
                terminal_fcf = current_fcf * (1 + stage3_growth)
                terminal_value = terminal_fcf / (discount_rate - stage3_growth)
                terminal_pv = terminal_value / ((1 + discount_rate) ** (terminal_year - 1))
                total_value += terminal_pv
            else:  # 有限期增长
                stage3_start_year = stage1_years + stage2_years + 1
                for year in range(stage3_start_year, stage3_start_year + stage3_years):
                    current_fcf = current_fcf * (1 + stage3_growth)
                    pv = current_fcf / ((1 + discount_rate) ** year)
                    total_value += pv

            return total_value
        except Exception as e:
            print(f"DCF计算时出错: {e}")
            return 0


def get_stock_info_from_akshare(stock_input):
    """从AKShare获取股票信息"""
    try:
        # 获取股票列表
        stock_list = ak.stock_info_a_code_name()

        # 判断输入是股票代码还是公司名称
        if stock_input.isdigit():
            # 输入是股票代码
            stock_code = stock_input.zfill(6)  # 补齐到6位
            stock_info = stock_list[stock_list['code'] == stock_code]
            if not stock_info.empty:
                return {
                    'code': stock_code,
                    'name': stock_info.iloc[0]['name'],
                    'success': True
                }
        else:
            # 输入是公司名称
            stock_info = stock_list[stock_list['name'].str.contains(stock_input, na=False)]
            if not stock_info.empty:
                return {
                    'code': stock_info.iloc[0]['code'],
                    'name': stock_info.iloc[0]['name'],
                    'success': True
                }

        return {'success': False, 'message': '未找到匹配的股票信息'}
    except Exception as e:
        return {'success': False, 'message': f'获取股票信息失败: {str(e)}'}


def get_stock_info_from_database(stock_input):
    """从数据库获取股票信息"""
    try:
        print(f"从数据库搜索股票信息: {stock_input}")

        # 判断输入是股票代码还是公司名称
        if stock_input.isdigit():
            # 输入是股票代码
            stock_code = stock_input.zfill(6)  # 补齐到6位
            result = db.query_db(
                'SELECT DISTINCT stock_code, company_name FROM financial_data WHERE stock_code = %s LIMIT 1',
                (stock_code,),
                one=True
            )
        else:
            # 输入是公司名称（模糊搜索）
            result = db.query_db(
                'SELECT DISTINCT stock_code, company_name FROM financial_data WHERE company_name LIKE %s LIMIT 1',
                (f'%{stock_input}%',),
                one=True
            )

        if result:
            print(f"找到股票信息: {result['company_name']} ({result['stock_code']})")
            return {
                'code': result['stock_code'],
                'name': result['company_name'],
                'success': True
            }
        else:
            print("数据库中未找到匹配的股票信息")
            return {'success': False, 'message': '未找到匹配的股票信息'}

    except Exception as e:
        print(f"数据库查询错误: {e}")
        return {'success': False, 'message': f'获取股票信息失败: {str(e)}'}


def get_financial_data_from_database(stock_code):
    """从数据库获取财务数据"""
    try:
        print(f"从数据库获取股票 {stock_code} 的财务数据...")

        # 查询最近3年的财务数据
        financial_records = db.query_db(
            '''SELECT stock_code, company_name, report_year, report_date, 
                      net_income, interest_expense, depreciation, capex, 
                      current_assets, current_liabilities, total_shares
               FROM financial_data 
               WHERE stock_code = %s 
               ORDER BY report_year DESC 
               LIMIT 3''',
            (stock_code,)
        )

        if not financial_records:
            print(f"数据库中未找到股票 {stock_code} 的财务数据")
            return {'success': False, 'message': '数据库中未找到该股票的财务数据'}

        print(f"从数据库获取到 {len(financial_records)} 年的财务数据")

        # 转换数据格式
        financial_data = []
        for record in financial_records:
            year_data = {
                'year': str(record['report_date']),
                'net_income': float(record['net_income']) if record['net_income'] else 0,
                'interest_expense': float(record['interest_expense']) if record['interest_expense'] else 0,
                'depreciation': float(record['depreciation']) if record['depreciation'] else 0,
                'capex': float(record['capex']) if record['capex'] else 0,
                'current_assets': float(record['current_assets']) if record['current_assets'] else 0,
                'current_liabilities': float(record['current_liabilities']) if record['current_liabilities'] else 0,
                'total_shares': int(record['total_shares']) if record['total_shares'] else 0,
            }
            financial_data.append(year_data)
            print(f"{record['report_year']}年数据: 净利润={year_data['net_income'] / 100000000:.2f}亿")

        return {'success': True, 'data': financial_data}

    except Exception as e:
        print(f"从数据库获取财务数据失败: {e}")
        return {'success': False, 'message': f'获取财务数据失败: {str(e)}'}


def get_financial_data_mixed(stock_code):
    """混合获取财务数据：先从数据库获取，如果没有则生成fake数据"""
    try:
        print(f"混合方式获取股票 {stock_code} 的财务数据...")

        # 先尝试从数据库获取
        db_result = get_financial_data_from_database(stock_code)
        if db_result['success']:
            print(f"从数据库获取到财务数据")
            return db_result

        # 数据库没有数据，生成fake数据
        print(f"数据库中没有财务数据，生成fake数据...")
        return generate_fake_financial_data(stock_code)

    except Exception as e:
        print(f"混合获取财务数据失败: {e}")
        return {'success': False, 'message': f'获取财务数据失败: {str(e)}'}


def generate_fake_financial_data(stock_code):
    """为指定股票生成fake财务数据"""
    try:
        print(f"为股票 {stock_code} 生成fake财务数据...")

        # 基础数据（根据股票代码生成相对合理的数据）
        base_seed = sum(ord(c) for c in stock_code)  # 根据股票代码生成种子
        import random
        random.seed(base_seed)  # 确保同一股票生成相同的fake数据

        # 生成基础财务指标（单位：元）
        base_net_income = random.uniform(5, 100) * 100000000  # 5-100亿净利润
        base_revenue = base_net_income * random.uniform(3, 8)  # 营收通常是净利润的3-8倍

        financial_data = []

        # 生成2022-2024年的数据
        for i in range(3):
            year = 2024 - i  # 2024, 2023, 2022

            # 模拟业务增长/下降
            growth_factor = random.uniform(0.95, 1.15) ** (2 - i)  # 2022到2024年的增长

            net_income = base_net_income * growth_factor
            interest_expense = net_income * random.uniform(0.02, 0.15)  # 利息支出占净利润2-15%
            depreciation = net_income * random.uniform(0.1, 0.3)  # 折旧占净利润10-30%
            capex = net_income * random.uniform(0.15, 0.4)  # 资本支出占净利润15-40%

            # 资产负债相关
            total_assets = base_revenue * random.uniform(1.5, 3)  # 总资产通常是营收的1.5-3倍
            current_assets = total_assets * random.uniform(0.3, 0.6)  # 流动资产占总资产30-60%
            current_liabilities = current_assets * random.uniform(0.6, 0.9)  # 流动负债占流动资产60-90%

            year_data = {
                'year': f'{year}-12-31',
                'net_income': round(net_income, 2),
                'interest_expense': round(interest_expense, 2),
                'depreciation': round(depreciation, 2),
                'capex': round(capex, 2),
                'current_assets': round(current_assets, 2),
                'current_liabilities': round(current_liabilities, 2),
                'total_shares': 0,  # 股本从AKShare获取
            }
            financial_data.append(year_data)
            print(f"生成{year}年fake数据: 净利润={net_income / 100000000:.2f}亿")

        return {
            'success': True,
            'data': financial_data,
            'note': '该股票的财务数据为模拟数据，仅供参考'
        }

    except Exception as e:
        print(f"生成fake财务数据失败: {e}")
        return {'success': False, 'message': f'生成财务数据失败: {str(e)}'}


def get_financial_data_from_akshare(stock_code):
    """从AKShare获取财务数据"""
    try:
        print(f"正在获取股票 {stock_code} 的财务数据...")

        # 获取现金流量表数据
        try:
            cash_flow = ak.stock_cash_flow_sheet_by_yearly_em(symbol=stock_code)
            if cash_flow is None:
                print(f"现金流量表API返回None，可能是股票代码不存在或API问题")
                cash_flow = pd.DataFrame()
            else:
                print(f"现金流量表数据获取成功，共 {len(cash_flow)} 条记录")
                if not cash_flow.empty:
                    print(f"现金流量表字段: {cash_flow.columns.tolist()}")
        except Exception as e:
            print(f"获取现金流量表失败: {e}")
            cash_flow = pd.DataFrame()

        # 获取资产负债表数据
        try:
            balance_sheet = ak.stock_balance_sheet_by_yearly_em(symbol=stock_code)
            if balance_sheet is None:
                print(f"资产负债表API返回None，可能是股票代码不存在或API问题")
                balance_sheet = pd.DataFrame()
            else:
                print(f"资产负债表数据获取成功，共 {len(balance_sheet)} 条记录")
                if not balance_sheet.empty:
                    print(f"资产负债表字段: {balance_sheet.columns.tolist()}")
        except Exception as e:
            print(f"获取资产负债表失败: {e}")
            balance_sheet = pd.DataFrame()

        # 获取利润表数据
        try:
            income_statement = ak.stock_profit_sheet_by_yearly_em(symbol=stock_code)
            if income_statement is None:
                print(f"利润表API返回None，可能是股票代码不存在或API问题")
                income_statement = pd.DataFrame()
            else:
                print(f"利润表数据获取成功，共 {len(income_statement)} 条记录")
                if not income_statement.empty:
                    print(f"利润表字段: {income_statement.columns.tolist()}")
        except Exception as e:
            print(f"获取利润表失败: {e}")
            income_statement = pd.DataFrame()

        if cash_flow.empty or balance_sheet.empty or income_statement.empty:
            # 尝试使用备用方法获取基础财务数据
            print("尝试使用备用方法获取财务数据...")
            return get_simplified_financial_data(stock_code)

        # 处理最近3年的数据
        recent_years = min(3, len(cash_flow))
        financial_data = []

        for i in range(recent_years):
            try:
                # 从现金流量表获取数据
                cf_data = cash_flow.iloc[i]
                # 从资产负债表获取数据
                bs_data = balance_sheet.iloc[i]
                # 从利润表获取数据
                is_data = income_statement.iloc[i]

                # 尝试不同的字段名称
                def safe_get_value(data, possible_keys, default=0):
                    for key in possible_keys:
                        value = data.get(key, None)
                        if value is not None and pd.notna(value):
                            try:
                                return float(value)
                            except:
                                continue
                    return default

                year_data = {
                    'year': cf_data.get('REPORT_DATE', cf_data.get('报告期', '')),
                    'net_income': safe_get_value(is_data, ['净利润', 'net_income']),
                    'interest_expense': safe_get_value(is_data, ['利息支出', 'interest_expense', '财务费用']),
                    'depreciation': safe_get_value(cf_data, ['折旧与摊销', 'depreciation', '折旧费用', '摊销费用']),
                    'capex': abs(safe_get_value(cf_data, [
                        '购建固定资产、无形资产和其他长期资产支付的现金',
                        '购建固定资产支付的现金',
                        'capex',
                        '资本支出'
                    ])),
                    'current_assets': safe_get_value(bs_data, ['流动资产合计', 'current_assets', '流动资产总计']),
                    'current_liabilities': safe_get_value(bs_data,
                                                          ['流动负债合计', 'current_liabilities', '流动负债总计']),
                }

                print(f"第{i + 1}年数据: {year_data}")
                financial_data.append(year_data)

            except Exception as e:
                print(f"处理第{i + 1}年数据时出错: {e}")
                continue

        if not financial_data:
            return {'success': False, 'message': '无法解析财务数据，可能字段格式已变更'}

        return {'success': True, 'data': financial_data}
    except Exception as e:
        print(f"获取财务数据总体错误: {e}")
        return {'success': False, 'message': f'获取财务数据失败: {str(e)}'}


def get_stock_shares_from_akshare(stock_code):
    """从AKShare获取股本信息"""
    try:
        print(f"正在获取股票 {stock_code} 的股本信息...")

        # 尝试获取股本结构数据
        try:
            shares_info = ak.stock_share_change_sse(symbol=stock_code)
            if shares_info is not None and not shares_info.empty:
                # 获取最新的总股本（单位：万股）
                total_shares = float(shares_info.iloc[0]['总股本']) * 10000  # 转换为股
                print(f"从股本变动数据获取总股本: {total_shares} 股")
                return {'success': True, 'total_shares': total_shares}
        except Exception as e:
            print(f"获取股本结构数据失败: {e}")

        # 如果无法获取股本数据，尝试从基本信息获取
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if stock_info is not None and not stock_info.empty:
                print(f"股票基本信息可用，尝试提取总股本...")
                shares_row = stock_info[stock_info['item'] == '总股本']
                if not shares_row.empty:
                    shares_str = shares_row.iloc[0]['value']
                    print(f"总股本字符串: {shares_str}")
                    # 解析股本数值（可能包含单位）
                    import re
                    numbers = re.findall(r'[\d.]+', shares_str)
                    if numbers:
                        total_shares = float(numbers[0])
                        if '万' in shares_str:
                            total_shares *= 10000
                        elif '亿' in shares_str:
                            total_shares *= 100000000
                        print(f"解析得到总股本: {total_shares} 股")
                        return {'success': True, 'total_shares': total_shares}
                else:
                    print("基本信息中未找到总股本字段")
                    # 使用估算股本（基于市值和价格）
                    print("使用估算股本...")
                    estimated_shares = 10000000000  # 估算100亿股
                    return {'success': True, 'total_shares': estimated_shares}
        except Exception as e:
            print(f"从基本信息获取股本失败: {e}")

        # 如果都失败了，使用默认估算值
        print("使用默认估算股本...")
        estimated_shares = 10000000000  # 估算100亿股
        return {'success': True, 'total_shares': estimated_shares}

    except Exception as e:
        print(f"获取股本信息总体错误: {e}")
        # 即使出错也返回估算值，确保DCF计算能继续
        estimated_shares = 10000000000  # 估算100亿股
        return {'success': True, 'total_shares': estimated_shares}


def get_simplified_financial_data(stock_code):
    """备用方法：获取简化的财务数据用于DCF计算"""
    try:
        print(f"使用简化方法获取股票 {stock_code} 的财务数据...")

        # 尝试使用基础API获取关键指标
        try:
            # 获取股票基本信息，包含一些财务指标
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if stock_info is not None and not stock_info.empty:
                print(f"股票基本信息获取成功: {len(stock_info)} 条记录")
                print(f"可用信息: {stock_info['item'].tolist()}")

                # 构造模拟的财务数据（用于演示）
                financial_data = []

                # 模拟3年的数据
                for i in range(3):
                    year = 2023 - i
                    # 这里使用估算值，实际应用中需要真实数据
                    estimated_data = {
                        'year': f'{year}-12-31',
                        'net_income': 1000000000 * (1.1 ** (2 - i)),  # 假设净利润10亿，每年增长10%
                        'interest_expense': 50000000 * (1.05 ** (2 - i)),  # 假设利息支出5000万
                        'depreciation': 200000000 * (1.03 ** (2 - i)),  # 假设折旧2亿
                        'capex': 300000000 * (1.08 ** (2 - i)),  # 假设资本支出3亿
                        'current_assets': 5000000000 * (1.05 ** (2 - i)),  # 假设流动资产50亿
                        'current_liabilities': 3000000000 * (1.05 ** (2 - i)),  # 假设流动负债30亿
                    }
                    financial_data.append(estimated_data)
                    print(f"模拟第{i + 1}年数据: {estimated_data}")

                return {
                    'success': True,
                    'data': financial_data,
                    'note': '由于无法获取详细财务报表，使用了估算数据进行DCF计算，结果仅供参考'
                }
            else:
                return {'success': False, 'message': '无法获取股票基本信息'}

        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return {'success': False, 'message': f'获取财务数据失败: {str(e)}'}

    except Exception as e:
        print(f"简化财务数据获取失败: {e}")
        return {'success': False, 'message': f'获取财务数据失败: {str(e)}'}


@stock_bp.route('/search', methods=['POST'])
@token_required
def search_stock():
    """搜索股票信息"""
    data = request.get_json()
    stock_input = data.get('stock_input', '').strip()

    if not stock_input:
        return jsonify({'error': '请输入股票代码或公司名称'}), 400

    # 使用AKShare获取股票信息
    result = get_stock_info_from_akshare(stock_input)

    if result['success']:
        return jsonify({
            'success': True,
            'stock_code': result['code'],
            'stock_name': result['name']
        })
    else:
        return jsonify({'error': result['message']}), 404


@stock_bp.route('/valuation', methods=['POST'])
@token_required
def calculate_valuation():
    """计算股票DCF估值"""
    data = request.get_json()

    # 获取参数
    stock_code = data.get('stock_code', '').strip()
    discount_rate = float(data.get('discount_rate', 0.1))
    stage1_years = int(data.get('stage1_years', 5))
    stage1_growth = float(data.get('stage1_growth', 0.1))
    stage2_years = int(data.get('stage2_years', 5))
    stage2_growth = float(data.get('stage2_growth', 0.05))
    stage3_years = int(data.get('stage3_years', 0))
    stage3_growth = float(data.get('stage3_growth', 0.02))

    if not stock_code:
        return jsonify({'error': '请提供股票代码'}), 400

    try:
        # 先尝试从数据库获取财务数据，如果没有则生成fake数据
        financial_result = get_financial_data_mixed(stock_code)
        if not financial_result['success']:
            return jsonify({'error': financial_result['message']}), 400

        financial_data = financial_result['data']
        if len(financial_data) == 0:
            return jsonify({'error': '没有找到财务数据'}), 400

        # 计算平均自由现金流
        dcf_model = DCFValuation()
        fcf_list = []

        for year_data in financial_data:
            # 计算营运资本变动（简化处理，使用流动资产-流动负债的变化）
            working_capital = year_data['current_assets'] - year_data['current_liabilities']
            # 为简化，假设营运资本变动为当年营运资本的10%
            change_wc = working_capital * 0.1

            fcf = dcf_model.fcf_by_net_income(
                year_data['net_income'],
                year_data['interest_expense'],
                0,  # 摊销（包含在折旧中）
                year_data['depreciation'],
                change_wc,
                abs(year_data['capex'])  # 资本支出取绝对值
            )
            fcf_list.append(fcf)

        # 计算平均FCF
        avg_fcf = sum(fcf_list) / len(fcf_list) if fcf_list else 0

        # 计算企业价值
        enterprise_value = dcf_model.common_dcf(
            avg_fcf, discount_rate, stage1_years, stage1_growth,
            stage2_years, stage2_growth, stage3_years, stage3_growth
        )

        # 获取股本信息（从AKShare获取）
        shares_result = get_stock_shares_from_akshare(stock_code)
        if not shares_result['success']:
            return jsonify({'error': shares_result['message']}), 400

        total_shares = shares_result['total_shares']

        # 计算每股价值
        price_per_share = enterprise_value / total_shares if total_shares > 0 else 0

        # 获取当前市场价格进行比较
        try:
            print(f"正在获取股票 {stock_code} 的当前市场价格...")
            current_price_data = ak.stock_zh_a_spot_em()
            if current_price_data is not None and not current_price_data.empty:
                current_stock = current_price_data[current_price_data['代码'] == stock_code]
                if not current_stock.empty:
                    current_price = float(current_stock.iloc[0]['最新价'])
                    print(f"获取到当前市场价格: ¥{current_price}")
                else:
                    print(f"未找到股票代码 {stock_code} 的市场数据，使用估算价格")
                    current_price = 10.0  # 估算价格
            else:
                print("市场数据API返回空，使用估算价格")
                current_price = 10.0  # 估算价格
        except Exception as e:
            print(f"获取市场价格失败: {e}，使用估算价格")
            current_price = 10.0  # 估算价格

        # 检查是否有备注信息（使用了估算数据）
        note = financial_result.get('note', '')

        result = {
            'success': True,
            'valuation_result': {
                'stock_code': stock_code,
                'avg_fcf': round(avg_fcf / 100000000, 2),  # 转换为亿元
                'enterprise_value': round(enterprise_value / 100000000, 2),  # 转换为亿元
                'total_shares': round(total_shares / 100000000, 2),  # 转换为亿股
                'price_per_share': round(price_per_share, 2),
                'current_market_price': round(current_price, 2),
                'valuation_ratio': round((price_per_share / current_price) if current_price > 0 else 0, 2),
                'financial_years': len(financial_data),
                'fcf_history': [round(fcf / 100000000, 2) for fcf in fcf_list],  # 历年FCF（亿元）
                'parameters': {
                    'discount_rate': discount_rate,
                    'stage1_years': stage1_years,
                    'stage1_growth': stage1_growth,
                    'stage2_years': stage2_years,
                    'stage2_growth': stage2_growth,
                    'stage3_years': stage3_years,
                    'stage3_growth': stage3_growth
                }
            }
        }

        # 如果使用了估算数据，添加警告信息
        if note:
            result['valuation_result']['warning'] = note

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'计算估值时出错: {str(e)}'}), 500


@stock_bp.route('/market-data/<stock_code>', methods=['GET'])
@token_required
def get_market_data(stock_code):
    """获取股票市场数据"""
    try:
        # 获取实时价格
        current_price_data = ak.stock_zh_a_spot_em()
        current_stock = current_price_data[current_price_data['代码'] == stock_code]

        if current_stock.empty:
            return jsonify({'error': '未找到股票市场数据'}), 404

        stock_data = current_stock.iloc[0]

        # 获取基本信息
        stock_info = ak.stock_individual_info_em(symbol=stock_code)
        pe_ratio = 0
        pb_ratio = 0

        if not stock_info.empty:
            pe_row = stock_info[stock_info['item'] == '市盈率-动态']
            pb_row = stock_info[stock_info['item'] == '市净率']

            if not pe_row.empty:
                try:
                    pe_ratio = float(pe_row.iloc[0]['value'])
                except:
                    pe_ratio = 0

            if not pb_row.empty:
                try:
                    pb_ratio = float(pb_row.iloc[0]['value'])
                except:
                    pb_ratio = 0

        return jsonify({
            'success': True,
            'market_data': {
                'current_price': float(stock_data['最新价']),
                'change_percent': float(stock_data['涨跌幅']),
                'volume': float(stock_data['成交量']),
                'turnover': float(stock_data['成交额']),
                'high': float(stock_data['最高']),
                'low': float(stock_data['最低']),
                'open': float(stock_data['今开']),
                'yesterday_close': float(stock_data['昨收']),
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio
            }
        })

    except Exception as e:
        return jsonify({'error': f'获取市场数据失败: {str(e)}'}), 500
