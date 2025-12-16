/**
 * Simple inference example using MLE Node.js SDK
 */

const { MLEEngine, Device } = require('../dist/index');

async function main() {
    if (process.argv.length < 3) {
        console.error('Usage: node simple_inference.js <model.mle>');
        process.exit(1);
    }
    
    const modelPath = process.argv[2];
    
    try {
        // Create engine
        const engine = new MLEEngine(Device.CPU);
        
        // Load model
        console.log(`Loading model: ${modelPath}`);
        await engine.loadModel(modelPath);
        
        // Print metadata
        const metadata = engine.getMetadata();
        if (metadata) {
            console.log(`Model: ${metadata.modelName}`);
            console.log(`Framework: ${metadata.framework}`);
        }
        
        // Create input tensor (example: 1x20 features)
        const input = new Float32Array(20);
        for (let i = 0; i < 20; i++) {
            input[i] = i * 0.1;
        }
        
        // Run inference
        console.log('Running inference...');
        const outputs = await engine.run([input]);
        
        // Print results
        console.log(`Output shape: [${outputs[0].length}]`);
        console.log(`First output value: ${outputs[0][0]}`);
        console.log(`Peak memory usage: ${engine.getPeakMemoryUsage() / 1024} KB`);
        
        // Clean up
        engine.dispose();
        
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

main();
