# MLE Runtime - Node.js Client Library

Fast ML inference runtime with memory-mapped loading. 10-100x faster than traditional serialization tools.

## Installation

```bash
npm install @mle/runtime
```

## Quick Start

```typescript
import { MLEEngine, Device } from '@mle/runtime';

// Create engine
const engine = new MLEEngine(Device.CPU);

// Load model (1-5ms vs 100-500ms for traditional tools)
await engine.loadModel('model.mle');

// Run inference
const inputs = [new Float32Array([1.0, 2.0, 3.0, 4.0])];
const outputs = await engine.run(inputs);

console.log('Predictions:', outputs[0]);
console.log('Peak memory:', engine.getPeakMemoryUsage(), 'bytes');

// Clean up
engine.dispose();
```

## Features

- ✅ **10-100x faster loading** - Memory-mapped binary format
- ✅ **50-90% smaller files** - Optimized weight storage
- ✅ **Zero Python overhead** - Native C++ execution
- ✅ **Cross-platform** - Works on Linux, macOS, Windows
- ✅ **TypeScript support** - Full type definitions
- ✅ **Async/await API** - Modern JavaScript patterns

## API Reference

### MLEEngine

#### Constructor
```typescript
new MLEEngine(device?: Device)
```

#### Methods

**loadModel(path: string): Promise<void>**
Load a model from .mle file.

**run(inputs: Float32Array[], options?: InferenceOptions): Promise<Float32Array[]>**
Run inference on input tensors.

**getMetadata(): ModelMetadata | null**
Get model metadata.

**getPeakMemoryUsage(): number**
Get peak memory usage in bytes.

**dispose(): void**
Unload model and free resources.

### MLEUtils

**inspectModel(path: string): Promise<ModelMetadata>**
Inspect .mle file and return metadata.

**verifyModel(path: string, publicKey: string): Promise<boolean>**
Verify model signature.

## Examples

### Express.js API Server

```typescript
import express from 'express';
import { MLEEngine, Device } from '@mle/runtime';

const app = express();
const engine = new MLEEngine(Device.CPU);

app.use(express.json());

// Load model on startup
engine.loadModel('classifier.mle').then(() => {
  console.log('Model loaded successfully');
});

app.post('/predict', async (req, res) => {
  try {
    const { features } = req.body;
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

app.listen(3000, () => {
  console.log('Inference server running on port 3000');
});
```

### Batch Processing

```typescript
import { MLEEngine, Device } from '@mle/runtime';
import fs from 'fs/promises';

async function processBatch(inputFile: string, outputFile: string) {
  const engine = new MLEEngine(Device.CPU);
  await engine.loadModel('model.mle');
  
  const data = JSON.parse(await fs.readFile(inputFile, 'utf-8'));
  const results = [];
  
  for (const item of data) {
    const input = new Float32Array(item.features);
    const output = await engine.run([input]);
    results.push({
      id: item.id,
      prediction: Array.from(output[0])
    });
  }
  
  await fs.writeFile(outputFile, JSON.stringify(results, null, 2));
  engine.dispose();
}

processBatch('input.json', 'output.json');
```

## Performance

Compared to traditional tools (joblib, pickle):

| Metric | Traditional | MLE | Improvement |
|--------|------------|-----|-------------|
| Load Time | 100-500ms | 1-5ms | **100x faster** |
| File Size | 100MB | 20MB | **80% smaller** |
| Inference | Python | Native C++ | **2-5x faster** |
| Memory | Full copy | Zero-copy | **50% less** |

## License

MIT
