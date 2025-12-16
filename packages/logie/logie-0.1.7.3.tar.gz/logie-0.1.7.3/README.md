# Install
```bash
pip install logie
```

# 개요

Python 기본 logging 모듈을 사용할 때마다 매번 formatter, handler, 파일 분리 등을 설정하는 과정을 생략하고자 편의성 함수로 그 과정을 압축하여 제공하는 로그 생성 유틸성 라이브러리

# Features

| 함수명                                                       | 목적                                     |
| ------------------------------------------------------------ | ---------------------------------------- |
| [get_logger](https://github.com/Kim-YoonHyun/logie/blob/master/docs/get_logger.md) | log 생성                                 |
| [log_sort](https://github.com/Kim-YoonHyun/logie/blob/master/docs/log_sort.md) | 생성된 rollover .log 파일 폴더 트리 정리 |

# version

## ver 0.1.7
- rollover 시 생성되는 log 파일을 특정 기간 기준 삭제하는 함수 log_del 추가

## ver 0.1.7.1 

- log_del 에 print 추가
- README.md 내용 갱신
- docs 추가
## ver 0.1.7.2 
- log_path 설정 안할시 자동으로 작업 디렉토리가 되도록 수정
## ver 0.1.6
- log 생성시 log_id 를 반드시 지정하도록 변경
- log handler 를 중복 생성하지 않도록 설정하여 log 기록 중첩을 방지
## ver 0.1.5 
- log 찍을 시 console display 추가
log 생성용 모듈
