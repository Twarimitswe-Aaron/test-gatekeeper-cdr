package main

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	gatekeeper "github.com/Twarimitswe-Aaron/gatekeeper-cdr/bindings/go"
)

func disarmHandler(w http.ResponseWriter, r *http.Request) {
	// Enable CORS
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	err := r.ParseMultipartForm(10 << 20) // 10 MB max
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Error retrieving file", http.StatusBadRequest)
		return
	}
	defer file.Close()

	rawBuffer, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Error reading file", http.StatusInternalServerError)
		return
	}

	// Gatekeeper CDR native binding
	formatDetected, err := gatekeeper.SniffFormat(rawBuffer)
	if err != nil {
		http.Error(w, fmt.Sprintf("Gatekeeper format error: %v", err), http.StatusInternalServerError)
		return
	}

	result, err := gatekeeper.Disarm(rawBuffer)
	if err != nil {
		http.Error(w, fmt.Sprintf("Gatekeeper disarm failed: %v", err), http.StatusInternalServerError)
		return
	}

	log.Printf("[Go] Disarmed file | Format: %s | Original: %d bytes | Native: %d bytes\n", formatDetected, len(rawBuffer), len(result.Buffer))

	response := map[string]interface{}{
		"success":            true,
		"originalSize":       len(rawBuffer),
		"finalSize":          len(result.Buffer),
		"format":             formatDetected,
		"outputFormat":       result.OutputFormat,
		"disarmedFileBase64": base64.StdEncoding.EncodeToString(result.Buffer),
	}

	if len(result.PngBuffer) > 0 {
		response["pngFileBase64"] = base64.StdEncoding.EncodeToString(result.PngBuffer)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func main() {
	http.HandleFunc("/disarm", disarmHandler)
	port := "3002"
	fmt.Printf("Go Backend listening on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
