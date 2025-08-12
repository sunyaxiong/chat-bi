-- 创建表: dwd_sungrow.dwd_pub_user_org_d
-- 描述: 用户和所属组织的相关信息，是一张事务事实表
DROP TABLE IF EXISTS `dwd_sungrow.dwd_pub_user_org_d`;
CREATE TABLE `dwd_sungrow.dwd_pub_user_org_d` (
  `user_account` VARCHAR(255) COMMENT '用户账号',
  `user_name` VARCHAR(255) COMMENT '用户名称',
  `user_type` VARCHAR(255) COMMENT '用户类型，值*MUST*只能是这些值中的一个：‘业主’和‘安装商’',
  `crt_date` TIMESTAMP COMMENT '用户创建时间',
  `valid_flag` INT COMMENT '有效标识，值*MUST*只能是这一个：‘1’代表‘有效’',
  `login_first_date` TIMESTAMP COMMENT '用户首次登录时间',
  `login_last_date` TIMESTAMP COMMENT '用户最后一次登录时间',
  `user_country` VARCHAR(255) COMMENT '国家名称，值*MUST*是中文的国家名，例如：‘中国’，‘中国香港’，‘中国澳门’，‘中国台湾’，‘美国’，‘俄罗斯’',
  `org_name` VARCHAR(255) COMMENT '组织名称',
  `is_master_org` INT COMMENT '是否是该用户的主组织，值*MUST*只能是这些值中的一个： ‘0’代表‘不是’， ‘1’代表‘是’',
  `is_home_pv` VARCHAR(255) COMMENT '判断是否是家庭光伏，值*MUST*只能是这些值中的一个：\'是\',\'否\'',
  `login_times` INT COMMENT '用户登录次数',
  `login_web_times` INT COMMENT '用户登录web次数',
  `login_app_times` INT COMMENT '用户登录app次数',
  `pt` VARCHAR(255) COMMENT '分区字段（yyyy-MM-dd）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户和所属组织的相关信息，是一张事务事实表';

-- 创建表: dwd_sungrow.dwd_user_sys_user_version_info_d
-- 描述: 用户使用应用版本的信息，是一张事务事实表
DROP TABLE IF EXISTS `dwd_sungrow.dwd_user_sys_user_version_info_d`;
CREATE TABLE `dwd_sungrow.dwd_user_sys_user_version_info_d` (
  `version_name` VARCHAR(255) COMMENT '应用版本名称',
  `version_code` VARCHAR(255) COMMENT '应用版本号,版本号',
  `update_time` TIMESTAMP COMMENT '用户在不同产品类型的登录时间',
  `pt` VARCHAR(255) COMMENT '分区字段（yyyy-MM-dd）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户使用应用版本的信息，是一张事务事实表';
