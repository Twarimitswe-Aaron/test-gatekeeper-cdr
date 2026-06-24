const express = require('express');
const cors = require('cors');
const multer = require('multer');
const { disarm } = require('gatekeeper-cdr');

const app = express();
app.use(cors());

// Configure multer for file uploads (in-memory)
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

app.post('/disarm', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        const rawBuffer = req.file.buffer;
        // Call the gatekeeper native binding
        const result = disarm(rawBuffer);
        
        console.log(`[Node.js] Disarmed file | Format: ${result.detectedFormat} | Original: ${result.originalSizeBytes} bytes | Clean: ${result.finalSizeBytes} bytes`);
        
        // Return JSON with stats + base64 disarmed file (or send as binary)
        // For easiest frontend integration, let's send JSON with base64
        res.json({
            success: true,
            originalSize: result.originalSizeBytes,
            finalSize: result.finalSizeBytes,
            format: result.detectedFormat,
            disarmedFileBase64: result.buffer.toString('base64')
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Node.js Backend listening on port ${PORT}`);
});
