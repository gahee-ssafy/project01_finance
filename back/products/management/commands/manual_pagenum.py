import re
import olefile
import zlib
from django.core.management.base import BaseCommand
from products.models import ManualChunk

class Command(BaseCommand):
    help = '보금자리론 매뉴얼 목차 기반 페이지 매핑 적재'

    def handle(self, *args, **options):
        # 1. 파일 경로 설정
        file_path = r"C:\Users\rkgml\Downloads\01_06_260102.hwp"
        self.stdout.write(self.style.SUCCESS(f"공정 시작: {file_path}"))

        try:
            count = self.run_manual_import(file_path)
            self.stdout.write(self.style.SUCCESS(f"✅ 적재 완료: 총 {count}개의 섹션이 목차 기반으로 매핑되었습니다."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 오류 발생: {str(e)}"))

    def get_hwp_text(self, filename):
        """HWP 바이너리에서 본문 스트림 추출 및 정제"""
        f = olefile.OleFileIO(filename)
        bodytext_dirs = [d for d in f.listdir() if "BodyText" in d[0]]
        full_text = ""
        for d in bodytext_dirs:
            data = f.openstream("/".join(d)).read()
            try:
                unpacked_data = zlib.decompress(data, -15)
                full_text += unpacked_data.decode('utf-16', errors='ignore')
            except:
                continue
        # 바이너리 제어 문자 제거
        return re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', full_text)

    def run_manual_import(self, file_path):
        """목차(TOC) 데이터를 지도로 사용하여 페이지 번호를 강제 할당"""
        raw_text = self.get_hwp_text(file_path)
        
        # [데이터 지도] 제공된 매뉴얼 목차 기반 페이지 매핑 테이블
        toc_map = {
            "제1장": 1, "제2장": 4, "제3장": 10, "제4장": 12, "제5장": 15,
            "제6장": 18, "제7장": 25, "제8장": 31, "제9장": 34, "제10장": 36,
            "제11장": 40, "제12장": 42, "제13장": 44, "제14장": 46, "제15장": 50,
            "별표1": 55
        }

        # 챕터 분할 패턴
        chapter_pattern = r'(제\s?\d+\s?장\s?[^\n\r]+|\[별표\d+\][^\n\r]+)'
        parts = re.split(chapter_pattern, raw_text)
        
        ManualChunk.objects.all().delete()
        
        current_chapter = "서론/공통"
        current_page = 1
        record_count = 0

        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 장 제목 감지 시 현재 챕터와 시작 페이지 갱신
            if re.search(r'제\s?\d+\s?장|별표', part):
                current_chapter = part
                # 목차 맵에서 매칭되는 시작 페이지 탐색
                for key, page in toc_map.items():
                    # 공백 제거 후 비교하여 매칭 확률 상승
                    if key in current_chapter.replace(" ", ""):
                        current_page = page
                        break
                continue

            # 데이터베이스 적재 (텍스트가 너무 길 경우 3000자 단위로 분할 저장)
            chunk_size = 3000
            sub_chunks = [part[i:i+chunk_size] for i in range(0, len(part), chunk_size)]
            
            for content in sub_chunks:
                ManualChunk.objects.create(
                    content=content,
                    chapter_title=current_chapter,
                    page_number=current_page
                )
                record_count += 1
                
        return record_count