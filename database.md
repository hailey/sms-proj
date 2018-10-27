# Database layout
Here is some code.

CREATE TABLE `messages` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`timestamp` INT(12) NOT NULL,
	`pid` VARCHAR(32) NULL DEFAULT NULL COMMENT 'Flowroute Msg Id' COLLATE 'utf8_bin',
	`provider_timestamp` VARCHAR(24) NOT NULL COMMENT 'Flowroute Provided Timestamp' COLLATE 'utf8_bin',
	`direction` ENUM('inbound','outbound') NULL DEFAULT 'inbound' COLLATE 'utf8_bin',
	`source_number` VARCHAR(11) NOT NULL COLLATE 'utf8_bin',
	`dest_number` VARCHAR(11) NOT NULL COLLATE 'utf8_bin',
	`cost` VARCHAR(10) NOT NULL DEFAULT '$0.00' COLLATE 'utf8_bin',
	`body` TEXT NOT NULL COLLATE 'utf8_bin',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
AUTO_INCREMENT=15
;



CREATE TABLE `dids` (
	`id` MEDIUMINT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
	`number` TINYTEXT NOT NULL COLLATE 'utf8_bin',
	`provider` VARCHAR(18) NULL DEFAULT '0' COLLATE 'utf8_bin',
	PRIMARY KEY (`id`)
)
COLLATE='utf8_bin'
ENGINE=InnoDB
AUTO_INCREMENT=4
;
