import json
import logging
from django.conf import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

# OpenAI 라이브러리 안전 import
try:
    import openai
    OPENAI_AVAILABLE = True
    logger.info("OpenAI 라이브러리 로드 성공")
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("OpenAI 라이브러리를 찾을 수 없습니다.")


class GPTService:
    """OpenAI GPT API를 사용한 가이드라인 처리 서비스"""
    
    def __init__(self):
        self.use_fallback = True
        self.client = None
        
        # OpenAI 사용 가능성 확인
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI 라이브러리가 없습니다. 기본값을 사용합니다.")
            return
            
        # API 키 확인
        self.api_key = getattr(settings, 'OPENAI_API_KEY', '')
        
        # API 키 상세 로그 출력
        if self.api_key:
            logger.info(f"🔑 API 키 확인됨:")
            logger.info(f"   - 길이: {len(self.api_key)}자")
            logger.info(f"   - 시작: {self.api_key[:20]}...")
            logger.info(f"   - 끝: ...{self.api_key[-10:]}")
            logger.info(f"   - 전체: {self.api_key}")  # 디버깅용 전체 키 출력
        else:
            logger.error("❌ API 키가 비어있습니다.")
            
        if not self.api_key or self.api_key.startswith('sk-your'):
            logger.error("❌ OpenAI API 키가 설정되지 않았습니다. .env 파일의 OPENAI_API_KEY를 확인하세요.")
            return
            
        # OpenAI 클라이언트 초기화 (0.28.1 버전용)
        try:
            # OpenAI 0.28.1 방식: 전역 API 키 설정
            logger.info("OpenAI 0.28.1 방식으로 초기화 시도...")
            openai.api_key = self.api_key
            
            # 연결 테스트 - 올바른 모델명으로
            logger.info("OpenAI API 연결 테스트 중...")
            test_response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # 존재하는 모델명 사용
                messages=[{"role": "user", "content": "테스트"}],
                max_tokens=5
            )
            
            self.use_fallback = False
            self.model_name = "gpt-4o-mini"
            logger.info("✅ OpenAI API 연결 성공! 실제 GPT를 사용합니다.")
            
        except Exception as e:
            logger.warning(f"gpt-4o-mini 실패: {e}")
            try:
                # gpt-3.5-turbo로 재시도
                logger.info("gpt-3.5-turbo로 연결 테스트...")
                test_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "테스트"}],
                    max_tokens=5
                )
                
                self.use_fallback = False
                self.model_name = "gpt-3.5-turbo"
                logger.info("✅ OpenAI API 연결 성공! (gpt-3.5-turbo)")
                
            except Exception as e2:
                logger.error(f"❌ 모든 모델 테스트 실패:")
                logger.error(f"   gpt-4o-mini: {e}")
                logger.error(f"   gpt-3.5-turbo: {e2}")
                logger.error("기본 더미 데이터를 사용합니다.")
                self.use_fallback = True
    
    def generate_summary(self, guideline_text: str = None) -> Dict[str, Any]:
        """
        가이드라인 텍스트를 요약하여 구조화된 데이터로 반환
        """
        # Fallback 사용
        if self.use_fallback:
            logger.warning("🔄 실제 GPT API를 사용할 수 없어 더미 데이터를 반환합니다.")
            return self._get_default_summary()
            
        try:
            # 기본 가이드라인 텍스트
            if not guideline_text:
                guideline_text = """
                소프트웨어 개발 가이드라인
                
                1. 코드 품질 관리
                - 모든 코드는 코드 리뷰를 거쳐야 합니다
                - 린터와 포매터를 사용하여 일관된 코딩 스타일을 유지합니다
                - 변수명과 함수명은 명확하고 의미 있게 작성합니다
                - 복잡한 로직에는 충분한 주석을 작성합니다
                
                2. 테스팅
                - 단위 테스트 커버리지는 최소 80% 이상을 유지합니다
                - 통합 테스트를 통해 시스템 전체 동작을 검증합니다
                - CI/CD 파이프라인에서 자동화된 테스트를 실행합니다
                - 테스트 코드도 프로덕션 코드와 동일한 품질을 유지합니다
                
                3. 문서화
                - API 문서는 자동으로 생성되도록 설정합니다
                - README 파일을 최신 상태로 유지합니다
                - 아키텍처 결정사항은 ADR(Architecture Decision Record)로 기록합니다
                - 운영 가이드와 트러블슈팅 문서를 작성합니다
                
                4. 보안
                - 민감한 정보는 환경변수로 관리합니다
                - 정기적으로 보안 취약점 스캔을 실행합니다
                - 인증과 권한 관리를 철저히 합니다
                - HTTPS를 필수로 사용합니다
                """
            
            prompt = f"""
            다음 소프트웨어 개발 가이드라인을 분석하여 핵심 내용을 요약해주세요.
            
            가이드라인:
            {guideline_text}
            
            다음 JSON 형식으로 응답해주세요:
            {{
                "title": "가이드라인의 제목",
                "content": "가이드라인의 전체적인 요약 (2-3문장)",
                "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
                "word_count": 단어수
            }}
            
            JSON 형식만 반환하고 다른 텍스트는 포함하지 마세요.
            """
            
            logger.info("🤖 실제 GPT API로 요약 생성 시작...")
            
            # OpenAI 0.28.1 방식 사용
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 소프트웨어 개발 문서를 분석하고 요약하는 전문가입니다. 정확한 JSON 형식으로만 응답하세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"✅ GPT API 응답 성공! (길이: {len(content)}자)")
            logger.info(f"응답 미리보기: {content[:100]}...")
            
            # JSON 파싱 (마크다운 코드 블록 제거)
            try:
                # ```json과 ``` 제거
                if content.startswith('```json'):
                    content = content[7:]  # ```json 제거
                if content.startswith('```'):
                    content = content[3:]   # ``` 제거
                if content.endswith('```'):
                    content = content[:-3]  # 끝의 ``` 제거
                
                content = content.strip()
                summary_data = json.loads(content)
                logger.info("🎉 실제 GPT가 생성한 요약 완료!")
                
                # GPT 응답임을 표시하기 위해 메타 정보 추가
                summary_data['_source'] = 'openai_gpt'
                summary_data['_model'] = self.model_name
                
                return summary_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 에러: {e}")
                logger.error(f"정제된 응답: {content[:200]}...")
                return self._get_default_summary()
                
        except Exception as e:
            logger.error(f"❌ GPT 요약 생성 오류: {e}")
            return self._get_default_summary()
    
    def generate_checklist(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        요약 데이터를 바탕으로 체크리스트를 생성
        """
        # Fallback 사용
        if self.use_fallback:
            logger.warning("🔄 실제 GPT API를 사용할 수 없어 더미 체크리스트를 반환합니다.")
            return self._get_default_checklist()
            
        try:
            prompt = f"""
            다음 가이드라인 요약을 바탕으로 개발자들이 사용할 수 있는 체크리스트를 생성해주세요.
            
            요약:
            제목: {summary.get('title', '')}
            내용: {summary.get('content', '')}
            핵심 포인트: {', '.join(summary.get('key_points', []))}
            
            다음 JSON 형식으로 체크리스트를 생성해주세요:
            {{
                "categories": [
                    {{
                        "name": "카테고리명",
                        "items": [
                            {{
                                "id": 1,
                                "text": "체크할 내용 (질문 형태)",
                                "required": true
                            }}
                        ]
                    }}
                ],
                "total_items": 전체_항목_수,
                "required_items": 필수_항목_수
            }}
            
            카테고리는 4-5개, 각 카테고리당 3-5개 항목을 만들어주세요.
            JSON 형식만 반환하고 다른 텍스트는 포함하지 마세요.
            """
            
            logger.info("🤖 실제 GPT API로 체크리스트 생성 시작...")
            
            # OpenAI 0.28.1 방식 사용
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 소프트웨어 개발 체크리스트 작성 전문가입니다. 실용적이고 구체적인 체크리스트를 JSON 형식으로만 제공하세요."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"✅ GPT API 응답 성공! (길이: {len(content)}자)")
            logger.info(f"응답 미리보기: {content[:100]}...")
            
            # JSON 파싱 (마크다운 코드 블록 제거)
            try:
                # ```json과 ``` 제거
                if content.startswith('```json'):
                    content = content[7:]  # ```json 제거
                if content.startswith('```'):
                    content = content[3:]   # ``` 제거
                if content.endswith('```'):
                    content = content[:-3]  # 끝의 ``` 제거
                
                content = content.strip()
                checklist_data = json.loads(content)
                logger.info("🎉 실제 GPT가 생성한 체크리스트 완료!")
                
                # GPT 응답임을 표시하기 위해 메타 정보 추가
                checklist_data['_source'] = 'openai_gpt'
                checklist_data['_model'] = self.model_name
                
                return checklist_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 에러: {e}")
                logger.error(f"정제된 응답: {content[:200]}...")
                return self._get_default_checklist()
                
        except Exception as e:
            logger.error(f"❌ GPT 체크리스트 생성 오류: {e}")
            return self._get_default_checklist()
    
    def _get_default_summary(self) -> Dict[str, Any]:
        """기본 요약 반환 (더미 데이터)"""
        return {
            "title": "소프트웨어 개발 가이드라인 요약",
            "content": "가이드라인은 코드 품질, 테스팅, 문서화, 보안 등 소프트웨어 개발의 핵심 원칙들을 다룹니다.",
            "key_points": [
                "코드 리뷰 필수",
                "테스트 커버리지 80% 이상", 
                "API 문서화 자동화"
            ],
            "word_count": 150,
            "_source": "fallback_dummy",
            "_model": "dummy_data"
        }
    
    def _get_default_checklist(self) -> Dict[str, Any]:
        """기본 체크리스트 반환 (더미 데이터)"""
        return {
            "categories": [
                {
                    "name": "코드 품질",
                    "items": [
                        {"id": 1, "text": "코드 리뷰가 완료되었는가?", "required": True},
                        {"id": 2, "text": "린터 규칙을 준수하였는가?", "required": True},
                        {"id": 3, "text": "변수명이 명확하게 작성되었는가?", "required": False}
                    ]
                },
                {
                    "name": "테스팅", 
                    "items": [
                        {"id": 4, "text": "단위 테스트가 작성되었는가?", "required": True},
                        {"id": 5, "text": "통합 테스트가 수행되었는가?", "required": True}
                    ]
                },
                {
                    "name": "문서화",
                    "items": [
                        {"id": 6, "text": "API 문서가 업데이트되었는가?", "required": True},
                        {"id": 7, "text": "README 파일이 최신인가?", "required": False}
                    ]
                }
            ],
            "total_items": 7,
            "required_items": 5,
            "_source": "fallback_dummy",
            "_model": "dummy_data"
        }