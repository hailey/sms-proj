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