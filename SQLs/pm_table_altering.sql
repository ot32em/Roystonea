ALTER TABLE `pm` MODIFY `parent_addr` char(21) DEFAULT '',
                 MODIFY `level` ENUM('Cloud', 'Cluster', 'Rack', 'Node', 'None' ),
                 ADD `lastmodify_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                    ON UPDATE CURRENT_TIMESTAMP
