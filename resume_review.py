import re
import markitdown
import os
from dotenv import load_dotenv
import asyncio

from sentence_transformers import SentenceTransformer, util
from openai import AsyncOpenAI

load_dotenv()

# парсинг документов
def parse_document(path: str) -> str:
    md = markitdown.MarkItDown()
    output = md.convert(path)
    return output.text_content

# сравнение резюме с вакансией (векторное)
vector_model = SentenceTransformer('all-MiniLM-L6-v2')

def match_resume_vacancy(resume: str, vacancy: str) -> float:
    resume_embs = vector_model.encode(resume, convert_to_tensor=True)
    vacancy_embs = vector_model.encode(vacancy, convert_to_tensor=True)
    return round(util.cos_sim(resume_embs, vacancy_embs).item() * 100, 2)

SKILLS_DICT = os.getenv('SKILLS_DICT')
KEY = os.getenv('OPENAI_API_NIKITA')
client = AsyncOpenAI(api_key=KEY)

# --- асинхронные функции ---

async def match_resume_vacancy_llm(resume: str, vacancy: str) -> str:
    prompt = f"""
    Ты HR-специалист. Оцени, насколько данное резюме соответствует вакансии.
    Поставь оценку от 0 до 100 и расскажи подробно, почему именно такую оценку ты поставил.
    Сделай ответ максимально кратким. Без форматирования и перечислений.
    Резюме:
    {resume}
    Вакансия:
    {vacancy}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def extract_skills(text: str):
    lower_text = text.lower()
    skills = set()
    for skill in SKILLS_DICT:
        if re.search(r'\b' + re.escape(skill) + r'\b', lower_text):
            skills.add(skill)
    return skills

def match_skills(resume: str, vacancy: str):
    resume_skills = extract_skills(resume)
    vacancy_skills = extract_skills(vacancy)
    inter = resume_skills & vacancy_skills
    cov = len(inter) / len(vacancy_skills) * 100 if vacancy_skills else 0
    return {
        'resume_skills': resume_skills,
        'vacancy_skills': vacancy_skills,
        'match': inter,
        'cov': round(cov, 2)
    }

async def extract_skills_llm(text: str) -> str:
    prompt = f"""
    Выдели из текста список ключевых профессиональных навыков.
    Верни их в виде JSON массива строк.

    Текст:
    {text}
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def match_skills_llm(resume_text: str, job_text: str) -> str:
    resume_skills = await extract_skills_llm(resume_text)
    job_skills = await extract_skills_llm(job_text)
    
    prompt = f"""
    Сравни на сколько совпадают навыки, требуемые для вакансии с навыками в резюме.
    Ответь насколько совпадают навыки от 0 до 100 и скажи каких навыков не хватает.
    Ответ сделай кратким, без пунктов и форматирования. 
    Если навыки не совпадают один в один, но их смысл одинаковый, не упоминай их.
    Навыки из резюме:
    {resume_skills}
    Навыки из вакансии:
    {job_skills}
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# --- запуск тестов ---
async def main():
    print("TESTING...")
    print('#'*30)

    print('---noLLM pipeline---')
    print("Matching resume: ")
    print(match_resume_vacancy(
        parse_document('/root/backend/uploads/resume/test_resume.docx'),
        parse_document('/root/backend/uploads/vacancies/test_vacancy.docx')
    ))
    print("Matching skills: ")
    print(match_skills(
        parse_document('/root/backend/uploads/resume/test_resume.docx'),
        parse_document('/root/backend/uploads/vacancies/test_vacancy.docx')
    ))

    print('#'*30)
    print('---LLM pipeline---')
    print("Matching resume: ")
    print(await match_resume_vacancy_llm(
        parse_document('/root/backend/uploads/resume/test_resume.docx'),
        parse_document('/root/backend/uploads/vacancies/test_vacancy.docx')
    ))
    print("Matching skills: ")
    print(await match_skills_llm(
        parse_document('/root/backend/uploads/resume/test_resume.docx'),
        parse_document('/root/backend/uploads/vacancies/test_vacancy.docx')
    ))

if __name__ == '__main__':
    asyncio.run(main())