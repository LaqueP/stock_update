# StockUpdate Module for PrestaShop 8

**Version:** 1.0.0
**Author:** LaqueP

## Descripción

Este módulo añade el campo `idconecta` a las tablas:

* `ps_product_attribute`
* `ps_stock_available`

y lo expone en el Webservice de PrestaShop, permitiendo sincronizar un identificador personalizado basado en la concatenación:

```
<reference_del_producto>-<id_attribute>
```

El módulo crea automáticamente las columnas si no existen al instalarse, y las elimina al desinstalarse.

## Características principales

* **Instalación automática** de la columna `idconecta` (VARCHAR(255)).
* **Override** de las clases `Combination` y `StockAvailable` para exponer `idconecta` en el Webservice.
* **Merge inteligente**: si ya existe un override, inyecta sólo el bloque marcado, sin sobrescribir el core.
* **Desinstalación limpia**: elimina columnas y overrides.
* **Compatibilidad** con PrestaShop 8.x.
* Uso de **Bootstrap** en formularios del back office.

## Estructura del módulo

```
modules/stockupdate/
├── override/
│   ├── classes/
│   │   ├── Combination.php
│   │   └── stock/
│   │       └── StockAvailable.php
├── stockupdate.php       ← Archivo principal del módulo
├── logo.png
└── README.md             ← Este archivo
```

* **override/classes/Combination.php**
  Override completo de `CombinationCore`, añadiendo al final de `fields` la definición de `idconecta`.

* **override/classes/stock/StockAvailable.php**
  Override completo de `StockAvailableCore`, añadiendo al final de `fields` la definición de `idconecta`.

## Instalación

1. Copiar la carpeta `stockupdate` a tu directorio `/modules/`.
2. Asegurarse de que los archivos de override están en `modules/stockupdate/override/...`.
3. En el Back Office, **Módulos > Gestor de módulos**, buscar "Stock Update" e instalar.
4. Vaciar caché (BO > Parámetros avanzados > Rendimiento > **Vaciar caché**).
5. Regenerar el índice de clases:

   ```php
   PrestaShopAutoload::getInstance()->generateIndex();
   Tools::clearCache();
   ```

## Configuración

No requiere configuración adicional en el Back Office. Tras la instalación, las columnas `idconecta` estarán disponibles en la API Webservice (GET/PUT/POST) bajo los recursos:

* `/api/combinations`
* `/api/stock_availables`

Asegúrate de que tu clave Webservice tiene permisos sobre estos recursos.

## Creación de Evento MySQL (recomendado)

Para sincronizar periódicamente el valor de `idconecta` con la concatenación de `reference` e `id_attribute`, crea un **EVENT** en tu servidor MySQL:

```sql
-- 1) Activar Event Scheduler
SHOW VARIABLES LIKE 'event_scheduler';
SET GLOBAL event_scheduler = ON;

-- 2) Crear el EVENT
DELIMITER $$
CREATE EVENT IF NOT EXISTS `stockupdate_idconecta_sync`
ON SCHEDULE EVERY 1 HOUR
COMMENT 'Sincroniza idconecta con reference-id_attribute'
DO
BEGIN
  -- Actualizar ps_product_attribute
  UPDATE `ps_product_attribute` pa
  JOIN `ps_product` p
    ON p.`id_product` = pa.`id_product`
  JOIN `ps_product_attribute_combination` pac
    ON pac.`id_product_attribute` = pa.`id_product_attribute`
  SET pa.`idconecta` = CONCAT(p.`reference`, '-', pac.`id_attribute`)
  WHERE pa.`idconecta` IS NULL
     OR pa.`idconecta` <> CONCAT(p.`reference`, '-', pac.`id_attribute`);

  -- Actualizar ps_stock_available
  UPDATE `ps_stock_available` sa
  JOIN `ps_product` p
    ON p.`id_product` = sa.`id_product`
  JOIN `ps_product_attribute_combination` pac
    ON pac.`id_product_attribute` = sa.`id_product_attribute`
  SET sa.`idconecta` = CONCAT(p.`reference`, '-', pac.`id_attribute`)
  WHERE sa.`idconecta` IS NULL
     OR sa.`idconecta` <> CONCAT(p.`reference`, '-', pac.`id_attribute`);
END$$
DELIMITER ;
```

* **Frecuencia:** cada hora (`EVERY 1 HOUR`). Ajusta según tus necesidades.
* **Requerimientos:** el parámetro `event_scheduler` de MySQL debe estar `ON`.

## Desinstalación

1. En el Back Office, desinstalar el módulo "Stock Update".
2. El módulo eliminará las columnas `idconecta` y los overrides.
3. Verificar en base de datos:

   ```sql
   ALTER TABLE ps_product_attribute DROP COLUMN IF EXISTS idconecta;
   ALTER TABLE ps_stock_available   DROP COLUMN IF EXISTS idconecta;
   ```
4. Eliminar registros residuales:

   ```sql
   DELETE FROM ps_module WHERE name = 'stockupdate';
   DELETE FROM ps_configuration WHERE name LIKE 'STOCKUPDATE_%';
   ```

## Observaciones

* Este módulo **no** gestiona la lógica de sincronización en tiempo real; es necesario crear el evento MySQL o actualizar manualmente los registros.
* Asegúrate de tener activado el **Event Scheduler** en tu servidor MySQL.

---

¡Listo! Ahora tienes un módulo que expone `idconecta` y un evento para mantenerlo sincronizado. ¡Disfruta!
