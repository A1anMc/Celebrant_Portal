"""Add CRM enhancements

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add CRM fields to existing couples table (backward compatible)
    op.add_column('couples', sa.Column('lead_stage', sa.String(50), nullable=True))
    op.add_column('couples', sa.Column('lead_source', sa.String(100), nullable=True))
    op.add_column('couples', sa.Column('follow_up_date', sa.Date(), nullable=True))
    op.add_column('couples', sa.Column('estimated_value', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('couples', sa.Column('notes', sa.Text(), nullable=True))
    
    # Create communication log table
    op.create_table('communication_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('communication_type', sa.String(50), nullable=False),
        sa.Column('subject', sa.String(200), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communication_log_id'), 'communication_log', ['id'], unique=False)
    
    # Create tasks/reminders table
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('couple_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    
    # Create email templates table
    op.create_table('email_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('subject', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('template_type', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)


def downgrade() -> None:
    # Remove new tables
    op.drop_index(op.f('ix_email_templates_id'), table_name='email_templates')
    op.drop_table('email_templates')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index(op.f('ix_communication_log_id'), table_name='communication_log')
    op.drop_table('communication_log')
    
    # Remove new columns from couples table
    op.drop_column('couples', 'notes')
    op.drop_column('couples', 'estimated_value')
    op.drop_column('couples', 'follow_up_date')
    op.drop_column('couples', 'lead_source')
    op.drop_column('couples', 'lead_stage')
