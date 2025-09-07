CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE INDEX IF NOT EXISTS idx_interviews_candidate_id ON interviews(candidate_id);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
CREATE INDEX IF NOT EXISTS idx_interviews_current_state ON interviews(current_state);
CREATE INDEX IF NOT EXISTS idx_interviews_created_at ON interviews(created_at);

CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_applied_position ON candidates(applied_position);

CREATE INDEX IF NOT EXISTS idx_questions_interview_id ON questions(interview_id);
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);

CREATE INDEX IF NOT EXISTS idx_responses_interview_id ON responses(interview_id);
CREATE INDEX IF NOT EXISTS idx_responses_question_id ON responses(question_id);
CREATE INDEX IF NOT EXISTS idx_responses_score ON responses(score);

CREATE INDEX IF NOT EXISTS idx_timeline_entries_interview_id ON timeline_entries(interview_id);
CREATE INDEX IF NOT EXISTS idx_timeline_entries_timestamp ON timeline_entries(timestamp);

/*

INSERT INTO candidates (id, first_name, last_name, email, applied_position, status)
VALUES (
    uuid_generate_v4(),
    'John',
    'Doe', 
    'john.doe@example.com',
    'Software Developer',
    'applied'
) ON CONFLICT (email) DO NOTHING;

INSERT INTO interviews (id, candidate_id, position, status, scheduled_at, max_questions)
SELECT 
    uuid_generate_v4(),
    c.id,
    'Software Developer',
    'scheduled',
    NOW() + INTERVAL '1 day',
    5
FROM candidates c 
WHERE c.email = 'john.doe@example.com'
ON CONFLICT DO NOTHING;
*/

CREATE OR REPLACE VIEW interview_summaries AS
SELECT 
    i.id,
    i.candidate_id,
    CONCAT(c.first_name, ' ', c.last_name) as candidate_name,
    c.email as candidate_email,
    i.position,
    i.status,
    i.current_state,
    i.scheduled_at,
    i.started_at,
    i.ended_at,
    i.total_score,
    i.recommendation,
    COUNT(r.id) as questions_answered,
    i.max_questions,
    CASE 
        WHEN i.max_questions > 0 THEN (COUNT(r.id)::float / i.max_questions * 100)
        ELSE 0
    END as progress_percentage
FROM interviews i
JOIN candidates c ON i.candidate_id = c.id
LEFT JOIN responses r ON i.id = r.interview_id
GROUP BY i.id, c.id, c.first_name, c.last_name, c.email;

CREATE OR REPLACE FUNCTION calculate_avg_interview_duration()
RETURNS INTERVAL AS $$
BEGIN
    RETURN (
        SELECT AVG(ended_at - started_at)
        FROM interviews 
        WHERE status = 'completed' 
        AND started_at IS NOT NULL 
        AND ended_at IS NOT NULL
    );
END;
$$ LANGUAGE plpgsql;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hr_avatar;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hr_avatar;
GRANT USAGE ON SCHEMA public TO hr_avatar;

INSERT INTO public.init_log (message, created_at) 
VALUES ('HR Avatar database initialized successfully', NOW())
ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS init_log (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);