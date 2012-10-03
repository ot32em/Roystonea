CREATE TABLE `pm` 
    ( `id` INT(10) AUTO_INCREMENT PRIMARY KEY,
      `level` ENUM( 'Cloud', 'Cluster', 'Rack', 'Node', 'None' ),
      `label` VARCHAR(64) DEFAULT 'Unnamed',
      `host` CHAR(16) DEFAULT 'localhost' NOT NULL, INDEX USING BTREE(host),
      `port` SMALLINT(5) UNSIGNED NOT NULL,
      `parent_addr` VARCHAR (21) DEFAULT '',  
      `children_addrs` VARCHAR(1024),
      `create_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      `lastmodify_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP

    );
