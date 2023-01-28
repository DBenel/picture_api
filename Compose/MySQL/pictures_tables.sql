USE `PICTURES`;

CREATE TABLE `pictures` (
	id int NOT NULL AUTO_INCREMENT,
	path varchar(150),
	date char(19),
	PRIMARY KEY (id)
);

CREATE TABLE `tags` (
	tag varchar(32),
	picture_id int,
	confidence float,
	date char(19),
	PRIMARY KEY (tag, picture_id),
	FOREIGN KEY (picture_id) REFERENCES pictures(id)
);
