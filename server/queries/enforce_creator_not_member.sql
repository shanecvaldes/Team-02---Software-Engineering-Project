CREATE OR REPLACE FUNCTION enforce_creator_not_member()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if the user being added is the creator of the team
    IF EXISTS (
        SELECT 1
        FROM Teams
        WHERE Teams.team_id = NEW.team_id
          AND Teams.user_id = NEW.user_id
    ) THEN
        RAISE EXCEPTION 'The team creator cannot be a team member';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on Sound_Files table to enforce creator not being added as member
CREATE TRIGGER check_creator_not_member
BEFORE INSERT OR UPDATE ON Team_Members
FOR EACH ROW
EXECUTE FUNCTION enforce_creator_not_member();