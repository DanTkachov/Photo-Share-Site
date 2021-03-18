CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tag CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS AlbumContains CASCADE;
DROP TABLE IF EXISTS OwnsComment CASCADE;
DROP TABLE IF EXISTS HasComment CASCADE;
DROP TABLE IF EXISTS Tagged CASCADE;

CREATE TABLE Users (
    user_id INT4 AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    dob DATE,
    numberOfFriends INT4,
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


CREATE TABLE IF NOT EXISTS Album (
    album_id INT4 AUTO_INCREMENT,
    album_name VARCHAR(255),
    user_id INT4,
    creation_date DATE,
    INDEX uaid_idx (user_id),
    CONSTRAINT album_pk_a PRIMARY KEY (album_id),
        CONSTRAINT user_fk_a FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
);

CREATE TABLE IF NOT EXISTS Pictures (
    picture_id INT4 AUTO_INCREMENT,
    album_id INT4 NOT NULL,
    user_id INT4 NOT NULL,
    likes INT4,
    imgdata LONGBLOB,
    caption VARCHAR(255),
    INDEX upid_idx (user_id),
    CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
    CONSTRAINT albums_pk FOREIGN KEY (album_id)
        REFERENCES Album (album_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Comments (
    comment_id INT4 AUTO_INCREMENT,
    user_id INT4,
    comment_text VARCHAR(255),
    created_date DATE NOT NULL,
    CONSTRAINT comments_pk PRIMARY KEY (comment_id),
    CONSTRAINT user_fk_c FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
);

CREATE TABLE IF NOT EXISTS Tag (
    tag VARCHAR(255),
    CONSTRAINT tag_pk PRIMARY KEY (tag)
);
CREATE TABLE BelongsTo (
    user_id INT4,
    album_id INT4,
    CONSTRAINT album_fk FOREIGN KEY (album_id)
        REFERENCES Album (album_id)
        ON DELETE CASCADE,
    CONSTRAINT user_fk FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
);
CREATE TABLE AlbumContains (
    album_id INT4,
    picture_id INT4,
    CONSTRAINT album_fk_ac FOREIGN KEY (album_id)
        REFERENCES Album (album_id)
        ON DELETE CASCADE,
    CONSTRAINT picture_fk_ac FOREIGN KEY (picture_id)
        REFERENCES Pictures (picture_id)
);

CREATE TABLE Friends (
    user_id1 INT4,
    user_id2 INT4,
    CONSTRAINT friend1_fk FOREIGN KEY (user_id1)
        REFERENCES Users (user_id),
    CONSTRAINT friend2_fk FOREIGN KEY (user_id2)
        REFERENCES Users (user_id),
    CONSTRAINT NoSelfFriends CHECK (user_id1 <> user_id2)
);

CREATE TABLE OwnsComment (
    comment_id INT4,
    user_id INT4,
    CONSTRAINT comment_fk_oc FOREIGN KEY (comment_id)
        REFERENCES Comments (comment_id),
    CONSTRAINT user_fk_oc FOREIGN KEY (user_id)
        REFERENCES Users (user_id)
);

CREATE TABLE HasComment (
    picture_id INT4,
    comment_id INT4,
    CONSTRAINT comment_fk_hc FOREIGN KEY (comment_id)
        REFERENCES Comments (comment_id),
    CONSTRAINT picture_fk_hc FOREIGN KEY (picture_id)
        REFERENCES Pictures (picture_id)
);
CREATE TABLE Tagged (
    picture_id INT4 NOT NULL,
    tag VARCHAR(255),
    CONSTRAINT tag_fk_t FOREIGN KEY (tag)
        REFERENCES Tag (tag),
    CONSTRAINT picture_fk_t FOREIGN KEY (picture_id)
        REFERENCES Pictures (picture_id)
);
