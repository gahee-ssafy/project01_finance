import re
from django.core.management.base import BaseCommand
from products.models import ManualChunk

class Command(BaseCommand):
    help = "매뉴얼 텍스트를 장(Chapter) 단위로 잘라 DB에 적재합니다."

    def handle(self, *args, **options):
        # r-string을 유지하되 경로 확인을 한 번 더 수행하십시오.
        file_path = r"C:\Users\rkgml\Desktop\project01_finance\back\01_06_260102.txt"
        
        self.stdout.write(self.style.WARNING("--- 매뉴얼 적재 프로세스 가동 ---"))
        
        try:
            self.ingest_manual_to_db_simple(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"종합 에러 발생: {str(e)}"))

    def ingest_manual_to_db_simple(self, file_path):  # self 인자 추가
        # 1. 파일 읽기
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ 파일을 찾을 수 없습니다: {file_path}"))
            return

        # 2. 기존 데이터 초기화 (루프 밖으로 이동)
        # 새로운 적재를 시작하기 전에 한 번만 수행합니다.
        ManualChunk.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("기존 매뉴얼 데이터를 초기화했습니다."))

        # 3. '제 N 장' 패턴 분할 (파일 첫머리 대응을 위해 수정)
        # 양쪽 공백 제거 후 첫 장부터 잘 자르기 위해 패턴을 유연하게 잡습니다.
        chapter_splits = re.split(r'\n\s*(?=제\s?\d+\s?장)', full_text.strip())

        count = 0
        for section in chapter_splits:
            section = section.strip()
            if not section:
                continue

            # 4. 장 제목 추출
            lines = section.split('\n')
            chapter_title = lines[0].strip() if lines else "제목 없음"

            # 5. DB 저장
            ManualChunk.objects.create(
                content=section,
                # embedding=None,  # 벡터화 보류 (null)
                chapter_title=chapter_title,
                # page_number=None
            )
            count += 1
            
            if count % 5 == 0:
                self.stdout.write(f"적재 중... ({count}개 완료)")

        self.stdout.write(self.style.SUCCESS(f"✅ 총 {count}개의 장(Chapter) 단위 원문이 DB에 성공적으로 적재되었습니다."))