from enum import Enum


class InterviewState(Enum):
    """Interview states based on assets/diagram.mermaid"""
    START = "START"                        # A: Начало интервью
    INTRODUCTION = "INTRODUCTION"          # B: ИИ проговаривает вступление  
    LOADING_CONTEXT = "LOADING_CONTEXT"    # C: Подтягивание контекста
    PLAN_DECISION = "PLAN_DECISION"        # D: Решение об изменении плана
    UPDATING_PLAN = "UPDATING_PLAN"        # E: Обновление плана
    NEXT_STAGE = "NEXT_STAGE"              # F: Определение следующего этапа
    ENDING = "ENDING"                      # G: Запланированное завершение
    FAREWELL = "FAREWELL"                  # I: ИИ проговаривает прощание
    COMPLETE = "COMPLETE"                  # J: Конец интервью
    ASKING_QUESTION = "ASKING_QUESTION"    # H: Генерация вопроса
    WAITING_RESPONSE = "WAITING_RESPONSE"  # K: Ожидание ответа
    ANALYZING = "ANALYZING"                # L: Анализ ответа
    SKIPPING_QUESTION = "SKIPPING_QUESTION" # M: Вопрос пропущен
    UPDATING_TIMELINE = "UPDATING_TIMELINE" # N: Обновление таймлайна


class InterviewEvent(Enum):
    """Events that trigger state transitions"""
    START_INTERVIEW = "start_interview"
    INTRODUCTION_COMPLETE = "introduction_complete"
    CONTEXT_LOADED = "context_loaded"
    PLAN_CHANGE_REQUIRED = "plan_change_required"
    PLAN_CONTINUE = "plan_continue"
    PLAN_UPDATED = "plan_updated"
    END_INTERVIEW = "end_interview"
    CONTINUE_INTERVIEW = "continue_interview"
    FAREWELL_COMPLETE = "farewell_complete"
    QUESTION_GENERATED = "question_generated"
    SPEECH_RECOGNIZED = "speech_recognized"
    NO_SPEECH_DETECTED = "no_speech_detected"
    RESPONSE_ANALYZED = "response_analyzed"
    QUESTION_TIMEOUT = "question_timeout"
    TIMELINE_UPDATED = "timeline_updated"