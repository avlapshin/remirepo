<?php
/* Autoloader for solarium/solarium and its dependencies */

$vendorDir = '/usr/share/php';
// Use Symfony autoloader
if (!isset($fedoraClassLoader) || !($fedoraClassLoader instanceof \Symfony\Component\ClassLoader\ClassLoader)) {
    if (!class_exists('Symfony\\Component\\ClassLoader\\ClassLoader', false)) {
        require_once $vendorDir . '/Symfony/Component/ClassLoader/ClassLoader.php';
    }

    $fedoraClassLoader = new \Symfony\Component\ClassLoader\ClassLoader();
    $fedoraClassLoader->register();
}

$fedoraClassLoader->addPrefix('Solarium\\', dirname(__DIR__));

// dependencies
if (file_exists($vendorDir . '/Symfony/Component/autoload.php')) {
   require_once $vendorDir . '/Symfony/Component/autoload.php';
} else {
   $fedoraClassLoader->addPrefix('Symfony\\Component\\', $vendorDir);
}
