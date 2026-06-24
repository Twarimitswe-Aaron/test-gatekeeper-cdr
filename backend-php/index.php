<?php

require __DIR__ . '/vendor/autoload.php';

use Gatekeeper\GatekeeperCdr;

header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
    exit;
}

if ($_SERVER['REQUEST_URI'] === '/disarm') {
    if (!isset($_FILES['file'])) {
        http_response_code(400);
        echo json_encode(["error" => "No file uploaded"]);
        exit;
    }

    $rawBuffer = file_get_contents($_FILES['file']['tmp_name']);

    try {
        $result = GatekeeperCdr::disarm($rawBuffer);
        
        $cleanBuffer = $result['buffer'];
        $pngBuffer = $result['png_buffer'];
        $outputFormat = $result['output_format'];

        $formatDetected = GatekeeperCdr::sniffFormat($rawBuffer);
        
        $response = [
            "success" => true,
            "originalSize" => strlen($rawBuffer),
            "finalSize" => strlen($cleanBuffer),
            "format" => $formatDetected,
            "outputFormat" => $outputFormat,
            "disarmedFileBase64" => base64_encode($cleanBuffer)
        ];

        if ($pngBuffer !== null) {
            $response["pngFileBase64"] = base64_encode($pngBuffer);
        }

        header('Content-Type: application/json');
        echo json_encode($response);
    } catch (Throwable $e) {
        http_response_code(500);
        echo json_encode(["error" => "PHP Backend Error: " . $e->getMessage()]);
    }
}
