import re
from hwp5.filtering import TextFilter
from hwp5.xmlmodel import Hwp5File
from django.core.management.base import BaseCommand
from products.models import ManualChunk

class Command(BaseCommand):
    help = '보금자리론 매뉴얼 목차 기반 페이지 매핑 및 슬라이딩 윈도우 적재'

    def handle(self, *args, **options):
        file_path = r"C:\Users\rkgml\Downloads\01_06_260102.hwp"
        self.stdout.write(self.style.SUCCESS(f"공정 시작: {file_path}"))

        try:
            # 1. 구조적 텍스트 추출 및 적재 실행
            count = self.run_manual_import(file_path)
            self.stdout.write(self.style.SUCCESS(f"✅ 적재 완료: 총 {count}개의 데이터 조각이 생성되었습니다."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 오류 발생: {str(e)}"))

    def get_hwp_text_clean(self, filename):
        """HWP 전문 라이브러리(pyhwp)를 통해 바이너리 노이즈 없이 텍스트 추출"""
        with Hwp5File(filename) as hwp:
            text_filter = TextFilter()
            # 내부 레코드 구조를 분석하여 텍스트만 필터링 (외계어 방지 핵심)
            return text_filter.filter_hwp5(hwp)

    def run_manual_import(self, file_path):
        # 2. 깨끗한 텍스트 획득
        raw_text = self.get_hwp_text_clean(file_path)
        
        # 3. 데이터 지도 (사용자 매뉴얼 기준)
        toc_map = {
            "제1장": 1, "제2장": 4, "제3장": 10, "제4장": 12, "제5장": 15,
            "제6장": 18, "제7장": 25, "제8장": 31, "제9장": 34, "제10장": 36,
            "제11장": 40, "제12장": 42, "제13장": 44, "제14장": 46, "제15장": 50,
            "별표1": 55
        }

        # 4. 챕터 분할 패턴
        chapter_pattern = r'(제\s?\d+\s?장\s?[^ ]+|별표\s?\d+)'
        parts = re.split(chapter_pattern, raw_text)
        
        # 기존 데이터 초기화
        ManualChunk.objects.all().delete()
        
        current_chapter = "서론/공통"
        current_page = 1
        record_count = 0

        # 슬라이딩 윈도우 설정
        window_size = 1200  # 한 조각 크기 (AI 문맥 파악 최적화)
        overlap = 300       # 중첩 크기 (연속성 확보)

        for part in parts:
            part = part.strip()
            if not part: continue
            
            # 챕터 및 페이지 정보 동기화
            is_chapter = False
            for key, page in toc_map.items():
                if key in part.replace(" ", ""):
                    current_chapter = part
                    current_page = page
                    is_chapter = True
                    break
            
            # 제목 자체는 저장하지 않고 다음 본문 파트로 진행
            if is_chapter: continue

            # [핵심] 슬라이딩 윈도우 알고리즘
            start = 0
            while start < len(part):
                end = start + window_size
                content = part[start:end]
                
                # DB 저장
                ManualChunk.objects.create(
                    content=content,
                    chapter_title=current_chapter,
                    page_number=current_page
                )
                record_count += 1
                
                # 윈도우 이동: (사이즈 - 오버랩)만큼 전진
                start += (window_size - overlap)
                
                # 조항의 끝에 도달하면 루프 종료
                if end >= len(part):
                    break
                
        return record_count