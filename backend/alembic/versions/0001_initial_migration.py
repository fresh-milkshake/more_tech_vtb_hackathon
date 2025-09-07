"""Initial migration - create all tables

Revision ID: 0001
Revises: 
Create Date: 2025-09-05 14:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create candidates table
    op.create_table('candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('experience_years', sa.String(length=20), nullable=True),
        sa.Column('current_position', sa.String(length=200), nullable=True),
        sa.Column('current_company', sa.String(length=200), nullable=True),
        sa.Column('applied_position', sa.String(length=200), nullable=True),
        sa.Column('application_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create interviews table
    op.create_table('interviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interviewer_id', sa.String(length=255), nullable=True),
        sa.Column('position', sa.String(length=255), nullable=False),
        sa.Column('interview_type', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('current_state', sa.String(length=50), nullable=True),
        sa.Column('timeline', sa.JSON(), nullable=True),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('interview_plan', sa.JSON(), nullable=True),
        sa.Column('max_questions', sa.Integer(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('overall_feedback', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.String(length=50), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create questions table
    op.create_table('questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('difficulty', sa.Integer(), nullable=True),
        sa.Column('expected_duration', sa.Integer(), nullable=True),
        sa.Column('order_in_interview', sa.Integer(), nullable=True),
        sa.Column('is_adaptive', sa.Boolean(), nullable=True),
        sa.Column('question_type', sa.String(length=50), nullable=True),
        sa.Column('generated_by_ai', sa.Boolean(), nullable=True),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('generation_context', sa.JSON(), nullable=True),
        sa.Column('expected_keywords', sa.JSON(), nullable=True),
        sa.Column('scoring_rubric', sa.JSON(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=True),
        sa.Column('tts_audio_url', sa.String(length=500), nullable=True),
        sa.Column('audio_duration', sa.Integer(), nullable=True),
        sa.Column('asked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create responses table
    op.create_table('responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(length=500), nullable=True),
        sa.Column('audio_duration', sa.Integer(), nullable=True),
        sa.Column('stt_confidence', sa.Float(), nullable=True),
        sa.Column('stt_segments', sa.JSON(), nullable=True),
        sa.Column('language_detected', sa.String(length=10), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('technical_accuracy', sa.Float(), nullable=True),
        sa.Column('communication_clarity', sa.Float(), nullable=True),
        sa.Column('relevance', sa.Float(), nullable=True),
        sa.Column('completeness', sa.Float(), nullable=True),
        sa.Column('keywords_matched', sa.JSON(), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('confidence_level', sa.String(length=20), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('speaking_rate', sa.Float(), nullable=True),
        sa.Column('pause_analysis', sa.JSON(), nullable=True),
        sa.Column('is_complete', sa.Boolean(), nullable=True),
        sa.Column('is_analyzed', sa.Boolean(), nullable=True),
        sa.Column('analysis_version', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('flags', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create timeline_entries table
    op.create_table('timeline_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interview_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entry_type', sa.String(length=50), nullable=False),
        sa.Column('state_from', sa.String(length=50), nullable=True),
        sa.Column('state_to', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=True),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('response_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('score_awarded', sa.Float(), nullable=True),
        sa.Column('running_total_score', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_milestone', sa.Boolean(), nullable=True),
        sa.Column('flags', sa.JSON(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['response_id'], ['responses.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index('idx_interviews_candidate_id', 'interviews', ['candidate_id'])
    op.create_index('idx_interviews_status', 'interviews', ['status'])
    op.create_index('idx_interviews_current_state', 'interviews', ['current_state'])
    op.create_index('idx_interviews_created_at', 'interviews', ['created_at'])
    
    op.create_index('idx_candidates_email', 'candidates', ['email'])
    op.create_index('idx_candidates_status', 'candidates', ['status'])
    op.create_index('idx_candidates_applied_position', 'candidates', ['applied_position'])
    
    op.create_index('idx_questions_interview_id', 'questions', ['interview_id'])
    op.create_index('idx_questions_category', 'questions', ['category'])
    
    op.create_index('idx_responses_interview_id', 'responses', ['interview_id'])
    op.create_index('idx_responses_question_id', 'responses', ['question_id'])
    op.create_index('idx_responses_score', 'responses', ['score'])
    
    op.create_index('idx_timeline_entries_interview_id', 'timeline_entries', ['interview_id'])
    op.create_index('idx_timeline_entries_timestamp', 'timeline_entries', ['timestamp'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_timeline_entries_timestamp', table_name='timeline_entries')
    op.drop_index('idx_timeline_entries_interview_id', table_name='timeline_entries')
    op.drop_index('idx_responses_score', table_name='responses')
    op.drop_index('idx_responses_question_id', table_name='responses')
    op.drop_index('idx_responses_interview_id', table_name='responses')
    op.drop_index('idx_questions_category', table_name='questions')
    op.drop_index('idx_questions_interview_id', table_name='questions')
    op.drop_index('idx_candidates_applied_position', table_name='candidates')
    op.drop_index('idx_candidates_status', table_name='candidates')
    op.drop_index('idx_candidates_email', table_name='candidates')
    op.drop_index('idx_interviews_created_at', table_name='interviews')
    op.drop_index('idx_interviews_current_state', table_name='interviews')
    op.drop_index('idx_interviews_status', table_name='interviews')
    op.drop_index('idx_interviews_candidate_id', table_name='interviews')
    
    # Drop tables
    op.drop_table('timeline_entries')
    op.drop_table('responses')
    op.drop_table('questions')
    op.drop_table('interviews')
    op.drop_table('candidates')
