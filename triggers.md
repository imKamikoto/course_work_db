- groups:
    1. валидация имени игруппы  
    ``` sql
    CREATE OR REPLACE FUNCTION trg_validate_group_name_before_ins_upd()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NEW.name IS NULL OR btrim(NEW.name) = '' THEN
            RAISE EXCEPTION 'Поле name не может быть пустым';
        END IF;

        IF NEW.name !~ '_(\d{4})$' THEN
            RAISE EXCEPTION 'Имя группы должно оканчиваться годом _YYYY';
        END IF;

        IF length(btrim(NEW.name)) < 6 THEN
            RAISE EXCEPTION 'name слишком короткое (минимум 6 символов: ._YYYY)';
        END IF;

        RETURN NEW;
    END;
    $$;

    CREATE TRIGGER validate_mytable_ins_upd
    BEFORE INSERT OR UPDATE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION trg_validate_group_name_before_ins_upd();
    ```
    2. проверка перед удалением: если в группе состоит хотя бы один студент - отмена  
    ```sql
    CREATE OR REPLACE FUNCTION trg_validate_group_delete()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        cnt int;
    BEGIN
        select count(*) into cnt
        from people
        where group_id = OLD.id and people.type = 'S';

        if cnt > 0 then
            RAISE EXCEPTION 'Невозможно удалить группу "%", в ней состоят студенты (%)', OLD.name, cnt;
        end if;
        return OLD;
    END;
    $$;

    DROP TRIGGER IF EXISTS validate_group_delete ON groups;

    CREATE TRIGGER validate_group_delete
    BEFORE DELETE ON groups
    FOR EACH ROW
    EXECUTE FUNCTION trg_validate_group_delete();
    ```
- subjects:
    1. проверка перед удалением: есть ли ссылка на этот предмет в таблице marks  
    ```sql
    CREATE OR REPLACE FUNCTION trg_forbid_subject_delete_if_has_marks()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        cnt int;
    BEGIN
        SELECT count(*) INTO cnt
        FROM marks
        WHERE subject_id = OLD.id;

        IF cnt > 0 THEN
            RAISE EXCEPTION 'Нельзя удалить предмет "%": по нему есть оценки (%).', OLD.name, cnt;
        END IF;

        RETURN OLD;
    END;
    $$;

    DROP TRIGGER IF EXISTS subjects_forbid_delete ON subjects;

    CREATE TRIGGER subjects_forbid_delete
    BEFORE DELETE ON subjects
    FOR EACH ROW
    EXECUTE FUNCTION trg_forbid_subject_delete_if_has_marks();
    ```
    2. проверка перед вставкой: не надо
    3. проверка перед изменением: есть ли ссылка на этот предмет в таблице marks  
    ```sql
    CREATE OR REPLACE FUNCTION trg_forbid_subject_update_if_has_marks()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        cnt int;
    BEGIN
        IF NEW.name = OLD.name THEN
            RETURN NEW;
        END IF;

        SELECT count(*) INTO cnt
        FROM marks
        WHERE subject_id = OLD.id;

        IF cnt > 0 THEN
            RAISE EXCEPTION 'Нельзя изменить предмет "%": по нему есть оценки (%).', OLD.name, cnt;
        END IF;

        RETURN NEW;
    END;
    $$;

    DROP TRIGGER IF EXISTS subjects_forbid_update ON subjects;

    CREATE TRIGGER subjects_forbid_update
    BEFORE UPDATE ON subjects
    FOR EACH ROW
    EXECUTE FUNCTION trg_forbid_subject_update_if_has_marks();
    ```
- people:
    1. проверка перед удалением: есть ли ссылка на этого человека в таблице marks  
    ```sql
    CREATE OR REPLACE FUNCTION trg_forbid_person_delete_if_has_marks()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        cnt_student int;
        cnt_teacher int;
    BEGIN
        SELECT count(*) INTO cnt_student
        FROM marks
        WHERE student_id = OLD.id;

        SELECT count(*) INTO cnt_teacher
        FROM marks
        WHERE teacher_id = OLD.id;

        IF (cnt_student + cnt_teacher) > 0 THEN
            RAISE EXCEPTION
                'Нельзя удалить человека id=%: есть ссылки в marks (как студент: %, как преподаватель: %).',
                OLD.id, cnt_student, cnt_teacher;
        END IF;

        RETURN OLD;
    END;
    $$;

    DROP TRIGGER IF EXISTS people_forbid_delete ON people;

    CREATE TRIGGER people_forbid_delete
    BEFORE DELETE ON people
    FOR EACH ROW
    EXECUTE FUNCTION trg_forbid_person_delete_if_has_marks();
    ```
    2. валидация добавления / изменения: имя, фамилия, отчество, год, группа если студент, отсутсвие группы если препод  
    ```sql
    CREATE OR REPLACE FUNCTION trg_validate_people_before_ins_upd()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    DECLARE
        grp_exists int;
    BEGIN
        IF NEW.last_name IS NULL OR btrim(NEW.last_name) = '' THEN
            RAISE EXCEPTION 'Фамилия (last_name) не может быть пустой';
        END IF;

        IF NEW.first_name IS NULL OR btrim(NEW.first_name) = '' THEN
            RAISE EXCEPTION 'Имя (first_name) не может быть пустым';
        END IF;

        IF NEW.type IS NULL OR NEW.type NOT IN ('S', 'P') THEN
            RAISE EXCEPTION 'type должен быть ''S'' (студент) или ''P'' (преподаватель)';
        END IF;

        IF NEW.type = 'S' THEN
            IF NEW.group_id IS NULL THEN
                RAISE EXCEPTION 'Для студента (type=''S'') group_id обязателен';
            END IF;

            SELECT count(*) INTO grp_exists
            FROM groups
            WHERE id = NEW.group_id;

            IF grp_exists = 0 THEN
                RAISE EXCEPTION 'Указанная группа group_id=% не существует', NEW.group_id;
            END IF;

        ELSE
            IF NEW.group_id IS NOT NULL THEN
                RAISE EXCEPTION 'Для преподавателя (type=''P'') group_id должен быть NULL';
            END IF;
        END IF;

        RETURN NEW;
    END;
    $$;

    DROP TRIGGER IF EXISTS people_validate_ins_upd ON people;

    CREATE TRIGGER people_validate_ins_upd
    BEFORE INSERT OR UPDATE ON people
    FOR EACH ROW
    EXECUTE FUNCTION trg_validate_people_before_ins_upd();
    ```
- marks:
    1. проверка добавления: есть ли все поля, не должно быть скипов - те обязательно присутвует студент, учитель, предмет, оценка  
    ```sql
    CREATE OR REPLACE FUNCTION trg_validate_marks_before_ins_upd()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NEW.student_id IS NULL THEN
            RAISE EXCEPTION 'Поле student_id не может быть пустым';
        END IF;

        IF NEW.subject_id IS NULL THEN
            RAISE EXCEPTION 'Поле subject_id не может быть пустым';
        END IF;

        IF NEW.teacher_id IS NULL THEN
            RAISE EXCEPTION 'Поле teacher_id не может быть пустым';
        END IF;

        IF NEW.value not between 1 and 5 THEN
            RAISE EXCEPTION 'Значение value (оценка) должно быть в диапазоне между 1 и 5';
        END IF;
    END;
    $$;

    DROP TRIGGER IF EXISTS marks_validate_ins_upd ON marks;

    CREATE TRIGGER marks_validate_ins_upd
    BEFORE INSERT OR UPDATE ON marks
    FOR EACH ROW
    EXECUTE FUNCTION trg_validate_marks_before_ins_upd();
    ```