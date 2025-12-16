/**
 * Express.js server with MLE inference
 */

const express = require('express');
const { MLEEngine, Device } = require('../dist/index');

const app = express();
app.use(express.json());

// Initialize engine
const engine = new MLEEngine(Device.CPU);
let modelLoaded = false;

// Load model on startup
async function initModel() {
    try {
        await engine.loadModel(process.env.MODEL_PATH || 'model.mle');
        modelLoaded = true;
        console.log('Model loaded successfully');
        
        const metadata = engine.getMetadata();
        console.log(`Model: ${metadata.modelName}`);
        console.log(`Framework: ${metadata.framework}`);
    } catch (error) {
        console.error('Failed to load model:', error.message);
        process.exit(1);
    }
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        modelLoaded: modelLoaded,
        memory: engine.getPeakMemoryUsage()
    });
});

// Prediction endpoint
app.post('/predict', async (req, res) => {
    if (!modelLoaded) {
        return res.status(503).json({ error: 'Model not loaded' });
    }
    
    try {
        const { features } = req.body;
        
        if (!Array.isArray(features)) {
            return res.status(400).json({ error: 'features must be an array' });
        }
        
        const input = new Float32Array(features);
        const outputs = await engine.run([input]);
        
        res.json({
            prediction: Array.from(outputs[0]),
            memory: engine.getPeakMemoryUsage()
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
const PORT = process.env.PORT || 3000;

initModel().then(() => {
    app.listen(PORT, () => {
        console.log(`Inference server running on port ${PORT}`);
        console.log(`Try: curl -X POST http://localhost:${PORT}/predict -H "Content-Type: application/json" -d '{"features":[1,2,3,4]}'`);
    });
});

// Cleanup on exit
process.on('SIGINT', () => {
    console.log('Shutting down...');
    engine.dispose();
    process.exit(0);
});
