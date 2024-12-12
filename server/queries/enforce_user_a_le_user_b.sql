CREATE OR REPLACE FUNCTION enforce_user_a_le_user_b()
RETURNS TRIGGER AS $$ 
DECLARE
    temp INT;
BEGIN
    IF NEW.user_a > NEW.user_b THEN
        temp := NEW.user_a;
        NEW.user_a := NEW.user_b;
        NEW.user_b := temp;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_enforce_user_a_le_user_b
BEFORE INSERT OR UPDATE ON Friends
FOR EACH ROW
EXECUTE FUNCTION enforce_user_a_le_user_b();
