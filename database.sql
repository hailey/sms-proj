# Database layout
Here is some code.

CREATE TABLE `account` (
	`id` SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT,
	`name` VARCHAR(50) NOT NULL DEFAULT '0' COLLATE 'utf8_bin',
	`email` VARCHAR(75) NOT NULL DEFAULT '0' COLLATE 'utf8_bin',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;


CREATE TABLE `destination` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`dest_did` VARCHAR(11) NOT NULL DEFAULT '0' COLLATE 'utf8_bin',
	`verify_status` ENUM('Y','N','P') NOT NULL DEFAULT 'N' COMMENT 'Y, N, for yes or No. P for Pending' COLLATE 'utf8_bin',
	`idpin` MEDIUMINT(8) UNSIGNED NULL DEFAULT '0',
	`account_id` SMALLINT(5) UNSIGNED NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	INDEX `FK_destination_account` (`account_id`),
	CONSTRAINT `FK_destination_account` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;

CREATE TABLE `dids` (
	`id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
	`number` TINYTEXT NOT NULL COLLATE 'utf8_bin',
	`provider` VARCHAR(18) NULL DEFAULT '0' COLLATE 'utf8_bin',
	`account_id` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,
	PRIMARY KEY (`id`),
	INDEX `FK_dids_account` (`account_id`),
	CONSTRAINT `FK_dids_account` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;
INSERT INTO dids (number,provider,account_id) VALUES ('17605551212','Flowroute',1)


CREATE TABLE `messages` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`account_id` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,
	`timestamp` INT(12) NOT NULL,
	`pid` VARCHAR(64) NULL DEFAULT NULL COMMENT 'Flowroute Msg Id' COLLATE 'utf8_bin',
	`provider_timestamp` VARCHAR(24) NULL DEFAULT NULL COMMENT 'Flowroute Provided Timestamp' COLLATE 'utf8_bin',
	`direction` ENUM('inbound','outbound') NULL DEFAULT 'inbound' COLLATE 'utf8_bin',
	`source_number` VARCHAR(11) NOT NULL COLLATE 'utf8_bin',
	`dest_number` VARCHAR(11) NOT NULL COLLATE 'utf8_bin',
	`cost` VARCHAR(10) NOT NULL DEFAULT '0.00' COLLATE 'utf8_bin',
	`body` TEXT NOT NULL COLLATE 'utf8_bin',
	PRIMARY KEY (`id`),
	INDEX `FK_messages_account` (`account_id`),
	CONSTRAINT `FK_messages_account` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
;
########## Update V1, add delivered status to messages table.
ALTER TABLE messages ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'pending';
ALTER TABLE `messages` MODIFY `provider_timestamp` VARCHAR(36);

##########Update V2
# Adding token and other infos.
ALTER TABLE account ADD COLUMN `refresh_token` BLOB NULL;
ALTER TABLE account ADD COLUMN `google_id` VARCHAR(255) NULL UNIQUE;
ALTER TABLE account ADD COLUMN `verified_email` BOOL NOT NULL DEFAULT False;

##########Update V3
# Adding last modified and created, as well as changing the timestamp
# This requires loss of all logs. Oops.
ALTER TABLE account ADD COLUMN `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE account ADD COLUMN `last_modified` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE messages MODIFY `timestamp` TIMESTAMP NOT NULL;

##########Update V4
# Add an entirely new table contactlist
CREATE TABLE `contacts` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`account_id` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,
	`last_modified` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`archived` BOOL NOT NULL DEFAULT '0',
	`fullname` VARCHAR(122) NOT NULL,
	`email` VARCHAR(200) NULL,
	PRIMARY KEY (`id`),
	INDEX `FK_contacts_account` (`account_id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB;

CREATE TABLE `phonebase` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`contact_id` SMALLINT(5) UNSIGNED NULL DEFAULT NULL,
	`phone_number` VARCHAR(15) NOT NULL,
	`number_type` ENUM('mobile','home', 'office', 'other') NULL DEFAULT 'mobile',
	`archived` BOOL NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	INDEX `pb_phonebaseID` (`contact_id`),
	INDEX `index_archivedNumbers` (`archived`),
	CONSTRAINT `pb_accountassoc`
		FOREIGN KEY (`contact_id`) REFERENCES account (id)
)
COLLATE='utf8_bin'
ENGINE=InnoDB;

########### Update V5
# Adding password and username support.
ALTER TABLE account ADD COLUMN `username` VARCHAR(255) NULL UNIQUE;
ALTER TABLE account ADD COLUMN `passwd` VARCHAR(255) NULL;

########## UPDATE V6
ALTER TABLE account DROP COLUMN `google_id`;
ALTER TABLE account DROP COLUMN `username`;
ALTER TABLE account DROP COLUMN `refresh_token`;
ALTER TABLE account ADD COLUMN `loginid` VARCHAR(255) NULL UNIQUE;
ALTER TABLE account ADD COLUMN `picture_url` VARCHAR(255) NULL;
ALTER TABLE messages ADD COLUMN `is_read` BOOL NOT NULL DEFAULT '0';
