CREATE DATABASE IF NOT EXISTS ai_api_test_platform
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ai_test'@'%' IDENTIFIED BY 'ai_test';
GRANT ALL PRIVILEGES ON ai_api_test_platform.* TO 'ai_test'@'%';
FLUSH PRIVILEGES;

USE ai_api_test_platform;

CREATE TABLE IF NOT EXISTS project (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  name VARCHAR(128) NOT NULL COMMENT '项目名称',
  description TEXT NULL COMMENT '项目描述',
  owner_name VARCHAR(128) NULL COMMENT '项目负责人',
  status VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '项目状态',
  config JSON NULL COMMENT '项目配置',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_project_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';

CREATE TABLE IF NOT EXISTS environment (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  name VARCHAR(128) NOT NULL COMMENT '环境名称',
  base_url VARCHAR(512) NOT NULL COMMENT '环境基础URL',
  variables JSON NULL COMMENT '环境变量',
  headers JSON NULL COMMENT '公共请求头',
  is_default TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否默认环境',
  status VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '环境状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_environment_project_id (project_id),
  KEY idx_environment_project_default (project_id, is_default),
  KEY idx_environment_status (status),
  CONSTRAINT fk_environment_project_id FOREIGN KEY (project_id) REFERENCES project (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='环境配置表';

CREATE TABLE IF NOT EXISTS api_document (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  name VARCHAR(128) NOT NULL COMMENT '文档名称',
  source_type VARCHAR(32) NOT NULL COMMENT '文档来源类型',
  file_path VARCHAR(512) NULL COMMENT '上传文件路径',
  raw_content LONGTEXT NULL COMMENT '原始文档内容',
  parsed_data JSON NULL COMMENT '解析后的文档数据',
  status VARCHAR(32) NOT NULL DEFAULT 'uploaded' COMMENT '文档状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_api_document_project_id (project_id),
  KEY idx_api_document_status (status),
  CONSTRAINT fk_api_document_project_id FOREIGN KEY (project_id) REFERENCES project (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='接口文档表';

CREATE TABLE IF NOT EXISTS api_endpoint (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  api_document_id BIGINT NULL COMMENT '接口文档ID',
  name VARCHAR(128) NOT NULL COMMENT '接口名称',
  group_name VARCHAR(128) NULL COMMENT '接口分组',
  method VARCHAR(16) NOT NULL COMMENT 'HTTP方法',
  path VARCHAR(512) NOT NULL COMMENT '接口路径',
  description TEXT NULL COMMENT '接口描述',
  headers JSON NULL COMMENT '请求头定义',
  request_params JSON NULL COMMENT '请求参数定义',
  request_body_schema JSON NULL COMMENT '请求体结构',
  response_schema JSON NULL COMMENT '响应结构',
  example_request JSON NULL COMMENT '示例请求',
  example_response JSON NULL COMMENT '示例响应',
  auth_required TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否需要鉴权',
  tags JSON NULL COMMENT '接口标签',
  status VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT '接口状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_api_endpoint_project_id (project_id),
  KEY idx_api_endpoint_document_id (api_document_id),
  KEY idx_api_endpoint_method_path (method, path),
  KEY idx_api_endpoint_status (status),
  CONSTRAINT fk_api_endpoint_project_id FOREIGN KEY (project_id) REFERENCES project (id),
  CONSTRAINT fk_api_endpoint_document_id FOREIGN KEY (api_document_id) REFERENCES api_document (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='接口定义表';

CREATE TABLE IF NOT EXISTS test_case (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  api_endpoint_id BIGINT NULL COMMENT '接口ID',
  endpoint_name VARCHAR(128) NULL COMMENT '接口名称快照',
  endpoint_path VARCHAR(512) NULL COMMENT '接口路径快照',
  name VARCHAR(128) NOT NULL COMMENT '用例名称',
  description TEXT NULL COMMENT '用例描述',
  type VARCHAR(32) NOT NULL DEFAULT 'functional' COMMENT '统一用例类型',
  priority VARCHAR(32) NOT NULL DEFAULT 'P1' COMMENT '优先级',
  status VARCHAR(32) NOT NULL DEFAULT 'generated' COMMENT '用例状态',
  request_data JSON NULL COMMENT '统一请求数据',
  assertions JSON NULL COMMENT '结构化断言',
  dsl_assertions JSON NULL COMMENT 'DSL断言列表',
  coverage_tag JSON NULL COMMENT '覆盖标签',
  risk_level VARCHAR(32) NULL COMMENT '风险等级',
  data_dependency JSON NULL COMMENT '数据依赖',
  ai_metadata JSON NULL COMMENT 'AI生成元数据',
  steps JSON NULL COMMENT '历史测试步骤',
  variables JSON NULL COMMENT '历史用例变量',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_test_case_project_id (project_id),
  KEY idx_test_case_api_endpoint_id (api_endpoint_id),
  KEY idx_test_case_status (status),
  KEY idx_test_case_type (type),
  KEY idx_test_case_priority (priority),
  CONSTRAINT fk_test_case_project_id FOREIGN KEY (project_id) REFERENCES project (id),
  CONSTRAINT fk_test_case_api_endpoint_id FOREIGN KEY (api_endpoint_id) REFERENCES api_endpoint (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';

CREATE TABLE IF NOT EXISTS execution_task (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  environment_id BIGINT NULL COMMENT '环境ID',
  task_name VARCHAR(128) NOT NULL COMMENT '任务名称',
  status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '任务状态',
  trigger_type VARCHAR(32) NOT NULL DEFAULT 'manual' COMMENT '触发方式',
  total_cases INT NOT NULL DEFAULT 0 COMMENT '用例总数',
  passed_cases INT NOT NULL DEFAULT 0 COMMENT '通过用例数',
  failed_cases INT NOT NULL DEFAULT 0 COMMENT '失败用例数',
  started_at DATETIME NULL COMMENT '开始时间',
  finished_at DATETIME NULL COMMENT '结束时间',
  config JSON NULL COMMENT '执行配置',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_execution_task_project_id (project_id),
  KEY idx_execution_task_environment_id (environment_id),
  KEY idx_execution_task_status (status),
  CONSTRAINT fk_execution_task_project_id FOREIGN KEY (project_id) REFERENCES project (id),
  CONSTRAINT fk_execution_task_environment_id FOREIGN KEY (environment_id) REFERENCES environment (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行任务表';

CREATE TABLE IF NOT EXISTS execution_result (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  execution_task_id BIGINT NOT NULL COMMENT '执行任务ID',
  test_case_id BIGINT NULL COMMENT '测试用例ID',
  api_endpoint_id BIGINT NULL COMMENT '接口ID',
  status VARCHAR(32) NOT NULL COMMENT '执行状态',
  status_code INT NULL COMMENT 'HTTP状态码',
  response_time_ms INT NULL COMMENT '响应耗时毫秒',
  request_data JSON NULL COMMENT '请求数据',
  response_data JSON NULL COMMENT '响应数据',
  assertion_result JSON NULL COMMENT '断言结果',
  error_message TEXT NULL COMMENT '错误信息',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_execution_result_task_id (execution_task_id),
  KEY idx_execution_result_test_case_id (test_case_id),
  KEY idx_execution_result_status (status),
  CONSTRAINT fk_execution_result_task_id FOREIGN KEY (execution_task_id) REFERENCES execution_task (id),
  CONSTRAINT fk_execution_result_test_case_id FOREIGN KEY (test_case_id) REFERENCES test_case (id),
  CONSTRAINT fk_execution_result_api_endpoint_id FOREIGN KEY (api_endpoint_id) REFERENCES api_endpoint (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='执行结果表';

CREATE TABLE IF NOT EXISTS test_report (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  execution_task_id BIGINT NOT NULL COMMENT '执行任务ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  title VARCHAR(128) NOT NULL COMMENT '报告标题',
  summary JSON NULL COMMENT '报告摘要',
  report_path VARCHAR(512) NULL COMMENT '报告文件路径',
  status VARCHAR(32) NOT NULL DEFAULT 'created' COMMENT '报告状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_test_report_project_id (project_id),
  KEY idx_test_report_execution_task_id (execution_task_id),
  CONSTRAINT fk_test_report_execution_task_id FOREIGN KEY (execution_task_id) REFERENCES execution_task (id),
  CONSTRAINT fk_test_report_project_id FOREIGN KEY (project_id) REFERENCES project (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试报告表';

CREATE TABLE IF NOT EXISTS ai_analysis_record (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  project_id BIGINT NOT NULL COMMENT '项目ID',
  api_document_id BIGINT NULL COMMENT '接口文档ID',
  api_endpoint_id BIGINT NULL COMMENT '接口ID',
  test_case_id BIGINT NULL COMMENT '测试用例ID',
  analysis_type VARCHAR(64) NOT NULL COMMENT '分析类型',
  prompt_data JSON NULL COMMENT '提示词数据',
  result_data JSON NULL COMMENT 'AI分析结果',
  model_name VARCHAR(128) NULL COMMENT '模型名称',
  status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '分析状态',
  error_message TEXT NULL COMMENT '错误信息',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (id),
  KEY idx_ai_analysis_record_project_id (project_id),
  KEY idx_ai_analysis_record_type (analysis_type),
  KEY idx_ai_analysis_record_status (status),
  CONSTRAINT fk_ai_analysis_record_project_id FOREIGN KEY (project_id) REFERENCES project (id),
  CONSTRAINT fk_ai_analysis_record_api_document_id FOREIGN KEY (api_document_id) REFERENCES api_document (id),
  CONSTRAINT fk_ai_analysis_record_api_endpoint_id FOREIGN KEY (api_endpoint_id) REFERENCES api_endpoint (id),
  CONSTRAINT fk_ai_analysis_record_test_case_id FOREIGN KEY (test_case_id) REFERENCES test_case (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI分析记录表';
