--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;

DROP TABLE IF EXISTS public.question;
DROP SEQUENCE IF EXISTS public.question_id_seq;
CREATE TABLE question (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    view_number integer,
    vote_number integer,
    title text,
    message text,
    image text,
    answer_count integer
);

DROP TABLE IF EXISTS public.answer;
DROP SEQUENCE IF EXISTS public.answer_id_seq;
CREATE TABLE answer (
    id serial NOT NULL,
    submission_time timestamp without time zone,
    vote_number integer,
    question_id integer,
    message text,
    image text
);

DROP TABLE IF EXISTS public.comment;
DROP SEQUENCE IF EXISTS public.comment_id_seq;
CREATE TABLE comment (
    id serial NOT NULL,
    question_id integer,
    answer_id integer,
    message text,
    submission_time timestamp without time zone,
    edited_count integer
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
DROP SEQUENCE IF EXISTS public.tag_id_seq;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);


ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
    ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id)
    ON UPDATE CASCADE ON DELETE CASCADE;


-- Initialize question table:

INSERT INTO question VALUES (1, '2017-05-19 08:22:00', 29, 3, 'How do orcs reproduce?', 'I had this question ever since I was a little girl: are there baby orcs? If so, where do they come from? There must be lady orcs as well, right? Do they look like males?', 'q_id_1_orc_mate.jpg', 5);
INSERT INTO question VALUES (2, '2017-03-02 09:19:10', 36, 6, 'Why is President Trump the color he is?', 'I mean he has this kinda oringie shade, does he have som sort of condition or what? Or does he just eat a lot of carrots? I heard that does that to you.', 'q_id_2_trump.jpg', 4);
INSERT INTO question VALUES (3, '2017-04-15 18:29:23', 7, 0, 'Where is my baboon?', 'I lost my beloved pet a few days ago. Please help me!', 'q_id_3_baboon.jpg', 2);
INSERT INTO question VALUES (4, '2016-04-12 10:15:24', 5, 8, 'Are there satanists in Hungary?', 'I heard that Hungary is a very religious Catholic country and nobody worships the beast there. Should I move there?', 'q_id_4_SaddamDevil.jpg', 5);
INSERT INTO question VALUES (5, '2017-04-28 05:45:10', 0, 2, 'Can you warm your baby chicks in the microwave?', 'Unfortunately we ate our family hen but now our chicks are always cold beacuse theres noone to warm them. Would it be okay to put them in the microwave for a couple of minutes, like on a low setting? Serious answers pleeease', NULL, 3);
INSERT INTO question VALUES (6, '2012-02-01 03:57:32', 23, 4, 'What is my IP adress?', 'Hey guys, can someone please tell me my IP address? I cannot find it anywhere.', NULL, 5);
INSERT INTO question VALUES (7, '2016-01-30 01:23:53', 12, 3, 'I killed my hamster today by accident.', 'Am I going to prison now? Please ANSWER', 'q_id_7_hamster.jpg', 2);
INSERT INTO question VALUES (8, '2013-11-26 02:01:40', 0, 1, 'Is Gandalf a woman?', 'I am not sure.. please help me!! He was my role model..', 'q_id_8_gandalf.jpg', 2);
INSERT INTO question VALUES (9, '2013-04-15 09:29:43', 29, 12, 'Is the Earth really flat?', 'My friend told me that..Im not sure', 'q_id_9_flat.jpg', 2);
INSERT INTO question VALUES (10, '2017-04-28 12:14:32', 2, 5, 'Can someone sell me weed?', 'Hey guys can someone please mail me weed i dont know where to buy it', 'q_id_10_weed.gif', 4);
INSERT INTO question VALUES (11, '2016-12-28 23:53:21', 5, 3, 'Can my girlfriend be fregnant???', 'We did yd some nasty stuff and I dont really know.. please help', 'q_id_11_prego.jpg', 3);
INSERT INTO question VALUES (12, '2017-04-28 12:23:35', 18, 10, 'My cat thinks that I cheat on him..how can i explain the situation?', 'I have to do something! He will leave me soon:(((', 'q_id_12_cat_cheat.jpg', 1);
SELECT pg_catalog.setval('question_id_seq', 12, true);


-- Initialize answer table:

INSERT INTO answer VALUES (1, '2017-05-23 08:25:22', 3, 1, 'LOL what is this question?', 'a_id_1_ugluk.jpg');
INSERT INTO answer VALUES (2, '2017-05-24 09:25:52', 5, 1, 'It is a though topic I do not think you are old enough to discuss it...', NULL);
INSERT INTO answer VALUES (3, '2017-05-19 10:25:32', 2, 1, 'God you guys are such neeeerds.', NULL);
INSERT INTO answer VALUES (4, '2017-05-20 11:25:24', 3, 1, 'No, orcs basically are zombie elves dug up from the ground with some back magic.', NULL);
INSERT INTO answer VALUES (5, '2017-05-21 12:35:53', 0, 1, 'Actually, it is just the uruk-hai that born from the ground, regular orcs indeed reproduce sexually.', NULL);
INSERT INTO answer VALUES (6, '2017-05-23 13:45:23', 6, 2, 'HE IS A SPACE LIZARDMAN ELECTED PRESIDENT BY THE CIA!!! WAKE UP SHEEPLE', NULL);
INSERT INTO answer VALUES (7, '2017-03-30 05:55:22', 5, 2, 'I think it is just a fake tan gone wrong. very wrong', NULL);
INSERT INTO answer VALUES (8, '2017-03-23 23:22:42', 2, 2, 'Definitely carrots!', NULL);
INSERT INTO answer VALUES (9, '2017-04-29 21:23:21', 0, 2, 'He will make America great again, stop asking these stupid questions!', NULL);
INSERT INTO answer VALUES (10, '2017-05-23 18:21:20', 1, 3, 'I believe I saw him in the downtown yesterday.', 'a_id_10_map_baboon.jpg');

INSERT INTO answer VALUES (11, '2017-05-23 10:25:32', 12, 3, 'Be careful! They can be dangerous!', 'a_id_11_BABOON_TEETH.jpg');
INSERT INTO answer VALUES (12, '2017-05-27 08:22:00', 4, 4, 'See I could find these monsters, do not go near to that country', 'a_id_12_buso.jpg');
INSERT INTO answer VALUES (13, '2017-05-22 09:25:52', 6, 4, 'bojler elado', NULL);
INSERT INTO answer VALUES (14, '2017-05-09 08:22:00', 12, 4, 'There are some but do not move here because we do not like immigrants', NULL);
INSERT INTO answer VALUES (15, '2017-05-06 18:21:20', 0, 4, 'Hungary is one of the last truly Catholic countries enduring all attacks from the failing Western world. Indeed only good Catholic people live here (plus the godless liberals but were getting rid of them soon)', NULL);
INSERT INTO answer VALUES (16, '2017-05-15 11:25:24', 4, 4, 'What a bullshit! In the 21st century there is no such things as satanists', NULL);
INSERT INTO answer VALUES (17, '2017-05-21 08:22:00', 4, 5, 'asdfadsfasdfadsfasdfasd', NULL);
INSERT INTO answer VALUES (18, '2017-05-25 23:22:42', 0, 5, 'Are you some special kind of idiot?', NULL);
INSERT INTO answer VALUES (19, '2017-05-02 08:22:00', 1, 5, 'Yes, that is the way to keep them warm, you do not want your chicks to catch a cold. Worked for me', NULL);
INSERT INTO answer VALUES (20, '2017-05-12 09:25:52', 6, 6, 'I dont know yours, but here, you can use mine 222.67.111.94. Sharing is caring', NULL);

INSERT INTO answer VALUES (21, '2017-05-23 10:25:32', 7, 6, 'aafdsfasdfdasgasdfadsfadsf', NULL);
INSERT INTO answer VALUES (22, '2017-05-27 08:22:00', 5, 6, 'asdfadsfasdfadsfasdfasd', NULL);
INSERT INTO answer VALUES (23, '2017-05-22 09:25:52', 12, 6, 'You can check it on google', NULL);
INSERT INTO answer VALUES (24, '2017-05-09 08:22:00', 2, 6, 'open a command prompt and type ipconfig', NULL);
INSERT INTO answer VALUES (25, '2017-05-06 18:21:20', 3, 7, 'I called the cops you sick bastard, they are on the way', NULL);
INSERT INTO answer VALUES (26, '2017-05-15 11:25:24', 0, 7, 'ROFL you are safe bro', NULL);
INSERT INTO answer VALUES (27, '2017-05-21 08:22:00', 5, 8, 'Gandalf the grey is a wise wizard. Dont you dare to make fun of him!!!', 'a_id_27_gandi.gif');
INSERT INTO answer VALUES (28, '2017-05-25 23:22:42', 7, 8, 'yep he is a she, sorry bro..', NULL);
INSERT INTO answer VALUES (29, '2017-05-02 08:22:00', 0, 9, 'The human dumbness , oh god please stop', NULL);
INSERT INTO answer VALUES (30, '2017-05-12 09:25:52', 3, 9, 'I agree with you it is so logical!', NULL);

INSERT INTO answer VALUES (31, '2017-05-23 10:25:32', 2, 10, 'Sure thing dude, just give me youe credit card number and pin', NULL);
INSERT INTO answer VALUES (32, '2017-05-27 08:22:00', 23, 10, 'Delete the question dumb kid, the police can catch it', NULL);
INSERT INTO answer VALUES (33, '2017-05-22 09:25:52', 3, 10, 'Write me on fb I have a lil pot;)', NULL);
INSERT INTO answer VALUES (34, '2017-05-09 08:22:00', 3, 10, 'Listen Jesus and do not do that boy!!', NULL);
INSERT INTO answer VALUES (35, '2017-05-06 18:21:20', 2, 11, 'You have to take responsibility for the unborn child!!!!', NULL);
INSERT INTO answer VALUES (36, '2017-05-15 11:25:24', 1, 11, 'You suck haha, dumb kid', NULL);
INSERT INTO answer VALUES (37, '2017-05-21 08:22:00', 0, 11, 'It depends.. what did you do?', NULL);
INSERT INTO answer VALUES (38, '2017-05-25 23:22:42', 0, 12, 'Surprise him with a vacation, he will forgive you for sure:)', 'a_id_38_cat_vac.jpg');
SELECT pg_catalog.setval('answer_id_seq', 38, true);


-- Initialize comment table:

INSERT INTO comment VALUES (1, 1, NULL, 'Please clarify the question as it is too vague!', '2017-05-22 05:49:00', 0);
INSERT INTO comment VALUES (2, 1, NULL, 'I believe it was clarified well enough.', '2017-05-23 05:52:05', 5);
INSERT INTO comment VALUES (3, 1, NULL, 'Ah never mind, I just understood.', '2017-05-21 06:21:16', 14);
INSERT INTO comment VALUES (4, NULL, 2, 'This answer was quiet comprehensive, I like it.', '2017-05-21 18:55:30', 0);
INSERT INTO comment VALUES (5, NULL, 2, 'I like it too.', '2017-05-24 16:52:50', 1);
INSERT INTO comment VALUES (6, NULL, 2, 'I could have given a better answer but then I realized I could not add much to it, so I spared the effort. Anyway, keep up the good work.', '2017-05-23 17:25:02', 2);
INSERT INTO comment VALUES (7, NULL, 3, 'Just wanted to add a single comment.', '2017-05-21 16:55:00', 3);
SELECT pg_catalog.setval('comment_id_seq', 7, true);


-- Initialize tag table:

INSERT INTO tag VALUES (1, 'fantasy');
INSERT INTO tag VALUES (2, 'animal');
INSERT INTO tag VALUES (3, 'politics');
INSERT INTO tag VALUES (4, 'philosophy');
INSERT INTO tag VALUES (5, 'IT');
INSERT INTO tag VALUES (6, 'love-life');
INSERT INTO tag VALUES (7, 'mystery');
INSERT INTO tag VALUES (8, 'hallucinogens');
SELECT pg_catalog.setval('tag_id_seq', 8, true);


-- Initialize question_tag table:

INSERT INTO question_tag VALUES (1, 1);
INSERT INTO question_tag VALUES (1, 6);
INSERT INTO question_tag VALUES (1, 7);
INSERT INTO question_tag VALUES (2, 3);
INSERT INTO question_tag VALUES (2, 7);
INSERT INTO question_tag VALUES (3, 2);
INSERT INTO question_tag VALUES (4, 4);
INSERT INTO question_tag VALUES (5, 2);
INSERT INTO question_tag VALUES (6, 5);
INSERT INTO question_tag VALUES (7, 2);
INSERT INTO question_tag VALUES (8, 1);
INSERT INTO question_tag VALUES (8, 4);
INSERT INTO question_tag VALUES (8, 7);
INSERT INTO question_tag VALUES (9, 4);
INSERT INTO question_tag VALUES (9, 7);
INSERT INTO question_tag VALUES (10, 8);
INSERT INTO question_tag VALUES (11, 2);
INSERT INTO question_tag VALUES (12, 2);
INSERT INTO question_tag VALUES (12, 6);
