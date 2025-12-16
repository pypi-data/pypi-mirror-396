"""
Matilo Model Serving Worker Module

author: Hyungkoo.kim
"""

__author__ = "ryuvsken"
__copyright__ = "Copyright (C) 2025 Matilo (C)"


import os
import time
import json
from datetime import datetime, date
import requests

from enum import Enum

from sqlalchemy import Connection, Engine, Transaction, create_engine, text

from mmsw.core.config_base import ConfigBase, set_config_base, get_config_base


REQUEST_TIMEOUT = 10


"""
모델 구동 결과의 상태 정보

- READY : 모델 서빙 대기
- RUN : 모델 구동 중
- FAIL : 모델 구동 실패
- BADPARAM : 잘못된 매개변수
- TIMEOUT : 모델 구동 타임아웃
- CANCEL : 모델 구동 취소
- COMPLETE : 모델 구동 완료
"""
class ModelStatus(Enum):
    READY = 0
    RUN = 1
    FAIL = 2
    BADPARAM = 3
    TIMEOUT = 4
    CANCEL = 5
    COMPLETE = 200


"""
모델 리포트 API 호출 결과 정보

0: 결과 반환 준비
1: 접속 실패
2: 오류 반환
3: 그외 에러
4: 보고하지 않음 (REPORT_URL 이 비어 있을 경우)
200: 완료
"""
class ModelReportStatus(Enum):
    READY = 0
    CONNECT_ERROR = 1
    READ_ERROR = 2
    ERROR = 3
    SKIP = 4
    COMPLETE = 200


"""
모델 워커 동작 상태

- 0: READY
- 1: RUN
- 2: TERMINATE
- 4: SHUTDOWN
"""
class WorkerStatus(Enum):
    READY = 0
    RUN = 1
    TERMINATE = 2
    SHUTDOWN = 4


"""
슬랙 알림 상태

- OK: 정상
- FAIL: 비정상
"""
class SlackStatus(Enum):
    OK = 0
    FAIL = 1


"""
모델 구동에 필요한 인자 정보

- **id**: 모델 실행 요청 ID
- **model_name**: 모델명
- **model_params**: 모델 실행을 위한 매개 변수 (JSON 문자열 형태)
- **image_root**: 모델 실행 결과에 이미지가 포함된 경우 이미지를 저장 할 루트 패스
ex) /var/www/2025/12/ 와 같이 전달된 경우 /var/www/2025/12/m1_1_01.png 형태로 저장
여기서 m1 은 모델명, 1 은 모델 실행 요청 ID, 01 은 이미지가 여러개 일 경우 순서
- **image_host**: 모델 실행 결과에 이미지가 포함된 경우 JSON 형태로 결과를 반환시 호스팅 되는 서버의 호스트 정보
ex) http://192.168.0.1:8080/2025/12/ 와 같이 전달된 경우 http://192.168.0.1:8080/2025/12/m1_1_01.png 형태로 JSON 결과에 포함
"""
class MMSWParams:
    id: int
    model_name: str
    model_params: str
    image_root: str
    image_host: str

    def __init__(self, id: int, model_name: str, model_params: str, image_root: str, image_host):
        self.id = id
        self.model_name = model_name
        self.model_params = model_params
        self.image_root = image_root
        self.image_host = image_host


"""
모델 서빙 결과 반환 정보

- **status**: 모델 구동 결과의 상태 정보
- **model_result**: 모델 실행 결과가 저장된 변수 (JSON 문자열 형태)
"""
class MMSWResult:
    status: ModelStatus
    model_result: str

    def __init__(self, status: ModelStatus, model_result: str):
        self.status = status
        self.model_result = model_result




def run_worker(fnRunModel):

    set_config_base(ConfigBase())
    settings = get_config_base()

    IMAGE_ROOT = settings.IMAGE_ROOT
    IMAGE_HOST = settings.IMAGE_HOST

    slack_send(status=SlackStatus.OK, slack_msg='Worker Start: ' + ', Worker: ' + settings.MODEL_WORKER)
    worker_report(status=WorkerStatus.RUN, serving_id=None)

    while True:
        time.sleep(3)

        if worker_check() == False:
            break

        engine: Engine = None
        conn: Connection = None
        transaction: Transaction = None
        
        id: int = None
        model_name: str = None
        params: str = None

        try:
            engine, conn = _db_open()
            transaction = conn.begin()
            query = f"SELECT * FROM model_serving WHERE model = '{settings.MODEL_NAME}' AND status = 0 ORDER BY id ASC LIMIT 1 FOR UPDATE;"
            rs = conn.execute(text(query)).fetchone()

            if rs is None or len(rs) == 0:
                transaction.commit()
                continue

            id = rs.id
            model_name = rs.model
            params = rs.params

            query = f"UPDATE model_serving SET status = {ModelStatus.RUN.value}, start_date = CURRENT_TIMESTAMP, upt_date = CURRENT_TIMESTAMP, worker_name='{settings.MODEL_WORKER}' WHERE id={id};"
            conn.execute(text(query))
            transaction.commit()
        except Exception as e:
            transaction.rollback()

            slack_msg = 'Serving Check DB Query Error: ' + str(e) + ', Worker: ' + settings.MODEL_WORKER
            slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
        finally:
            _db_close_safe(engine=engine, conn=conn)

        
        try:
            if not model_name or not params:
                raise Exception("Bad Model Params")

            slack_msg = 'Start ID: ' + str(id) + ', Worker: ' + settings.MODEL_WORKER
            slack_send(status=SlackStatus.OK, slack_msg=slack_msg)

            worker_report(status=WorkerStatus.RUN, serving_id=id)
            
            current_dt = datetime.now()
            image_root = os.path.join(IMAGE_ROOT, str(current_dt.year), str(current_dt.month))
            image_host = IMAGE_HOST + "/" + str(current_dt.year) + "/" + str(current_dt.month)
            model_params = MMSWParams(
                id=id,
                model_name=model_name,
                model_params=params,
                image_root=image_root,
                image_host=image_host
            )
            model_result = fnRunModel(model_params)
            #result = model_result.model_result.replace('"', '\"')

            # model_report() 함수를 호출하여 모델 결과 기록
            #model_report(id=id, status=200, result="{\"key1\": \"val1\"}")
            model_result_report(id=id, status=model_result.status, result_json=model_result.model_result)

            model_result_webhook_send(id = id)

            slack_msg = 'End ID: ' + str(id) + ', Worker: ' + settings.MODEL_WORKER
            slack_send(status=SlackStatus.OK, slack_msg=slack_msg)
        except Exception as e:
            result_json=json.dumps({"msg": str(e)}, ensure_ascii=False)
            model_result_report(id=id, status=ModelStatus.FAIL, result_json=result_json)

            slack_msg = 'Error ID: ' + str(id) + ", Msg: " + str(e) + ', Worker: ' + settings.MODEL_WORKER
            slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)

            model_result = MMSWResult(status=ModelStatus.FAIL, model_result=result_json)
            model_result_webhook_send(id = id)


"""
모델 구동 결과 기록
"""
def model_result_report(id: int, status: ModelStatus, result_json: str):

    settings = get_config_base()

    engine: Engine = None
    conn: Connection = None

    try:
        engine, conn = _db_open()
        query = f"UPDATE model_serving SET result_msg = '{result_json}', status = {status.value}, end_date = CURRENT_TIMESTAMP, upt_date = CURRENT_TIMESTAMP, worker_name='{settings.MODEL_WORKER}' WHERE id = {id};"
        conn.execute(text(query))
        conn.commit()
    except Exception as e:
        slack_msg = 'Model Result DB Error Msg: ' + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    finally:
        _db_close_safe(engine=engine, conn=conn)


"""
모델 상태 반환
"""
def model_get(id: int) -> tuple[int, int, str, str, str, str, str, str, str]:

    engine: Engine = None
    conn: Connection = None

    try:
        engine, conn = _db_open()
        query = f"SELECT * FROM model_serving WHERE id = {id};"
        rs = conn.execute(text(query)).fetchone()

        return (
            rs.id,
            rs.req_user_id,
            rs.model,
            rs.status,
            rs.result_msg,
            rs.crt_date,
            rs.upt_date,
            rs.start_date,
            rs.end_date
            )
    except Exception as e:
        raise e
    finally:
        _db_close_safe(engine=engine, conn=conn)


def model_result_webhook_status(id: int, status: ModelReportStatus):
    settings = get_config_base()

    engine: Engine = None
    conn: Connection = None

    try:
        engine, conn = _db_open()
        query = f"UPDATE model_serving SET report_status = '{status.value}', report_date = CURRENT_TIMESTAMP, upt_date = CURRENT_TIMESTAMP, worker_name='{settings.MODEL_WORKER}' WHERE id = {id};"
        conn.execute(text(query))
        conn.commit()
    except Exception as e:
        slack_msg = 'Model Report DB Error Msg: ' + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    finally:
        _db_close_safe(engine=engine, conn=conn)


def datetime_to_json_formatting(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()


"""
모델 구동 결과를 Webhook 으로 호출
"""
def model_result_webhook_send(id: int):

    settings = get_config_base()
    result_url = settings.RESULT_URL

    try:
        if not result_url:
            model_result_webhook_status(id=id, status=ModelReportStatus.SKIP)
            # slack_msg = 'Webhook Skip: id = ' + str(id) + ', Worker: ' + settings.MODEL_WORKER
            # slack_send(status=model_result.status.value, slack_msg=slack_msg)
            return

        (id, req_user_id, model, status, result_msg, crt_date, upt_date, start_date, end_date) = model_get(id)
        
        header = {'Content-type': 'application/json'}

        result_json = {
            "id": id,
            "req_user_id": req_user_id,
            "model": model,
            "status": status,
            "result_msg": result_msg,
            "crt_date": crt_date,
            "upt_date": upt_date,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        # 메세지 전송
        requests.post(result_url, headers=header, data=json.dumps(result_json, default=datetime_to_json_formatting, ensure_ascii=False), timeout=REQUEST_TIMEOUT)
        model_result_webhook_status(id=id, status=ModelReportStatus.COMPLETE)
    except requests.exceptions.ConnectTimeout as e:
        model_result_webhook_status(id=id, status=ModelReportStatus.CONNECT_ERROR)
        slack_msg = 'Webhook Error: id = ' + str(id) + ", msg: " + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    except requests.exceptions.ReadTimeout as e:
        model_result_webhook_status(id=id, status=ModelReportStatus.READ_ERROR)
        slack_msg = 'Webhook Error: id = ' + str(id) + ", msg: " + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    except Exception as e:
        model_result_webhook_status(id=id, status=ModelReportStatus.ERROR)
        slack_msg = 'Webhook Error: id = ' + str(id) + ", msg: " + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    

def worker_check():

    settings = get_config_base()

    engine: Engine = None
    conn: Connection = None

    ret = True
    try:
        engine, conn = _db_open()
        query = f"SELECT * FROM model_worker WHERE name = '{settings.MODEL_WORKER}' ORDER BY id ASC LIMIT 1;"
        rs = conn.execute(text(query)).fetchone()
        if rs is None or len(rs) == 0:
            ret = False
        
        if ret and rs.status == WorkerStatus.SHUTDOWN.value:
            ret = False

    except Exception as e:
        slack_msg = 'Worker Check DB Query Error Msg: ' + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    finally:
        _db_close_safe(engine=engine, conn=conn)

    if ret == False:
        worker_report(WorkerStatus.TERMINATE, None)
        
        slack_msg = 'Worker Shutdown: ' + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)

    return ret


def worker_report(status: WorkerStatus, serving_id: int = None):

    settings = get_config_base()
    
    engine: Engine = None
    conn: Connection = None

    try:
        id = None

        engine, conn = _db_open()
        conn = engine.connect()
        query = f"SELECT * FROM model_worker WHERE name = '{settings.MODEL_WORKER}' ORDER BY id ASC LIMIT 1;"
        rs = conn.execute(text(query)).fetchone()
        if rs is None or len(rs) == 0:
            query = f"INSERT INTO model_worker (name, model_name, status) VALUES ('{settings.MODEL_WORKER}', '{settings.MODEL_NAME}', 0)"
            conn.execute(text(query))
            conn.commit()

            query = f"SELECT * FROM model_worker WHERE name = '{settings.MODEL_WORKER}' ORDER BY id ASC LIMIT 1;"
            rs = conn.execute(text(query)).fetchone()
            if rs is None or len(rs) == 0:
                raise Exception('Model Worker DB Not Exist...')
            id = rs.id
        else:
            id = rs.id

        if serving_id is not None:
            query = f"UPDATE model_worker SET status = {status.value}, upt_date = CURRENT_TIMESTAMP, serving_id = {serving_id}, serving_date = CURRENT_TIMESTAMP WHERE id = {id}"
        else:
            query = f"UPDATE model_worker SET status = {status.value}, upt_date = CURRENT_TIMESTAMP WHERE id = {id}"
        conn.execute(text(query))
        conn.commit()
    except Exception as e:
        slack_msg = 'Worker Report DB Error Msg: ' + str(e) + ', Worker: ' + settings.MODEL_WORKER
        slack_send(status=SlackStatus.FAIL, slack_msg=slack_msg)
    finally:
        _db_close_safe(engine=engine, conn=conn)


def slack_send(status: SlackStatus, slack_msg: str):

    settings = get_config_base()
    if not settings.SLACK_URL:
        return

    try:
        url = settings.SLACK_URL
        
        header = {'Content-type': 'application/json'}
        username = "model-worker-bot"

        # https://slackmojis.com/
        # https://github.com/d0x2f/slack-emoji-text
        icon_emoji = ":smile:" if status == SlackStatus.OK else ":cry:"
        color = ":good:" if status == SlackStatus.OK else ":bad:"

        time_with_milliseconds_string = datetime.now().strftime("%H:%M:%S")
        # 😢
        icon_msg = ": :smile: - " if status == SlackStatus.OK else ": :cry: - "
        slack_msg = time_with_milliseconds_string + icon_msg + slack_msg
        attachments = [{
            "color": color,
            "text": slack_msg
        }]
        
        data = {"username": username, "attachments": attachments, "icon_emoji": icon_emoji}
        #print(data)

        # 메세지 전송
        requests.post(url, headers=header, json=data, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        pass


def _db_open() -> tuple[Engine, Connection]:

    settings = get_config_base()
    DB_URL = f'{settings.DB_SCHEME}://{settings.DB_USER}:{settings.DB_PWD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8'

    engine: Engine = None
    conn: Connection = None

    try:
        engine = create_engine(DB_URL, echo=True)
        conn = engine.connect()
    except Exception as e:
        _db_close_safe(engine=engine, conn=conn)
        raise e

    return (engine, conn)


def _db_close_safe(engine, conn):

    try:
        if conn is not None:
            conn.close()
    except:
        pass

    try:
        if engine is not None:
            engine.dispose()
    except:
        pass

