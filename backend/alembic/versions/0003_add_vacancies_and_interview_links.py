"""Add vacancies and interview links tables

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    # Create vacancies table
    op.create_table('vacancies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('responsibilities', sa.Text(), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('original_document_path', sa.String(length=500), nullable=True),
        sa.Column('processed_document_path', sa.String(length=500), nullable=True),
        sa.Column('document_status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create interview_links table
    op.create_table('interview_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('unique_token', sa.String(length=255), nullable=False),
        sa.Column('candidate_name', sa.String(length=255), nullable=True),
        sa.Column('candidate_email', sa.String(length=255), nullable=True),
        sa.Column('candidate_phone', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('interview_session_id', sa.String(length=255), nullable=True),
        sa.Column('interview_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('interview_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('candidate_resume_path', sa.String(length=500), nullable=True),
        sa.Column('candidate_notes', sa.Text(), nullable=True),
        sa.Column('vacancy_id', sa.Integer(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['vacancy_id'], ['vacancies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_vacancies_id'), 'vacancies', ['id'], unique=False)
    op.create_index(op.f('ix_interview_links_id'), 'interview_links', ['id'], unique=False)
    op.create_index(op.f('ix_interview_links_unique_token'), 'interview_links', ['unique_token'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_interview_links_unique_token'), table_name='interview_links')
    op.drop_index(op.f('ix_interview_links_id'), table_name='interview_links')
    op.drop_index(op.f('ix_vacancies_id'), table_name='vacancies')
    
    # Drop tables
    op.drop_table('interview_links')
    op.drop_table('vacancies')
