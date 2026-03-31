import re
import olefile
import zlib
from django.core.management.base import BaseCommand
from products.models import ManualChunk

class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = r"C:\Users\rkgml\Downloads\01_06_260102.hwp"
        self.stdout.write(self.style.WARNING("--- 페이지 중심 추출 공정 가동 ---"))
        try:
            count = self.run_manual_import(file_path)
            self.stdout.write(self.style.SUCCESS(f"✅ 성공: 총 {count}페이지 분량의 데이터가 적재되었습니다."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 오류: {str(e)}"))

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
        
        # 정제: 한글, 숫자, 기본 기호 및 페이지 구분자(-) 유지
        clean_text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s\-\(\)\[\]\%\:\.\/\>]', ' ', full_text)
        return re.sub(r'\s+', ' ', clean_text).strip()

    def run_manual_import(self, file_path):
        raw_text = self.get_clean_hwp_text(file_path)
        
        # 1. 페이지 번호 패턴 (- 1 -, - 2 - 등) 기준으로 텍스트 분할
        page_split_pattern = r'(-\s?\d+\s?-)'
        tokens = re.split(page_split_pattern, raw_text)
        
        # 2. 챕터 탐지 패턴
        chapter_pattern = r'(제\s?\d+\s?장\s?[^ ]+)'
        
        ManualChunk.objects.all().delete()
        
        current_chapter = "서론"
        last_page_num = 1
        record_count = 0

        # 분할된 토큰들을 순회하며 (본문, 페이지번호) 쌍을 맞춤
        # re.split에 괄호를 사용하면 구분자(페이지번호)도 리스트에 포함됨
        for i in range(0, len(tokens)-1, 2):
            content_part = tokens[i].strip()
            
            # 본문 내에서 새로운 챕터가 등장했는지 확인하여 상태 업데이트
            chapters_in_part = re.findall(chapter_pattern, content_part)
            if chapters_in_part:
                current_chapter = chapters_in_part[-1] # 가장 마지막에 나온 챕터 기준

            # 다음 토큰이 페이지 번호인 경우 추출
            if i + 1 < len(tokens):
                page_marker = tokens[i+1]
                page_match = re.search(r'\d+', page_marker)
                if page_match:
                    last_page_num = int(page_match.group())

            if not content_part: continue

            # DB 저장: 챕터는 중복되어도 페이지별로 레코드 생성
            ManualChunk.objects.create(
                content=content_part,
                chapter_title=current_chapter,
                page_number=last_page_num
            )
            record_count += 1
            
        return record_count