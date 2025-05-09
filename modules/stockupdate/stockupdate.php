<?php
// modules/stockupdate/stockupdate.php
if (!defined('_PS_VERSION_')) {
    exit;
}

class StockUpdate extends Module
{
    /**
     * Use bootstrap for back office forms
     * @var bool
     */
    public $bootstrap = true;

    /**
     * Compatible Prestashop versions
     * @var array
     */
    public $ps_versions_compliancy = [
        'min' => '8.0.0',
        'max' => _PS_VERSION_,
    ];

    public function __construct()
    {
        $this->name = 'stockupdate';
        $this->tab = 'administration';
        $this->version = '1.0.1';
        $this->author = 'LaqueP';
        $this->need_instance = 0;

        parent::__construct();

        $this->displayName = $this->l('Stock Update');
        $this->description = $this->l('Añade el campo idconecta a ps_product_attribute y ps_stock_available y lo expone en el webservice.');
    }

    public function install()
    {
        return parent::install()
            && $this->addCustomFields()
            && $this->installOverrides()
            && $this->clearCache();
    }

    public function uninstall()
    {
        return parent::uninstall()
            && $this->uninstallOverrides()
            && $this->removeCustomFields()
            && $this->clearCache();
    }

    /**
     * Añade columnas si no existen
     */
    protected function addCustomFields()
    {
        $db = Db::getInstance();
        $fields = [
            'product_attribute' => "ALTER TABLE `" . _DB_PREFIX_ . "product_attribute` ADD `idconecta` VARCHAR(255) NULL,
            'stock_available'   => "ALTER TABLE `" . _DB_PREFIX_ . "stock_available` ADD `idconecta` VARCHAR(255) NULL,
        ];
        foreach ($fields as $table => $sql) {
            $exists = $db->executeS("SHOW COLUMNS FROM `" . _DB_PREFIX_ . $table . "` LIKE 'idconecta'");
            if (!$exists) {
                if (!$db->execute($sql)) {
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * Elimina columnas si existen
     */
    protected function removeCustomFields()
    {
        $db = Db::getInstance();
        $fields = [
            'product_attribute' => "ALTER TABLE `" . _DB_PREFIX_ . "product_attribute` DROP COLUMN `idconecta`",
            'stock_available'   => "ALTER TABLE `" . _DB_PREFIX_ . "stock_available` DROP COLUMN `idconecta`",
        ];
        foreach ($fields as $table => $sql) {
            $exists = $db->executeS("SHOW COLUMNS FROM `" . _DB_PREFIX_ . $table . "` LIKE 'idconecta'");
            if ($exists) {
                $db->execute($sql);
            }
        }
        return true;
    }

    /**
     * Copia o fusiona archivos de override ubicados en override/
     */
    public function installOverrides()
    {
        $overrides = [
            ['src' => _PS_MODULE_DIR_ . $this->name . '/override/classes/Combination.php', 'dst' => _PS_OVERRIDE_DIR_ . 'classes/Combination.php'],
            ['src' => _PS_MODULE_DIR_ . $this->name . '/override/classes/stock/StockAvailable.php',   'dst' => _PS_OVERRIDE_DIR_ . 'classes/stock/StockAvailable.php'],
        ];
        foreach ($overrides as $ov) {
            $destDir = dirname($ov['dst']);
            if (!file_exists($destDir)) {
                mkdir($destDir, 0755, true);
            }
            if (!file_exists($ov['dst'])) {
                copy($ov['src'], $ov['dst']);
            } else {
                $this->mergeOverrideCode($ov['src'], $ov['dst']);
            }
        }
        return true;
    }

    /**
     * Elimina overrides al desinstalar
     */
    public function uninstallOverrides()
    {
        $overrides = [
            _PS_OVERRIDE_DIR_ . 'classes/Combination.php',
            _PS_OVERRIDE_DIR_ . 'classes/stock/StockAvailable.php',
        ];
        foreach ($overrides as $file) {
            if (!file_exists($file)) {
                continue;
            }
            $content = Tools::Tools::file_get_contents($file);
            $content = preg_replace("#/\* STOCKUPDATE START \*/.*?/\* STOCKUPDATE END \*/#s", '', $content);
            if (trim($content) === '' || strpos($content, 'extends') === false) {
                @unlink($file);
            } else {
                Tools::Tools::file_put_contents($file, $content);
            }
        }
        return true;
    }

    /**
     * Limpia caché de autoload y Smarty
     */
    protected function clearCache()
    {
        PrestaShopAutoload::getInstance()->generateIndex();
        Tools::clearCache();
        return true;
    }

    /**
     * Fusiona código marcado al override existente
     */
    protected function mergeOverrideCode($src, $dst)
    {
        $srcCode = Tools::file_get_contents($src);
        if (preg_match("#(/\* STOCKUPDATE START \*/.*?/\* STOCKUPDATE END \*/)#s", $srcCode, $m)) {
            $existing = Tools::file_get_contents($dst);
            $block = "\n" . $m[1] . "\n";
            $newContent = rtrim($existing, "\n") . $block;
            Tools::file_put_contents($dst, $newContent);
        }
    }
}

// NOTA: Los archivos de override deben situarse en:
// modules/stockupdate/override/classes/Combination.php
// modules/stockupdate/override/classes/stock/StockAvailable.php
// Y deben incluir su propio guardia de contexto (_PS_VERSION_) al inicio.
