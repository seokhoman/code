import re
from collections import defaultdict

def clean_text(text):
    """
    불필요한 단어 및 문장을 제거하는 함수
    """
    remove_phrases = ["사진", "파일", "초대", "안녕하십니까", "구호", "이름", "공지사항", "학부모님 안내"]
    for phrase in remove_phrases:
        text = re.sub(f".*{phrase}.*", "", text)
    return text.strip()

def extract_schedules(chat_text):
    date_pattern = re.compile(r'\d{4}년\s\d{1,2}월\s\d{1,2}일')
    task_pattern = re.compile(r'(\d{1,2}월\s\d{1,2}일).*?(\d{1,2}:\d{2})?.*?(공지|회의|일정|마감|제출|발표|시험|대회|설명회|봉사)')
    
    schedules = defaultdict(list)
    
    for match in task_pattern.finditer(chat_text):
        date, time, event_type = match.groups()
        entry = f"{event_type}"
        if time:
            entry += f" ({time})"
        schedules[date].append(entry)
    
    sorted_schedules = sorted(schedules.items())
    
    result = ""
    for date, events in sorted_schedules:
        result += f"\n📌 {date}\n"
        for event in events:
            result += f"  - {event}\n"
    
    return clean_text(result.strip())

# 🔹 파일에서 대화 내용 읽기
file_path = r"C:\Users\T470\Downloads\대화내용.txt"

with open(file_path, "r", encoding="utf-8") as file:
    chat_text = file.read()

# 🔹 일정 추출 및 출력
print(extract_schedules(chat_text))
