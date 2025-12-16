import logging
import re
from datetime import datetime
from typing import Union, List

from k2magic.dataframe_db_exception import DataFrameDBException
from k2magic.dialect import k2a_requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import URL, make_url, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from d3sdk.model.business_model_define import InstanceMeasurement, HealthScore


class PgRepoDataFrameDB:
    """
    基于Repo数据库，提供根据业务信息如报警组访问Repo数据的能力
    :param repo_url: repo地址
    :param debug: 调试模式可输出更多日志信息
    """
    def __init__(self, repo_url: Union[str, URL], debug: bool = False, pgPort: int = None):
        self.debug = debug
        self.repo_url = repo_url
        self.pgPort = 5433 if pgPort is None else pgPort
        # 日志配置（与父类初始化可能存在重复，但问题不大）
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # pg连接配置
        pg_url_obj = self._disclose_pg_url(repo_url)
        self.engine = create_engine(pg_url_obj, echo=debug)
        # self.k2DataFrameDB = K2DataFrameDB(k2a_url, schema=schema, db_port=db_port, debug=debug, rest=rest)


    def _disclose_pg_url(self, k2a_url: Union[str, URL]) -> URL:
        """
        访问k2a的env接口，获取pg数据库的连接信息
        """
        k2a_url_obj = make_url(k2a_url)
        protocol = k2a_url_obj.query.get('protocol', 'https')  # k2assets http protocol
        auth = HTTPBasicAuth(k2a_url_obj.username, k2a_url_obj.password)
        api_url = f"{protocol}://{k2a_url_obj.host}:{k2a_url_obj.port}/api/env/k2box.postgresql"
        resp = k2a_requests.get(api_url, auth=auth)

        envs = resp['body']['values']
        pg_host = k2a_url_obj.host
        pg_password = envs['k2box.postgresql.password']
        pg_user = envs['k2box.postgresql.username']
        pg_url_obj = make_url(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{self.pgPort}/repos')
        self.logger.debug(f'postgres url: {pg_url_obj}')
        return pg_url_obj

    def getLatestHealthScore(self, deviceCode: str, healthCode: str) -> HealthScore:
        """
        查询机组诊断模块最新健康度
        :param deviceCode: 设备编码
        :param healthCode: 健康指标编码
        :return: 最新健康度信息
        """
        
        sql = """
        SELECT
            TO_CHAR( TO_TIMESTAMP( k_ts / 1000000000 ), 'YYYY-MM-DD HH24:MI:SS' ) AS k_ts, 
            k_device, 
            score, 
            healthy_code, 
            jsoninfo
        FROM
            _root_healthy
        WHERE
            k_device = :deviceCode AND healthy_code = :healthCode
        ORDER BY
            k_ts DESC
        LIMIT 1
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {
                    'deviceCode': deviceCode,
                    'healthCode': healthCode
                })
                row = result.fetchone()
                if row:
                    return HealthScore(
                        timestamp=row[0],
                        deviceCode=row[1],
                        score=row[2],
                        healthyCode=row[3],
                        jsonInfo=row[4]
                    )
                else:
                    return None
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query latest health score due to a database error. SQL: {sql}",
                original_exception=e
            )

    def getHealthScoreRecords(self, deviceCode: str, healthCode: str, startTime: str, endTime: str) -> List[HealthScore]:
        """
        通过设备编码、健康指标编码和时间范围查询健康度记录
        :param deviceCode: 设备编码 (必填)
        :param healthCode: 健康指标编码 (必填)
        :param startTime: 开始时间 (格式: yyyy-MM-dd HH:mm:ss) (必填)
        :param endTime: 结束时间 (格式: yyyy-MM-dd HH:mm:ss) (必填)
        :return: 健康度记录列表
        """
        
        # 参数验证
        if not deviceCode:
            raise ValueError("deviceCode cannot be empty")
        if not healthCode:
            raise ValueError("healthCode cannot be empty")
        if not startTime:
            raise ValueError("startTime cannot be empty")
        if not endTime:
            raise ValueError("endTime cannot be empty")
        
        # 将时间字符串转换为纳秒时间戳
        from datetime import datetime
        try:
            start_dt = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(endTime, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise ValueError(f"Invalid time format. Expected 'yyyy-MM-dd HH:mm:ss', got error: {e}")
        
        # 转换为纳秒时间戳 (PostgreSQL中存储的是纳秒)
        start_time_ns = int(start_dt.timestamp() * 1000000000)
        end_time_ns = int(end_dt.timestamp() * 1000000000)
        
        sql = """
        SELECT
            k_device,
            healthy_code,
            TO_CHAR( TO_TIMESTAMP( k_ts / 1000000000 ), 'YYYY-MM-DD HH24:MI:SS' ) AS k_ts,
            score
        FROM
            _root_healthy
        WHERE
            (k_ts BETWEEN :startTimeNs AND :endTimeNs)
            AND k_device = :deviceCode
            AND healthy_code = :healthCode
        ORDER BY k_ts DESC
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), {
                    'startTimeNs': start_time_ns,
                    'endTimeNs': end_time_ns,
                    'deviceCode': deviceCode,
                    'healthCode': healthCode
                })
                records = []
                for row in result.fetchall():
                    record = HealthScore(
                        timestamp=row[2],  # 格式化后的时间字符串
                        deviceCode=row[0],
                        score=row[3],
                        healthyCode=row[1],
                        jsonInfo=None  # 这个查询中没有jsoninfo字段
                    )
                    records.append(record)
                return records
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query health score records due to a database error. SQL: {sql}",
                original_exception=e
            )