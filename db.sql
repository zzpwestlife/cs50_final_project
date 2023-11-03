DROP TABLE IF EXISTS `user`;

CREATE TABLE `user`
(
    `id`            int           NOT NULL AUTO_INCREMENT,
    `username`      varchar(50)   NOT NULL NOT NULL DEFAULT '',
    `email`         varchar(120)  NOT NULL NOT NULL DEFAULT '',
    `password_hash` varchar(1000) NOT NULL          DEFAULT '',
    `created_at`    datetime                        DEFAULT NULL,
    `updated_at`    datetime                        DEFAULT NULL,
    `deleted_at`    datetime                        DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`),
    UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `todo`;

CREATE TABLE `todo`
(
    `id`           int          NOT NULL AUTO_INCREMENT,
    `user_id`      int          NOT NULL DEFAULT '0',
    `title`        varchar(100) NOT NULL DEFAULT '',
    `description`  varchar(500) NOT NULL DEFAULT '',
    `completed`    tinyint(1) NOT NULL DEFAULT '0',
    `notified`     tinyint(1) NOT NULL DEFAULT '0',
    `completed_at` datetime              DEFAULT NULL,
    `deadline`     datetime              DEFAULT NULL,
    `created_at`   datetime              DEFAULT NULL,
    `updated_at`   datetime              DEFAULT NULL,
    `deleted_at`   datetime              DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

