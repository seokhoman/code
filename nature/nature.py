import re
from konlpy.tag import Okt
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

# 파일 이름 설정
input_file = "KakaoTalk_20250328_1853_34_224_group.txt"
output_file = "todo_list.txt"

# Okt 형태소 분석기 초기화
okt = Okt()

def clean_message(line):
    """카카오톡 메시지에서 이름, 시간 정보 제거 + '이모티콘' 단어만 제거"""
    line = re.sub(r"\[\d{5} .*?\] \[.*?\] ", "", line)  # [이름] [시간] 제거
    line = line.replace("이모티콘", "").strip()  # "이모티콘" 단어만 제거
    return line


def extract_nouns(text):
    """문장에서 명사 추출"""
    words = okt.nouns(text)
    return " ".join([word for word in words if len(word) > 1])  # 한 글자 제거 후 띄어쓰기 구분

def is_schedule_related(sentence):
    """일정과 관련된 문장인지 판단"""
    schedule_keywords = ["내일", "모레", "시간", "장소", "언제", "약속", "계획", "일정"]
    return any(keyword in sentence for keyword in schedule_keywords)

def process_chat_file(input_file, output_file):
    """카카오톡 대화 파일을 처리하여 날짜별 중요한 키워드 + 일정 요약 저장"""
    if not os.path.exists(input_file):
        print(f"파일 {input_file}이(가) 존재하지 않습니다.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chat_data = {}  # 날짜별 대화 저장
    schedule_summaries = defaultdict(list)  # 날짜별 일정 관련 문장 저장
    current_date = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 날짜 감지 (ex: "--------------- 2025년 1월 3일 금요일 ---------------")
        date_match = re.match(r"-+\s*(\d{4})년 (\d{1,2})월 (\d{1,2})일.*-+", line)
        if date_match:
            year, month, day = date_match.groups()
            current_date = f"{year}.{int(month):02}.{int(day):02}"
            chat_data[current_date] = []
            continue

        if current_date:
            # 메시지 클리닝 (이모티콘 제거 포함)
            text = clean_message(line)
            if text:
                chat_data[current_date].append(extract_nouns(text))
                
                # 일정 관련 문장 저장
                if is_schedule_related(text):
                    schedule_summaries[current_date].append(text)

    # 날짜별 텍스트를 하나의 문장으로 합침
    date_texts = {date: " ".join(texts) for date, texts in chat_data.items()}

    # TF-IDF 계산
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(date_texts.values())
    feature_names = vectorizer.get_feature_names_out()

    # TF-IDF 점수 계산 후 상위 키워드 추출
    important_keywords = {}
    for i, date in enumerate(date_texts.keys()):
        scores = tfidf_matrix[i].toarray().flatten()
        top_indices = scores.argsort()[-5:][::-1]  # 점수가 높은 상위 5개 단어 선택
        top_keywords = [feature_names[idx] for idx in top_indices if scores[idx] > 0]
        important_keywords[date] = top_keywords

    # 결과 저장
    with open(output_file, "w", encoding="utf-8") as f:
        for date, keywords in sorted(important_keywords.items()):
            f.write(f"{date}: {', '.join(keywords)}\n")
            if schedule_summaries[date]:
                f.write(f"  📌 일정 요약: {schedule_summaries[date][0]}\n")  # 첫 번째 일정 관련 문장 저장

    print(f"중요 키워드 및 일정 요약이 {output_file}에 저장되었습니다.")

# 실행
process_chat_file(input_file, output_file)
