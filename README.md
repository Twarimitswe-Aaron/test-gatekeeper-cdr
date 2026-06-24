# Gatekeeper CDR Multi-Language Testbed

This repository contains a SvelteKit frontend and five backend implementations (Node.js, Go, Java, PHP, and Python) demonstrating how to integrate the **published** `gatekeeper-cdr` packages natively without requiring a Rust compiler.

## 1. Frontend (SvelteKit)
The frontend provides a rich UI to upload suspicious files and send them to the selected backend.
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

---

## 2. Node.js Backend (Express) - Port 3001
Uses the native `@napi-rs` addon downloaded via NPM.
```bash
cd backend-node
npm install
node server.js
```

---

## 3. Go Backend - Port 3002
Uses CGo with the statically linked `.a` library bundled inside the Go module.
```bash
cd backend-go
go run main.go
```

---

## 4. Java Backend (Spring Boot) - Port 3003
Uses a JNI wrapper. The `.so` binary is bundled inside the `.jar` and dynamically extracted/loaded at runtime by `NativeUtils`, requiring zero local configuration.
```bash
cd backend-java
./mvnw spring-boot:run
# Or if you don't have the wrapper:
mvn spring-boot:run
```

---

## 5. PHP Backend (Minimal) - Port 3004
Uses PHP **FFI** to load the bundled `libgatekeeper.so` directly, avoiding the need to compile a PHP extension or modify `php.ini`.
```bash
cd backend-php
# Download dependencies
php composer.phar install
# Start the built-in server
php -S localhost:3004 index.php
```

---

## 6. Python Backend (FastAPI) - Port 3005
Uses the PyO3 native library provided via `maturin` wheels.
```bash
cd backend-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Verification
1. Start the **Frontend**.
2. Start one or more **Backends**.
3. Open `http://localhost:3000`.
4. Upload an image (e.g., JPEG, PNG, GIF) or document.
5. Watch it seamlessly sanitize the payload via the native CDR engine!
