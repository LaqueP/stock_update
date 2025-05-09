<?php
// modules/stockupdate/stockupdate.php
if (!defined('_PS_VERSION_')) {
    exit;
}


class StockAvailable extends StockAvailableCore
{
    /** @var string */
    public $idconecta;
public static $definition = [
        'table' => 'stock_available',
        'primary' => 'id_stock_available',
        'fields' => [
            'id_product' => ['type' => self::TYPE_INT, 'validate' => 'isUnsignedId', 'required' => true],
            'id_product_attribute' => ['type' => self::TYPE_INT, 'validate' => 'isUnsignedId', 'required' => true],
            'id_shop' => ['type' => self::TYPE_INT, 'validate' => 'isUnsignedId'],
            'id_shop_group' => ['type' => self::TYPE_INT, 'validate' => 'isUnsignedId'],
            'quantity' => ['type' => self::TYPE_INT, 'validate' => 'isInt', 'required' => true, 'range' => ['min' => StockSettings::INT_32_MAX_NEGATIVE, 'max' => StockSettings::INT_32_MAX_POSITIVE]],
            'depends_on_stock' => ['type' => self::TYPE_BOOL, 'validate' => 'isBool', 'required' => true],
            'out_of_stock' => ['type' => self::TYPE_INT, 'validate' => 'isInt', 'required' => true],
            'location' => ['type' => self::TYPE_STRING, 'validate' => 'isString', 'size' => 255],
            'idconecta' => ['type' => self::TYPE_STRING, 'validate' => 'isGenericName'],
        ],
    ];
}