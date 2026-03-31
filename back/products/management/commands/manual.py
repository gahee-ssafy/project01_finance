import re
import olefile
import zlib
from django.core.management.base import BaseCommand
from products.models import ManualChunk

class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = r"C:\Users\rkgml\Downloads\01_06_260102.hwp"
        self.stdout.write(self.style.WARNING("--- 디버깅 모드 가동 ---"))
        try:
            self.run_manual_import(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"에러: {str(e)}"))

    def get_clean_hwp_text(self, filename):
        f = olefile.OleFileIO(filename)
        bodytext_dirs = [d for d in f.listdir() if "BodyText" in d[0]]
        full_text = ""
        for d in bodytext_dirs:
            data = f.openstream("/".join(d)).read()
            try:
                unpacked_data = zlib.decompress(data, -15)
                full_text += unpacked_data.decode('utf-16', errors='ignore')
            except: continue
        
        # [디버깅 포인트] 정제 범위를 넓힘 (하이픈 필수 포함)
        clean_text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s\-\(\)\[\]\%\.]', ' ', full_text)
        return re.sub(r'\s+', ' ', clean_text).strip()

    def run_manual_import(self, file_path):
        raw_text = self.get_clean_hwp_text(file_path)
        
        # 패턴 유연화: 하이픈 앞뒤 공백 및 다양한 형태 대응
        # 하이픈(-) 또는 점(.)으로 둘러싸인 숫자 매칭 시도
        page_pattern = r'[-\. ]\s?(\d+)\s?[-\. ]'
        chapter_pattern = r'(제\s?\d+\s?장\s?[^ ]+)'
        
        parts = re.split(chapter_pattern, raw_text)
        ManualChunk.objects.all().delete()
        
        current_chapter = "서론"
        current_page = 1
        
        for i, part in enumerate(parts):
            if not part.strip(): continue
            if re.match(chapter_pattern, part):
                current_chapter = part
                continue

            # [디버깅 출력] 각 조각의 마지막 100자를 출력하여 실제 페이지 번호 형태 확인
            debug_tail = part[-100:]
            found_pages = re.findall(page_pattern, debug_tail)
            
            if found_pages:
                current_page = int(found_pages[-1])
                # 페이지 번호 발견 시 터미널에 보고
                self.stdout.write(f"[{current_chapter}] 페이지 발견: {current_page}")
            else:
                # 못 찾았을 경우 꼬리 텍스트 노출 (원인 분석용)
                self.stdout.write(self.style.NOTICE(f"페이지 미발견 구역 꼬리: ...{debug_tail}"))

            ManualChunk.objects.create(
                content=part,
                chapter_title=current_chapter,
                page_number=current_page
            )
        return len(parts)