-- 创建表: dwd_sungrow.dwd_dev_power_device_fault_details_d
-- 描述: 包含了电站、电站关联的设备对应的故障信息
DROP TABLE IF EXISTS `dwd_sungrow.dwd_dev_power_device_fault_details_d`;
CREATE TABLE `dwd_sungrow.dwd_dev_power_device_fault_details_d` (
  `site_name` VARCHAR(255) COMMENT '站点名称，值*MUST*只能是这些值中的一个：‘中国站’，‘国际站’，‘欧洲站’，‘澳洲站’',
  `ps_id` VARCHAR(255) COMMENT '电站id,电站的唯一ID',
  `fault_date` VARCHAR(255) COMMENT '故障日期',
  `sn` VARCHAR(255) COMMENT 'sn',
  `device_model` VARCHAR(255) COMMENT '设备型号',
  `big_fault_type_name` VARCHAR(255) COMMENT '大故障码名称',
  `small_fault_type_name` VARCHAR(255) COMMENT '小故障码名称',
  `ps_name` VARCHAR(255) COMMENT '电站名称',
  `pt` VARCHAR(255) COMMENT '分区字段（yyyy-MM-dd）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='包含了电站、电站关联的设备对应的故障信息';

-- 创建表: dwd_sungrow.dwd_pub_ps_dev_power_station_d
-- 描述: 包含了电站，电站关联的设备信息，是一张事务事实表
DROP TABLE IF EXISTS `dwd_sungrow.dwd_pub_ps_dev_power_station_d`;
CREATE TABLE `dwd_sungrow.dwd_pub_ps_dev_power_station_d` (
  `ps_id` INT COMMENT '电站id,电站的唯一ID',
  `ps_name` VARCHAR(255) COMMENT '电站名称/电站名',
  `ps_location` VARCHAR(255) COMMENT '电站位置，电站地址',
  `longitude` DECIMAL(10,2) COMMENT '经度-WGS84格式',
  `latitude` DECIMAL(10,2) COMMENT '维度-WGS84格式',
  `valid_flag` INT COMMENT '有效标识，值*MUST*只能是这一个：‘1’代表‘有效’',
  `ps_type` INT COMMENT '电站类型，值*MUST*只能是这些值中的一个：‘1’代表‘地面光伏电站’，‘3’代表‘分布式光伏’，‘4’代表‘户用光伏’，‘5’代表‘户用储能’，‘6’代表‘村级电站’，‘7’代表‘分布式储能’，‘8’代表‘扶贫电站’，‘9’代表‘风能电站’，‘10’代表‘地面储能电站’，‘11’代表‘地面光储电站’，‘12’代表‘工商业EMS’。',
  `recore_create_time` TIMESTAMP COMMENT '建站时间，电站创建时间',
  `access_type` INT COMMENT '接入方式，值*MUST*只能是这些值中的一个：‘0’代表‘Insight Pro上传’，‘1’代表‘Logger上传’，‘2’代表‘GPRS上传’，‘3’代表‘第三方上传’，‘4’代表‘WIFI上传’，‘5’代表‘Insight V4上传’，‘6’代表‘EMS上传’，‘7’代表‘SCADA上传’。',
  `is_odm_ps` INT COMMENT '是否是ODM电站，值*MUST*只能是这些值中的一个：‘0’代表‘不是’，‘1’代表‘是’。',
  `ps_country_name` VARCHAR(255) COMMENT '国家名称，值*MUST*是中文的国家名，例如：‘中国’，‘中国香港’，‘中国澳门’，‘中国台湾’，‘美国’，‘俄罗斯’等。',
  `ps_province_name` VARCHAR(255) COMMENT '省份名称，值*MUST*是中文的省份名称，例如：‘江苏省’，‘山东省’，‘河南省’，‘北京市’，‘天津市’，‘上海市’，‘宁夏回族自治区’，‘香港特别行政区’，‘广西壮族自治区’，‘西藏自治区’，‘重庆市’。',
  `ps_city_name` VARCHAR(255) COMMENT '城市名称，值*MUST*是中文的省份名称，例如：‘洛阳市’，‘南京市’',
  `ps_district_name` VARCHAR(255) COMMENT '区名称，值*MUST*是中文的区名称，例如：‘栾川县’，‘江宁区’。',
  `dev_model_id` INT COMMENT '设备型号ID',
  `dev_model_name` VARCHAR(255) COMMENT '设备型号',
  `dev_type_id` INT COMMENT '设备类型ID，值*MUST*只能是像‘1’这类数字，例如：‘1’，‘9’，‘22’，‘14’，‘5’等。',
  `dev_type_name` VARCHAR(255) COMMENT '设备类型，值*MUST*只能是像‘逆变器’的这类中文名称，例如：‘’逆变器，‘储能逆变器’，‘通信装置’，‘通讯模块’等。',
  `dev_name` VARCHAR(255) COMMENT '设备名称',
  `is_virtual_unit` INT COMMENT '虚拟设备标识，值*MUST*只能是这些值中的一个： ‘1’代表‘虚拟设备’， ‘0’代表‘物理设备’',
  `dev_create_date` TIMESTAMP COMMENT '设备创建时间',
  `dev_uuid` INT COMMENT '设备uuid',
  `dev_pro_sn` VARCHAR(255) COMMENT '设备SN号，序列号',
  `dev_conn_sn` VARCHAR(255) COMMENT '通讯设备sn',
  `dev_conn_model` VARCHAR(255) COMMENT '通讯设备机型',
  `total_installed_power` DECIMAL(10,2) COMMENT '设备总装机功率，设备装机总容量，设备装机功率，设备装机容量',
  `dev_bu_type` VARCHAR(255) COMMENT '设备归属产品线，值*MUST*只能是这些值中的一个：‘户用’，‘储能’，‘地面’，‘充电’，‘未定义’',
  `telemetry_point_num` INT COMMENT '遥测测点数',
  `telesignal_point_num` INT COMMENT '遥信测点数',
  `property_point_num` INT COMMENT '属性测点数',
  `total_point_num` INT COMMENT '单设备总测点数，设备测点数',
  `ps_owner_user_account` VARCHAR(255) COMMENT '电站业主账号',
  `ps_owner_user_name` VARCHAR(255) COMMENT '电站业主名称',
  `country_reagion` VARCHAR(255) COMMENT '国家所属大区，值*MUST*只能是这些值中的一个：‘中国大区’，‘欧洲大区’，‘美洲大区’，‘澳洲大区’，‘中东大区’，‘亚太大区’，‘南部非洲区’，‘未定义’）',
  `version1` VARCHAR(255) COMMENT '软件版本，版本，固件随机版本号1',
  `version2` VARCHAR(255) COMMENT '软件版本，版本，固件随机版本号2',
  `version3` VARCHAR(255) COMMENT '软件版本，版本，固件随机版本号3',
  `version4` VARCHAR(255) COMMENT '软件版本，版本，固件随机版本号4',
  `version5` VARCHAR(255) COMMENT '软件版本，版本，固件随机版本号5',
  `up_uuid` VARCHAR(255) COMMENT '上级uuid',
  `dev_status` VARCHAR(255) COMMENT '在离线设备状态，值*MUST*只能是这些值中的一个：‘0’代表‘离线’，‘1’代表‘在线’',
  `pt` VARCHAR(255) COMMENT '分区字段（yyyy-MM-dd）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='包含了电站，电站关联的设备信息，是一张事务事实表';
