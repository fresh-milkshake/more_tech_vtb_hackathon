from typing import Dict, Set
from app.core.states import InterviewState, InterviewEvent


class StateTransitions:
    """Defines valid state transitions based on assets/diagram.mermaid"""
    
    def __init__(self):
        self.transitions = self._build_transition_map()
    
    def _build_transition_map(self) -> Dict[InterviewState, Dict[InterviewEvent, InterviewState]]:
        """Build state transition map based on the Mermaid diagram"""
        return {
            # A → B: Start interview → AI Introduction
            InterviewState.START: {
                InterviewEvent.START_INTERVIEW: InterviewState.INTRODUCTION
            },
            
            # B → C: AI Introduction → Loading Context
            InterviewState.INTRODUCTION: {
                InterviewEvent.INTRODUCTION_COMPLETE: InterviewState.LOADING_CONTEXT
            },
            
            # C → D: Loading Context → Plan Decision
            InterviewState.LOADING_CONTEXT: {
                InterviewEvent.CONTEXT_LOADED: InterviewState.PLAN_DECISION
            },
            
            # D → E or D → F: Plan Decision → Update Plan OR Next Stage
            InterviewState.PLAN_DECISION: {
                InterviewEvent.PLAN_CHANGE_REQUIRED: InterviewState.UPDATING_PLAN,
                InterviewEvent.PLAN_CONTINUE: InterviewState.NEXT_STAGE
            },
            
            # E → F: Update Plan → Next Stage
            InterviewState.UPDATING_PLAN: {
                InterviewEvent.PLAN_UPDATED: InterviewState.NEXT_STAGE
            },
            
            # F → G or F → H: Next Stage → End OR Ask Question
            InterviewState.NEXT_STAGE: {
                InterviewEvent.END_INTERVIEW: InterviewState.ENDING,
                InterviewEvent.CONTINUE_INTERVIEW: InterviewState.ASKING_QUESTION
            },
            
            # G → I: Ending → Farewell
            InterviewState.ENDING: {
                InterviewEvent.END_INTERVIEW: InterviewState.FAREWELL
            },
            
            # I → J: Farewell → Complete
            InterviewState.FAREWELL: {
                InterviewEvent.FAREWELL_COMPLETE: InterviewState.COMPLETE
            },
            
            # H → K: Ask Question → Wait Response
            InterviewState.ASKING_QUESTION: {
                InterviewEvent.QUESTION_GENERATED: InterviewState.WAITING_RESPONSE
            },
            
            # K → L or K → M: Wait Response → Analyze OR Skip Question
            InterviewState.WAITING_RESPONSE: {
                InterviewEvent.SPEECH_RECOGNIZED: InterviewState.ANALYZING,
                InterviewEvent.NO_SPEECH_DETECTED: InterviewState.SKIPPING_QUESTION,
                InterviewEvent.QUESTION_TIMEOUT: InterviewState.SKIPPING_QUESTION
            },
            
            # L → N: Analyze → Update Timeline
            InterviewState.ANALYZING: {
                InterviewEvent.RESPONSE_ANALYZED: InterviewState.UPDATING_TIMELINE
            },
            
            # M → N: Skip Question → Update Timeline
            InterviewState.SKIPPING_QUESTION: {
                InterviewEvent.QUESTION_TIMEOUT: InterviewState.UPDATING_TIMELINE
            },
            
            # N → D: Update Timeline → Plan Decision (loop)
            InterviewState.UPDATING_TIMELINE: {
                InterviewEvent.TIMELINE_UPDATED: InterviewState.PLAN_DECISION
            },
            
            # J: Complete (terminal state)
            InterviewState.COMPLETE: {}
        }
    
    def is_valid_transition(self, current_state: InterviewState, event: InterviewEvent) -> bool:
        """Check if transition is valid"""
        return event in self.transitions.get(current_state, {})
    
    def get_next_state(self, current_state: InterviewState, event: InterviewEvent) -> InterviewState:
        """Get next state for given current state and event"""
        if not self.is_valid_transition(current_state, event):
            raise ValueError(f"Invalid transition: {event} from {current_state}")
        
        return self.transitions[current_state][event]
    
    def get_valid_events(self, current_state: InterviewState) -> Set[InterviewEvent]:
        """Get all valid events for current state"""
        return set(self.transitions.get(current_state, {}).keys())
    
    def is_terminal_state(self, state: InterviewState) -> bool:
        """Check if state is terminal (no outgoing transitions)"""
        return len(self.transitions.get(state, {})) == 0