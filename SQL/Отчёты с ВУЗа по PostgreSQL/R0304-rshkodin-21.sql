SELECT * FROM public.my_5_table

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(1, 1000000);

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(2, 1000000),
(3, 10000),
(40, 45000),
(12, 200000);

INSERT INTO my_5_table
(my_id, test_field)
SELECT 22, 50000
UNION ALL
SELECT 26, 51000
UNION ALL 
SELECT 24, 52000
UNION ALL 
SELECT 25, 53000

INSERT INTO my_5_test_table
(my_id, test_field)
SELECT 
   my_id, test_field
FROM my_5_table
WHERE
   my_id > 10

SELECT * FROM my_5_test_table

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(31, 800000);

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(32, 850000);

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(33, 860000);

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(34, 870000);

INSERT INTO my_5_table
(my_id, test_field)
VALUES
(35, 880000);

SELECT 
   my_id, test_field
INTO my_5_copy
FROM my_5_table
WHERE
   my_id > 20;

SELECT * FROM my_5_table

UPDATE my_5_table
SET
	sname = 'Sidorov'
WHERE my_id < 33;

UPDATE my_5_table
SET
   sname = 'Petrov'
WHERE
   (30 < my_id) AND (my_id < 43);

UPDATE my_5_table
SET
	test_field = test_field * 1.2
WHERE
   my_id BETWEEN 2 AND 24;

UPDATE my_5_table
SET
   test_field = test_field * 1.20
WHERE
   my_id < 22;

UPDATE my_5_table
SET
   test_field = test_field * 1.05,
   sname = sname || ' А.'
WHERE
   my_id >= 22;

CREATE TABLE IF NOT EXISTS films (
     code char(5) CONSTRAINT firstkey PRIMARY KEY,
     title varchar(40) NOT NULL,
     did integer NOT NULL,
     date_prod date,
     kind varchar(10),
     len interval hour to minute
);

DROP TABLE IF EXISTS films;

SELECT * FROM films; 

CREATE TABLE IF NOT EXISTS films (
     code char(5) CONSTRAINT firstkey PRIMARY KEY,
     title varchar(40) NOT NULL,
     did integer NOT NULL,
     date_prod date,
     kind varchar(10),
     len interval hour to minute
);

ALTER TABLE IF EXISTS films
	ADD COLUMN IF NOT EXISTS score varchar (6); 

ALTER TABLE IF EXISTS films
	DROP COLUMN IF EXISTS score;

ALTER TABLE IF EXISTS films
	ALTER COLUMN score SET default 'NORM';
	
INSERT INTO films (code, title, did)
VALUES ('0001', 'Nevermore...', 7);

INSERT INTO films (code, title, did, score)
VALUES ('0002', 'My Fair Lady', 10, 'HIGH');


SELECT * FROM films; 

SELECT code, title, score 
FROM films

CREATE VIEW film_specs
AS
	SELECT code, title, score 
	FROM films;

SELECT * FROM film_specs;

DROP VIEW film_specs;