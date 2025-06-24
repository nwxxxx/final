-- 创建财务数据表
CREATE TABLE IF NOT EXISTS financial_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    company_name VARCHAR(100) NOT NULL COMMENT '公司名称',
    report_year YEAR NOT NULL COMMENT '报告年份',
    report_date DATE NOT NULL COMMENT '报告日期',
    net_income DECIMAL(15,2) DEFAULT 0 COMMENT '净利润（元）',
    interest_expense DECIMAL(15,2) DEFAULT 0 COMMENT '利息支出（元）',
    depreciation DECIMAL(15,2) DEFAULT 0 COMMENT '折旧与摊销（元）',
    capex DECIMAL(15,2) DEFAULT 0 COMMENT '资本支出（元）',
    current_assets DECIMAL(15,2) DEFAULT 0 COMMENT '流动资产（元）',
    current_liabilities DECIMAL(15,2) DEFAULT 0 COMMENT '流动负债（元）',
    total_shares BIGINT DEFAULT 0 COMMENT '总股本（股）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_stock_year (stock_code, report_year),
    INDEX idx_stock_code (stock_code),
    INDEX idx_company_name (company_name),
    INDEX idx_report_year (report_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票财务数据表';

-- 插入示例数据（平安银行 000001）
INSERT INTO financial_data (stock_code, company_name, report_year, report_date, net_income, interest_expense, depreciation, capex, current_assets, current_liabilities, total_shares) VALUES
('000001', '平安银行', 2024, '2024-12-31', 43200000000, 16000000000, 9000000000, 12800000000, 380000000000, 300000000000, 19405918198),
('000001', '平安银行', 2023, '2023-12-31', 40500000000, 15000000000, 8500000000, 12000000000, 350000000000, 280000000000, 19405918198),
('000001', '平安银行', 2022, '2022-12-31', 37800000000, 14200000000, 8200000000, 11500000000, 320000000000, 260000000000, 19405918198);

-- 插入示例数据（万科A 000002）
INSERT INTO financial_data (stock_code, company_name, report_year, report_date, net_income, interest_expense, depreciation, capex, current_assets, current_liabilities, total_shares) VALUES
('000002', '万科A', 2024, '2024-12-31', 24000000000, 9000000000, 4800000000, 7000000000, 270000000000, 190000000000, 11039152459),
('000002', '万科A', 2023, '2023-12-31', 22500000000, 8500000000, 4500000000, 6500000000, 250000000000, 180000000000, 11039152459),
('000002', '万科A', 2022, '2022-12-31', 21200000000, 8200000000, 4200000000, 6200000000, 230000000000, 170000000000, 11039152459);

-- 插入示例数据（中国平安 601318）
INSERT INTO financial_data (stock_code, company_name, report_year, report_date, net_income, interest_expense, depreciation, capex, current_assets, current_liabilities, total_shares) VALUES
('601318', '中国平安', 2024, '2024-12-31', 115000000000, 26500000000, 16000000000, 19000000000, 850000000000, 680000000000, 18280443217),
('601318', '中国平安', 2023, '2023-12-31', 108500000000, 25000000000, 15000000000, 18000000000, 800000000000, 650000000000, 18280443217),
('601318', '中国平安', 2022, '2022-12-31', 102300000000, 24000000000, 14500000000, 17200000000, 750000000000, 620000000000, 18280443217);

-- 插入示例数据（招商银行 600036）
INSERT INTO financial_data (stock_code, company_name, report_year, report_date, net_income, interest_expense, depreciation, capex, current_assets, current_liabilities, total_shares) VALUES
('600036', '招商银行', 2024, '2024-12-31', 140000000000, 48000000000, 13000000000, 16000000000, 950000000000, 780000000000, 25218911112),
('600036', '招商银行', 2023, '2023-12-31', 132500000000, 45000000000, 12000000000, 15000000000, 900000000000, 750000000000, 25218911112),
('600036', '招商银行', 2022, '2022-12-31', 125800000000, 42000000000, 11500000000, 14200000000, 850000000000, 720000000000, 25218911112);

-- 插入示例数据（贵州茅台 600519）
INSERT INTO financial_data (stock_code, company_name, report_year, report_date, net_income, interest_expense, depreciation, capex, current_assets, current_liabilities, total_shares) VALUES
('600519', '贵州茅台', 2024, '2024-12-31', 67000000000, 160000000, 3000000000, 9000000000, 102000000000, 27000000000, 1256197800),
('600519', '贵州茅台', 2023, '2023-12-31', 62750000000, 150000000, 2800000000, 8500000000, 95000000000, 25000000000, 1256197800),
('600519', '贵州茅台', 2022, '2022-12-31', 58120000000, 140000000, 2650000000, 8200000000, 88000000000, 23000000000, 1256197800); 