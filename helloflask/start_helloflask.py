import sys
import os

# 현재 파일의 경로에서 상위 디렉토리로 이동
project_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 위치
parent_dir = os.path.dirname(project_dir)  # 상위 디렉토리

# 상위 디렉토리를 sys.path에 추가
sys.path.append(parent_dir)

from helloflask import app  # 모듈 임포트

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
