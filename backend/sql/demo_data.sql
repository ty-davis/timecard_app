INSERT INTO user (username, password_hash) VALUES ('tydav', '$2b$12$6jlSqYNafiPgF9p1QV1.cO4yPZIyAfSe3hhw8cuYgIM49MVZjipqC');

INSERT INTO record_attribute (name, user_id, level_num) VALUES ('home', 1, 1);
INSERT INTO record_attribute (name, parent_id, user_id, level_num) VALUES ('Timecard app', 1, 1, 2);
INSERT INTO record_attribute (name, parent_id, user_id, level_num) VALUES ('Database structure', 2, 1, 3);

INSERT INTO time_record (user_id, domain_id, category_id, title_id, timein) VALUES (1, 1, 2, 3, '2025-08-17T06:10:00.000Z');
