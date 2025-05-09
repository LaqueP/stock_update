DELIMITER $$
CREATE EVENT IF NOT EXISTS `stockupdate_idconecta_sync`
ON SCHEDULE EVERY 1 HOUR
COMMENT 'Sincroniza idconecta con reference-id_attribute usando ps_product_attribute_combination'
DO
BEGIN
  -- Para ps_product_attribute
  UPDATE `ps_product_attribute` AS pa
  INNER JOIN `ps_product` AS p
    ON p.`id_product` = pa.`id_product`
  INNER JOIN `ps_product_attribute_combination` AS pac
    ON pac.`id_product_attribute` = pa.`id_product_attribute`
  SET pa.`idconecta` = CONCAT(p.`reference`, '-', pac.`id_attribute`)
  WHERE pa.`idconecta` IS NULL
     OR pa.`idconecta` <> CONCAT(p.`reference`, '-', pac.`id_attribute`);

  -- Para ps_stock_available
  UPDATE `ps_stock_available` AS sa
  INNER JOIN `ps_product` AS p
    ON p.`id_product` = sa.`id_product`
  INNER JOIN `ps_product_attribute_combination` AS pac
    ON pac.`id_product_attribute` = sa.`id_product_attribute`
  SET sa.`idconecta` = CONCAT(p.`reference`, '-', pac.`id_attribute`)
  WHERE sa.`idconecta` IS NULL
     OR sa.`idconecta` <> CONCAT(p.`reference`, '-', pac.`id_attribute`);
END$$
DELIMITER ;