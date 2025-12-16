"""
mju-univ-auth 패키지 테스트
실제 PyPI에서 설치한 패키지를 테스트합니다.

사용법:
1. .env 파일에 MJU_ID와 MJU_PW 설정 (.env.example 참고)
2. python test.py 실행
"""

import os
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1. 패키지 import 테스트
print("=" * 50)
print("1. 패키지 Import 테스트")
print("=" * 50)

from mju_univ_auth import (
    StudentCard,
    StudentChangeLog,
    MjuUnivAuthError,
    NetworkError,
    PageParsingError,
    InvalidCredentialsError,
    SessionExpiredError
)

print("✅ 모든 클래스 import 성공!")
print(f"  - StudentCard: {StudentCard}")
print(f"  - StudentChangeLog: {StudentChangeLog}")
print(f"  - MjuUnivAuthError: {MjuUnivAuthError}")
print(f"  - NetworkError: {NetworkError}")
print(f"  - PageParsingError: {PageParsingError}")
print(f"  - InvalidCredentialsError: {InvalidCredentialsError}")
print(f"  - SessionExpiredError: {SessionExpiredError}")

# 2. 예외 클래스 테스트
print("\n" + "=" * 50)
print("2. 예외 클래스 테스트")
print("=" * 50)

try:
    raise InvalidCredentialsError("테스트 오류 메시지")
except InvalidCredentialsError as e:
    print(f"✅ InvalidCredentialsError 발생 및 캐치 성공: {e}")

try:
    raise NetworkError("네트워크 오류 테스트")
except MjuUnivAuthError as e:
    print(f"✅ NetworkError는 MjuUnivAuthError의 하위 클래스: {e}")

# 3. 모듈 정보 확인
print("\n" + "=" * 50)
print("3. 모듈 정보")
print("=" * 50)

import mju_univ_auth
print(f"패키지 위치: {mju_univ_auth.__file__}")
print(f"사용 가능한 항목: {mju_univ_auth.__all__}")

print("\n" + "=" * 50)
print("🎉 기본 테스트 모두 통과!")
print("=" * 50)

# 4. 실제 로그인 및 데이터 조회 테스트 (.env 필요)
print("\n" + "=" * 50)
print("4. 실제 동작 테스트 (데이터 조회)")
print("=" * 50)

# .env 파일 존재 여부 확인
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    print("⚠️  .env 파일이 없습니다. 다음 형식으로 .env 파일을 생성해주세요:")
    print()
    print("    MJU_ID=학번")
    print("    MJU_PW=비밀번호")
    print()
else:
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')
    print(f"📌 로그인 시도: {user_id}")
    
    # 4-1. 학생카드 정보 조회 테스트
    print("\n--- 4-1. 학생카드 정보 조회 테스트 ---")
    try:
        student_card = StudentCard.fetch(user_id, user_pw, verbose=False)
        print("✅ 학생카드 정보 조회 성공!")
        print("\n📋 학생카드 정보:")
        print(json.dumps(student_card.to_dict(), ensure_ascii=False, indent=2))
    except InvalidCredentialsError as e:
        print(f"❌ 조회 실패 (잘못된 인증 정보): {e}")
    except MjuUnivAuthError as e:
        print(f"❌ 조회 실패: {e}")
    
    # 4-2. 학적변동내역 조회 테스트
    print("\n--- 4-2. 학적변동내역 조회 테스트 ---")
    try:
        change_log = StudentChangeLog.fetch(user_id, user_pw, verbose=False)
        print("✅ 학적변동내역 조회 성공!")
        print("\n📋 학적변동내역:")
        print(json.dumps(change_log.to_dict(), ensure_ascii=False, indent=2))
    except InvalidCredentialsError as e:
        print(f"❌ 조회 실패 (잘못된 인증 정보): {e}")
    except MjuUnivAuthError as e:
        print(f"❌ 조회 실패: {e}")

print("\n" + "=" * 50)
print("🎉 모든 테스트 완료!")
print("=" * 50)

