import os
import re
import markitdown
from sentence_transformers import SentenceTransformer, util
from openai import OpenAI

# парсинг резюме

def parse_resume(path: str) -> str:
    md = markitdown.MarkItDown()

    output = md.convert(path)
        
    return output.text_content

# сравнение резюме с вакансией (векторное)

vector_model = SentenceTransformer('all-MiniLM-L6-v2')

def match_resume_vacancy(resume: str, vacancy: str) -> float:
    resume_embs = vector_model.encode(resume, convert_to_tensor=True)
    vacancy_embs = vector_model.encode(vacancy, convert_to_tensor=True)

    return round(util.cos_sim(resume_embs, vacancy_embs).item() * 100, 2)

# сравнение резюме с вакансией (LLM)

client = OpenAI(api_key='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')

def match_with_llm(resume: str, vacancy: str) -> float:
    prompt = f"""
            Ты HR-специалист. Оцени, насколько данное резюме соответствует вакансии.
            Верни только число от 0 до 100 (процент соответствия).

            Резюме:
            {resume}

            Вакансия:
            {vacancy}
    """
    
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0
    )
    
    score = response.choices[0].message.content.strip()
    try:
        return float(score)
    except:
        return None
    
# проверка навыков

def extract_skills(text: str):
    lower_text = text.lower()
    skills = set()
    
    for skill in os.getenv('SKILLS_DICT'):
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
    
def extract_skills_llm(text: str):
    prompt = f"""
            Выдели из текста список ключевых профессиональных навыков.
            Верни их в виде JSON массива строк.

            Текст:
            {text}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    try:
        return set(eval(response.choices[0].message.content.strip()))
    except:
        return set()

def match_skills_llm(resume_text: str, job_text: str):
    resume_skills = extract_skills_llm(resume_text)
    job_skills = extract_skills_llm(job_text)

    intersection = resume_skills & job_skills
    coverage = len(intersection) / len(job_skills) * 100 if job_skills else 0

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched": intersection,
        "coverage_percent": round(coverage, 2)
    }
    
print(match_with_llm(parse_resume('/home/andrewbolgoff/programs/more_tech_vtb_hackathon/src/test_resume.docx'), parse_resume('/home/andrewbolgoff/programs/more_tech_vtb_hackathon/src/test_vacancy.docx')))