package com.example.backendjava;

import io.github.gatekeeper.GatekeeperCdr;
import io.github.gatekeeper.FileFormat;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
@CrossOrigin(origins = "*") // Allow all origins for the testbed
public class BackendJavaApplication {

    public static void main(String[] args) {
        System.setProperty("server.port", "3003");
        SpringApplication.run(BackendJavaApplication.class, args);
        System.out.println("Java Backend listening on port 3003");
    }

    @PostMapping("/disarm")
    public ResponseEntity<Map<String, Object>> disarm(@RequestParam("file") MultipartFile file) {
        Map<String, Object> response = new HashMap<>();
        
        if (file.isEmpty()) {
            response.put("error", "No file uploaded");
            return ResponseEntity.badRequest().body(response);
        }

        try {
            byte[] rawBuffer = file.getBytes();
            
            // Sniff format
            FileFormat format = GatekeeperCdr.sniffFormat(rawBuffer);
            
            // Disarm file
            byte[] cleanBuffer = GatekeeperCdr.disarm(rawBuffer);
            
            response.put("success", true);
            response.put("originalSize", rawBuffer.length);
            response.put("finalSize", cleanBuffer.length);
            response.put("format", format.toString());
            response.put("disarmedFileBase64", Base64.getEncoder().encodeToString(cleanBuffer));
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            response.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
}
