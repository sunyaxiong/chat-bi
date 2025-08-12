-- 生成更多测试数据的SQL脚本
-- 用于扩充电站数据，便于ChatBI测试各种查询场景

-- 生成更多日发电量数据（过去6个月）
DELIMITER //
CREATE PROCEDURE GenerateDailyData()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_station_id INT;
    DECLARE v_generator_id INT;
    DECLARE v_capacity DECIMAL(8,2);
    DECLARE v_date DATE;
    DECLARE v_power DECIMAL(12,2);
    DECLARE v_hours DECIMAL(5,2);
    DECLARE v_load_factor DECIMAL(5,2);
    
    DECLARE cur CURSOR FOR 
        SELECT g.station_id, g.id, g.unit_capacity 
        FROM generators g 
        JOIN power_stations ps ON g.station_id = ps.id 
        WHERE ps.status = '运行';
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    SET v_date = DATE_SUB(CURDATE(), INTERVAL 180 DAY);
    
    WHILE v_date <= CURDATE() DO
        OPEN cur;
        read_loop: LOOP
            FETCH cur INTO v_station_id, v_generator_id, v_capacity;
            IF done THEN
                LEAVE read_loop;
            END IF;
            
            -- 生成随机发电数据
            SET v_hours = 20 + (RAND() * 4); -- 20-24小时运行
            SET v_load_factor = 70 + (RAND() * 25); -- 70-95%负荷率
            SET v_power = v_capacity * v_hours * (v_load_factor / 100);
            
            INSERT IGNORE INTO daily_generation 
            (station_id, generator_id, generation_date, power_generation, operating_hours, load_factor)
            VALUES (v_station_id, v_generator_id, v_date, v_power, v_hours, v_load_factor);
            
        END LOOP;
        CLOSE cur;
        SET done = FALSE;
        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END//
DELIMITER ;

-- 执行存储过程生成数据
CALL GenerateDailyData();

-- 生成月度统计数据
INSERT INTO monthly_statistics (station_id, year, month, total_generation, avg_load_factor, operating_days, maintenance_hours, revenue)
SELECT 
    station_id,
    YEAR(generation_date) as year,
    MONTH(generation_date) as month,
    SUM(power_generation) as total_generation,
    AVG(load_factor) as avg_load_factor,
    COUNT(DISTINCT generation_date) as operating_days,
    FLOOR(RAND() * 100) as maintenance_hours,
    SUM(power_generation) * 0.6 as revenue
FROM daily_generation 
WHERE generation_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY station_id, YEAR(generation_date), MONTH(generation_date)
ON DUPLICATE KEY UPDATE
    total_generation = VALUES(total_generation),
    avg_load_factor = VALUES(avg_load_factor),
    operating_days = VALUES(operating_days);

-- 添加更多维护记录
INSERT INTO maintenance_records (station_id, generator_id, maintenance_type, start_date, end_date, duration_hours, cost, description, status) VALUES
(1, 1, '日常维护', '2023-12-05', '2023-12-05', 6.0, 15000.00, '定期巡检维护', '已完成'),
(1, 2, '计划检修', '2023-11-15', '2023-11-18', 72.0, 200000.00, '汽轮机大修', '已完成'),
(2, 3, '故障检修', '2023-12-20', '2023-12-22', 36.0, 120000.00, '发电机绕组维修', '已完成'),
(2, 4, '日常维护', '2023-12-10', '2023-12-10', 8.0, 30000.00, '水轮机检查', '已完成'),
(3, 5, '计划检修', '2023-11-01', '2023-11-03', 48.0, 60000.00, '风机年度检修', '已完成'),
(3, 6, '故障检修', '2023-12-15', '2023-12-16', 24.0, 40000.00, '变桨系统故障', '已完成'),
(4, 7, '日常维护', '2023-12-01', '2023-12-01', 4.0, 8000.00, '逆变器检查', '已完成'),
(5, 8, '计划检修', '2023-10-01', '2023-10-15', 360.0, 5000000.00, '核反应堆换料大修', '已完成');

-- 添加更多燃料消耗数据
INSERT INTO fuel_consumption (station_id, consumption_date, fuel_type, consumption_amount, unit_price, total_cost, supplier) VALUES
-- 华能北京热电厂过去3个月数据
(1, '2023-12-01', '煤炭', 1200.00, 680.00, 816000.00, '山西煤业集团'),
(1, '2023-12-15', '煤炭', 1350.00, 690.00, 931500.00, '陕西煤业'),
(1, '2023-11-01', '煤炭', 1180.00, 675.00, 796500.00, '山西煤业集团'),
(1, '2023-11-15', '煤炭', 1280.00, 685.00, 876800.00, '内蒙古煤业'),
-- 华电上海电厂数据
(6, '2023-12-01', '天然气', 800.00, 3150.00, 2520000.00, '中石化'),
(6, '2023-12-15', '天然气', 950.00, 3200.00, 3040000.00, '中石油'),
(6, '2023-11-01', '天然气', 750.00, 3100.00, 2325000.00, '中海油'),
(6, '2023-11-15', '天然气', 880.00, 3180.00, 2798400.00, '中石化');

-- 创建一些常用的视图，便于ChatBI查询
CREATE VIEW station_summary AS
SELECT 
    ps.station_name,
    ps.station_type,
    ps.capacity,
    ps.location,
    ps.province,
    ps.city,
    ps.status,
    COUNT(g.id) as generator_count,
    SUM(g.unit_capacity) as total_unit_capacity
FROM power_stations ps
LEFT JOIN generators g ON ps.id = g.station_id
GROUP BY ps.id;

CREATE VIEW monthly_generation_summary AS
SELECT 
    ps.station_name,
    ps.station_type,
    ps.province,
    ms.year,
    ms.month,
    ms.total_generation,
    ms.avg_load_factor,
    ms.operating_days,
    ms.revenue,
    CONCAT(ms.year, '-', LPAD(ms.month, 2, '0')) as year_month
FROM monthly_statistics ms
JOIN power_stations ps ON ms.station_id = ps.id;

CREATE VIEW daily_generation_summary AS
SELECT 
    ps.station_name,
    ps.station_type,
    ps.province,
    g.generator_name,
    dg.generation_date,
    dg.power_generation,
    dg.operating_hours,
    dg.load_factor,
    YEAR(dg.generation_date) as year,
    MONTH(dg.generation_date) as month,
    DAY(dg.generation_date) as day
FROM daily_generation dg
JOIN power_stations ps ON dg.station_id = ps.id
JOIN generators g ON dg.generator_id = g.id;

-- 删除临时存储过程
DROP PROCEDURE GenerateDailyData;