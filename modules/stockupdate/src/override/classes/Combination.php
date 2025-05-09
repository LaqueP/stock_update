<?php
// modules/stockupdate/stockupdate.php
if (!defined('_PS_VERSION_')) {
    exit;
}

class Combination extends CombinationCore
{
    /** @var int */
    public $idconecta;
public static $definition = [
        'table' => 'product_attribute',
        'primary' => 'id_product_attribute',
        'multilang' => true,
        'fields' => [
            'id_product' => ['type' => self::TYPE_INT, 'shop' => 'both', 'validate' => 'isUnsignedId', 'required' => true],
            'ean13' => ['type' => self::TYPE_STRING, 'validate' => 'isEan13', 'size' => 13],
            'isbn' => ['type' => self::TYPE_STRING, 'validate' => 'isIsbn', 'size' => 32],
            'upc' => ['type' => self::TYPE_STRING, 'validate' => 'isUpc', 'size' => 12],
            'mpn' => ['type' => self::TYPE_STRING, 'validate' => 'isMpn', 'size' => 40],
            'reference' => ['type' => self::TYPE_STRING, 'size' => 64],
            'supplier_reference' => ['type' => self::TYPE_STRING, 'size' => 64],

            /* Shop fields */
            'wholesale_price' => ['type' => self::TYPE_FLOAT, 'shop' => true, 'validate' => 'isNegativePrice', 'size' => 27],
            'price' => ['type' => self::TYPE_FLOAT, 'shop' => true, 'validate' => 'isNegativePrice', 'size' => 20],
            'ecotax' => ['type' => self::TYPE_FLOAT, 'shop' => true, 'validate' => 'isPrice', 'size' => 20],
            'weight' => ['type' => self::TYPE_FLOAT, 'shop' => true, 'validate' => 'isFloat'],
            'unit_price_impact' => ['type' => self::TYPE_FLOAT, 'shop' => true, 'validate' => 'isNegativePrice', 'size' => 20],
            'minimal_quantity' => ['type' => self::TYPE_INT, 'shop' => true, 'validate' => 'isPositiveInt', 'required' => true],
            'low_stock_threshold' => ['type' => self::TYPE_INT, 'shop' => true, 'allow_null' => true, 'validate' => 'isInt'],
            'low_stock_alert' => ['type' => self::TYPE_BOOL, 'shop' => true, 'validate' => 'isBool'],
            'default_on' => ['type' => self::TYPE_BOOL, 'allow_null' => true, 'shop' => true, 'validate' => 'isBool'],
            'available_date' => ['type' => self::TYPE_DATE, 'shop' => true, 'validate' => 'isDateFormat'],

            /* Lang fields */
            'available_now' => ['type' => self::TYPE_STRING, 'lang' => true, 'validate' => 'isGenericName', 'size' => CombinationSettings::MAX_AVAILABLE_NOW_LABEL_LENGTH],
            'available_later' => ['type' => self::TYPE_STRING, 'lang' => true, 'validate' => 'IsGenericName', 'size' => CombinationSettings::MAX_AVAILABLE_LATER_LABEL_LENGTH],
            'idconecta' => ['type' => self::TYPE_STRING, 'validate' => 'isGenericName'],
        ],
    ];

}