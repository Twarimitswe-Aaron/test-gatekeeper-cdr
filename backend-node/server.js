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
        
        const responsePayload = {
            success: true,
            originalSize: result.originalSizeBytes,
            finalSize: result.finalSizeBytes,
            format: result.detectedFormat,
            outputFormat: result.outputFormat,
            disarmedFileBase64: result.buffer.toString('base64')
        };

        if (result.pngBuffer) {
            responsePayload.pngFileBase64 = result.pngBuffer.toString('base64');
        }

        res.json(responsePayload);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

const PORT = 3001;
app.listen(PORT, () => {
    console.log(`Node.js Backend listening on port ${PORT}`);
});
