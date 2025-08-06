-- 电站数据库表结构和测试数据
-- 适用于ChatBI项目的电站管理系统

-- 1. 电站基础信息表
CREATE TABLE power_stations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_code VARCHAR(50) UNIQUE NOT NULL COMMENT '电站编码',
    station_name VARCHAR(100) NOT NULL COMMENT '电站名称',
    station_type ENUM('火电', '水电', '风电', '光伏', '核电') NOT NULL COMMENT '电站类型',
    capacity DECIMAL(10,2) NOT NULL COMMENT '装机容量(MW)',
    location VARCHAR(100) NOT NULL COMMENT '所在地区',
    province VARCHAR(50) NOT NULL COMMENT '省份',
    city VARCHAR(50) NOT NULL COMMENT '城市',
    commissioning_date DATE NOT NULL COMMENT '投产日期',
    status ENUM('运行', '检修', '停机', '建设中') DEFAULT '运行' COMMENT '运行状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. 发电机组信息表
CREATE TABLE generators (
    id INT PRIMARY KEY AUTO_INCREMENT,
    generator_code VARCHAR(50) UNIQUE NOT NULL COMMENT '机组编码',
    generator_name VARCHAR(100) NOT NULL COMMENT '机组名称',
    station_id INT NOT NULL COMMENT '所属电站ID',
    unit_capacity DECIMAL(8,2) NOT NULL COMMENT '单机容量(MW)',
    manufacturer VARCHAR(100) COMMENT '制造商',
    model VARCHAR(100) COMMENT '型号',
    install_date DATE COMMENT '安装日期',
    status ENUM('运行', '检修', '停机', '备用') DEFAULT '运行' COMMENT '机组状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES power_stations(id)
);

-- 3. 日发电量数据表
CREATE TABLE daily_generation (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_id INT NOT NULL COMMENT '电站ID',
    generator_id INT COMMENT '机组ID',
    generation_date DATE NOT NULL COMMENT '发电日期',
    power_generation DECIMAL(12,2) NOT NULL COMMENT '发电量(MWh)',
    operating_hours DECIMAL(5,2) DEFAULT 0 COMMENT '运行小时数',
    load_factor DECIMAL(5,2) DEFAULT 0 COMMENT '负荷率(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES power_stations(id),
    FOREIGN KEY (generator_id) REFERENCES generators(id),
    UNIQUE KEY unique_daily_gen (station_id, generator_id, generation_date)
);

-- 4. 月度统计数据表
CREATE TABLE monthly_statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_id INT NOT NULL COMMENT '电站ID',
    year INT NOT NULL COMMENT '年份',
    month INT NOT NULL COMMENT '月份',
    total_generation DECIMAL(15,2) NOT NULL COMMENT '月发电量(MWh)',
    avg_load_factor DECIMAL(5,2) DEFAULT 0 COMMENT '平均负荷率(%)',
    operating_days INT DEFAULT 0 COMMENT '运行天数',
    maintenance_hours DECIMAL(8,2) DEFAULT 0 COMMENT '检修小时数',
    revenue DECIMAL(15,2) DEFAULT 0 COMMENT '发电收入(万元)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES power_stations(id),
    UNIQUE KEY unique_monthly_stat (station_id, year, month)
);

-- 5. 设备维护记录表
CREATE TABLE maintenance_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_id INT NOT NULL COMMENT '电站ID',
    generator_id INT COMMENT '机组ID',
    maintenance_type ENUM('计划检修', '故障检修', '日常维护', '大修') NOT NULL COMMENT '维护类型',
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE COMMENT '结束日期',
    duration_hours DECIMAL(8,2) COMMENT '维护时长(小时)',
    cost DECIMAL(12,2) DEFAULT 0 COMMENT '维护成本(元)',
    description TEXT COMMENT '维护描述',
    status ENUM('计划中', '进行中', '已完成', '已取消') DEFAULT '计划中' COMMENT '维护状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES power_stations(id),
    FOREIGN KEY (generator_id) REFERENCES generators(id)
);

-- 6. 燃料消耗记录表（主要用于火电站）
CREATE TABLE fuel_consumption (
    id INT PRIMARY KEY AUTO_INCREMENT,
    station_id INT NOT NULL COMMENT '电站ID',
    consumption_date DATE NOT NULL COMMENT '消耗日期',
    fuel_type ENUM('煤炭', '天然气', '柴油', '重油') NOT NULL COMMENT '燃料类型',
    consumption_amount DECIMAL(12,2) NOT NULL COMMENT '消耗量(吨)',
    unit_price DECIMAL(8,2) NOT NULL COMMENT '单价(元/吨)',
    total_cost DECIMAL(15,2) NOT NULL COMMENT '总成本(元)',
    supplier VARCHAR(100) COMMENT '供应商',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES power_stations(id)
);

-- 插入电站基础数据
INSERT INTO power_stations (station_code, station_name, station_type, capacity, location, province, city, commissioning_date, status) VALUES
('PS001', '华能北京热电厂', '火电', 1200.00, '北京市朝阳区', '北京', '北京', '2010-05-15', '运行'),
('PS002', '三峡水电站', '水电', 22500.00, '湖北省宜昌市', '湖北', '宜昌', '2003-07-10', '运行'),
('PS003', '大唐风电场', '风电', 300.00, '内蒙古呼和浩特市', '内蒙古', '呼和浩特', '2015-09-20', '运行'),
('PS004', '阳光光伏电站', '光伏', 150.00, '青海省西宁市', '青海', '西宁', '2018-03-12', '运行'),
('PS005', '秦山核电站', '核电', 3000.00, '浙江省嘉兴市', '浙江', '嘉兴', '1991-12-15', '运行'),
('PS006', '华电上海电厂', '火电', 800.00, '上海市浦东新区', '上海', '上海', '2008-11-30', '检修'),
('PS007', '龙滩水电站', '水电', 5400.00, '广西河池市', '广西', '河池', '2009-01-18', '运行'),
('PS008', '金风风电场', '风电', 200.00, '新疆乌鲁木齐市', '新疆', '乌鲁木齐', '2016-06-25', '运行');

-- 插入发电机组数据
INSERT INTO generators (generator_code, generator_name, station_id, unit_capacity, manufacturer, model, install_date, status) VALUES
('GEN001-1', '华能北京1号机组', 1, 600.00, '东方电气', 'DEC-600', '2010-03-01', '运行'),
('GEN001-2', '华能北京2号机组', 1, 600.00, '东方电气', 'DEC-600', '2010-04-15', '运行'),
('GEN002-1', '三峡1号机组', 2, 700.00, '哈尔滨电机', 'HEC-700', '2003-06-01', '运行'),
('GEN002-2', '三峡2号机组', 2, 700.00, '哈尔滨电机', 'HEC-700', '2003-06-15', '运行'),
('GEN003-1', '大唐风机1', 3, 2.50, '金风科技', 'GW2.5-121', '2015-08-01', '运行'),
('GEN003-2', '大唐风机2', 3, 2.50, '金风科技', 'GW2.5-121', '2015-08-15', '运行'),
('GEN004-1', '阳光逆变器1', 4, 1.00, '阳光电源', 'SG1000MX', '2018-02-01', '运行'),
('GEN005-1', '秦山反应堆1', 5, 1000.00, '中核集团', 'CNP-1000', '1991-11-01', '运行');

-- 插入日发电量数据（最近30天）
INSERT INTO daily_generation (station_id, generator_id, generation_date, power_generation, operating_hours, load_factor) VALUES
-- 华能北京热电厂数据
(1, 1, '2024-01-01', 12500.50, 24.0, 86.8),
(1, 1, '2024-01-02', 13200.75, 24.0, 91.7),
(1, 1, '2024-01-03', 11800.25, 22.5, 87.4),
(1, 2, '2024-01-01', 12800.30, 24.0, 88.9),
(1, 2, '2024-01-02', 13500.60, 24.0, 93.8),
(1, 2, '2024-01-03', 12100.45, 23.0, 87.8),
-- 三峡水电站数据
(2, 3, '2024-01-01', 15600.80, 24.0, 92.9),
(2, 3, '2024-01-02', 16200.90, 24.0, 96.4),
(2, 3, '2024-01-03', 14800.70, 24.0, 88.1),
(2, 4, '2024-01-01', 15800.60, 24.0, 94.0),
(2, 4, '2024-01-02', 16500.40, 24.0, 98.2),
(2, 4, '2024-01-03', 15200.30, 24.0, 90.5),
-- 风电场数据
(3, 5, '2024-01-01', 45.60, 18.5, 75.2),
(3, 5, '2024-01-02', 52.30, 20.2, 85.6),
(3, 5, '2024-01-03', 38.90, 15.8, 64.3),
-- 光伏电站数据
(4, 7, '2024-01-01', 8.50, 8.5, 85.0),
(4, 7, '2024-01-02', 9.20, 9.2, 92.0),
(4, 7, '2024-01-03', 7.80, 7.8, 78.0);

-- 插入月度统计数据
INSERT INTO monthly_statistics (station_id, year, month, total_generation, avg_load_factor, operating_days, maintenance_hours, revenue) VALUES
(1, 2023, 12, 780000.50, 89.5, 31, 48.0, 4680.00),
(1, 2024, 1, 820000.75, 91.2, 31, 24.0, 4920.00),
(2, 2023, 12, 1250000.80, 94.2, 31, 0.0, 6250.00),
(2, 2024, 1, 1300000.60, 95.8, 31, 0.0, 6500.00),
(3, 2023, 12, 18500.30, 72.8, 28, 72.0, 925.00),
(3, 2024, 1, 19800.45, 76.5, 29, 48.0, 990.00),
(4, 2023, 12, 3200.60, 80.5, 25, 24.0, 320.00),
(4, 2024, 1, 3800.80, 85.2, 28, 12.0, 380.00);

-- 插入维护记录数据
INSERT INTO maintenance_records (station_id, generator_id, maintenance_type, start_date, end_date, duration_hours, cost, description, status) VALUES
(1, 1, '计划检修', '2024-01-15', '2024-01-17', 48.0, 150000.00, '锅炉年度大修', '已完成'),
(1, 2, '故障检修', '2024-01-20', '2024-01-21', 18.0, 80000.00, '汽轮机轴承更换', '已完成'),
(2, 3, '日常维护', '2024-01-10', '2024-01-10', 8.0, 25000.00, '水轮机叶片检查', '已完成'),
(3, 5, '计划检修', '2024-01-25', '2024-01-27', 36.0, 45000.00, '风机齿轮箱维护', '进行中'),
(4, 7, '日常维护', '2024-01-12', '2024-01-12', 4.0, 8000.00, '光伏板清洁', '已完成');

-- 插入燃料消耗数据（火电站）
INSERT INTO fuel_consumption (station_id, consumption_date, fuel_type, consumption_amount, unit_price, total_cost, supplier) VALUES
(1, '2024-01-01', '煤炭', 1250.50, 680.00, 850340.00, '山西煤业集团'),
(1, '2024-01-02', '煤炭', 1320.75, 680.00, 898110.00, '山西煤业集团'),
(1, '2024-01-03', '煤炭', 1180.25, 680.00, 802570.00, '山西煤业集团'),
(6, '2024-01-01', '天然气', 850.30, 3200.00, 2720960.00, '中石油'),
(6, '2024-01-02', '天然气', 920.60, 3200.00, 2945920.00, '中石油'),
(6, '2024-01-03', '天然气', 780.45, 3200.00, 2497440.00, '中石油');

-- 创建索引以提高查询性能
CREATE INDEX idx_daily_gen_date ON daily_generation(generation_date);
CREATE INDEX idx_daily_gen_station ON daily_generation(station_id);
CREATE INDEX idx_monthly_stat_year_month ON monthly_statistics(year, month);
CREATE INDEX idx_maintenance_date ON maintenance_records(start_date);
CREATE INDEX idx_fuel_date ON fuel_consumption(consumption_date);