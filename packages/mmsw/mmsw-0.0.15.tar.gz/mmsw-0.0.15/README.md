

# Matilo Model Serving Worker (mmsw)


## Environment


| Name | Desc |
| --- | --- |
| APP_ENV | 운영 환경 (local/dev/test/prod) |
| PROJECT_NAME | 프로젝트 이름 |
| DB_SCHEME | Sqlalchemy DB 스키마 (mysql+pymysql) |
| DB_HOST | DB 서버 호스트 (IP) |
| DB_PORT | DB 서버 포트 |
| DB_USER | DB 사용자 ID |
| DB_PWD | DB 암호 |
| DB_NAME | DB 명 |
| MODEL_NAME | 서빙 할 모델의 고유 이름 |
| MODEL_WORKER | 서빙 할 모델 워커의 고유 이름 |
| IMAGE_ROOT | 모델 실행 결과에 이미지가 포함된 경우 이미지를 저장 할 루트 패스<br/>ex) /var/www/2025/12/ 와 같이 전달된 경우 /var/www/2025/12/m1_1_01.png 형태로 저장<br/>여기서 m1 은 모델명, 1 은 모델 실행 요청 ID, 01 은 이미지가 여러개 일 경우 순서 |
| IMAGE_HOST | 모델 실행 결과에 이미지가 포함된 경우 JSON 형태로 결과를 반환시 호스팅 되는 서버의 호스트 정보<br/>ex) http://192.168.0.1:8080/2025/12/ 와 같이 전달된 경우 http://192.168.0.1:8080/2025/12/m1_1_01.png 형태로 JSON 결과에 포함 |
| SLACK_URL | 오류 발생시 메시지를 전달 할 Slack URL |



## Module Integration Guide

- Module Setup

```bash
$ pipenv install mmsw
```


- Module Integration

```py
import json

from mmsw.mmsw import MMSWParams, MMSWResult, ModelStatus, run_worker


"""
**모델이 실행될 콜백 함수**

MMSWParams class 정의 (모델이 실행될 콜백 함수)

- **params: MMSWParams**: 모델 구동에 필요한 인자 정보
  - **id**: 모델 실행 요청 ID
  - **model_name**: 모델명
  - **model_params**: 모델 실행을 위한 매개 변수 (JSON 문자열 형태)
  - **image_root**: 모델 실행 결과에 이미지가 포함된 경우 이미지를 저장 할 루트 패스
    ex) /var/www/2025/12/ 와 같이 전달된 경우 /var/www/2025/12/m1_1_01.png 형태로 저장
    여기서 m1 은 모델명, 1 은 모델 실행 요청 ID, 01 은 이미지가 여러개 일 경우 순서
  - **image_host**: 모델 실행 결과에 이미지가 포함된 경우 JSON 형태로 결과를 반환시 호스팅 되는 서버의 호스트 정보
    ex) http://192.168.0.1:8080/2025/12/ 와 같이 전달된 경우 http://192.168.0.1:8080/2025/12/m1_1_01.png 형태로 JSON 결과에 포함

    
MMSWResult class 정의 (모델 서빙 결과 반환 정보)

- **status**: 모델의 실행 결과의 상태 (ModelStatus enum 사용)
- **model_result**: 모델 실행 결과가 저장된 변수 (JSON 문자열 형태)


ModelStatus enum 정의 (모델 서빙의 상태 정보)

- READY : 모델 서빙 대기
- RUN : 모델 구동 중
- FAIL : 모델 구동 실패
- BADPARAM : 잘못된 매개변수
- TIMEOUT : 모델 구동 타임아웃
- CANCEL : 모델 구동 취소
- COMPLETE : 모델 구동 완료
"""
def run_model(model_params: MMSWParams) -> MMSWResult:

    # TODO: 1. 모델 매개변수의 유효성 체크 (예시)

    try:
        json_params = json.loads(model_params)
        gen_size = json_params["gen_size"]
        scaffold = json_params["scaffold"]
        
        if gen_size is None or gen_size < 0 or gen_size > 100 or scaffold is None:
            # 모델 매개변수가 요효하지 않다면 다음과 같이 매개변수 오류를 반환
            return MMSWResult(status=ModelStatus.BADPARAM, model_result=json.dumps({"result": "Bad Param"}, ensure_ascii=False))
    except Exception:
        return MMSWResult(status=ModelStatus.BADPARAM, model_result=json.dumps({"result": "Bad Model Param - JSON Format"}, ensure_ascii=False))
    

    # TODO: 2. 모델 실행 코드 연동

    
    # TODO: 3. 모델의 출력 결과를 JSON 정보를 저장 (예시)
    model_result = ["data1", "data2"]


    # TODO: 4. 모델 실행 결과의 상태와 출력 정보를 JSON 문자열로 전달
    return MMSWResult(status=ModelStatus.COMPLETE, model_result=json.dumps({"result": model_result}, ensure_ascii=False))


if __name__ == '__main__':

    run_worker(fnRunModel=run_model)
```



## Module Distribution

- New Stype

```bash
# Pre install
$ pip install build

# Do build & upload
$ python -m build
$ python -m twine upload dist/*
```


- Old Stype

```bash
# Pre install
$ pip install setuptools wheel

# Do build & upload
$ python setup.py sdist bdist_wheel
$ python -m twine upload dist/*
```


