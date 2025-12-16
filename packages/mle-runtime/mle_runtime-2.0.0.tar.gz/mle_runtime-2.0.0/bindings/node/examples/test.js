const mle = require('../build/Release/mle_runtime');

async function main() {
    console.log('Creating MLE engine...');
    const engine = new mle.Engine('cpu');
    
    console.log('Loading model...');
    engine.loadModel('test_model.mle');
    
    // Create input buffer (128 floats)
    const inputSize = 128;
    const inputBuffer = Buffer.alloc(inputSize * 4); // 4 bytes per float
    
    // Fill with random data
    for (let i = 0; i < inputSize; ++i) {
        inputBuffer.writeFloatLE(Math.random(), i * 4);
    }
    
    console.log('Running inference...');
    const start = Date.now();
    const outputs = engine.run([inputBuffer]);
    const end = Date.now();
    
    console.log(`Inference time: ${end - start} ms`);
    console.log(`Output size: ${outputs[0].length} bytes`);
    console.log(`Peak memory: ${engine.peakMemory() / 1024 / 1024} MB`);
}

main().catch(console.error);
