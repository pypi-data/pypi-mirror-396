/**
 * MLE Runtime - Node.js Client Library
 * Fast ML inference runtime with memory-mapped loading
 */

export enum Device {
  CPU = 'cpu',
  CUDA = 'cuda'
}

export enum DType {
  FP32 = 0,
  FP16 = 1,
  INT8 = 2,
  INT32 = 3
}

export interface TensorShape {
  dimensions: number[];
  dtype: DType;
}

export interface ModelMetadata {
  modelName: string;
  framework: string;
  version: {
    major: number;
    minor: number;
    patch: number;
  };
  inputShapes: TensorShape[];
  outputShapes: TensorShape[];
  exportTimestamp?: number;
}

export interface InferenceOptions {
  device?: Device;
  batchSize?: number;
  timeout?: number;
}

export class MLEEngine {
  private nativeEngine: any;
  private modelPath: string | null = null;
  private metadata: ModelMetadata | null = null;

  constructor(device: Device = Device.CPU) {
    // Load native addon
    try {
      const addon = require('../build/Release/mle_node');
      this.nativeEngine = new addon.Engine(device);
    } catch (error) {
      throw new Error(`Failed to load MLE native addon: ${error}`);
    }
  }

  /**
   * Load a model from .mle file
   * @param path Path to .mle model file
   */
  async loadModel(path: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.nativeEngine.loadModel(path, (error: Error | null, metadata: any) => {
        if (error) {
          reject(new Error(`Failed to load model: ${error.message}`));
        } else {
          this.modelPath = path;
          this.metadata = metadata;
          resolve();
        }
      });
    });
  }

  /**
   * Run inference on input tensors
   * @param inputs Array of input tensors (Float32Array, Int32Array, etc.)
   * @param options Inference options
   * @returns Array of output tensors
   */
  async run(
    inputs: Float32Array[] | number[][],
    options?: InferenceOptions
  ): Promise<Float32Array[]> {
    if (!this.modelPath) {
      throw new Error('No model loaded. Call loadModel() first.');
    }

    return new Promise((resolve, reject) => {
      this.nativeEngine.run(inputs, options || {}, (error: Error | null, outputs: any) => {
        if (error) {
          reject(new Error(`Inference failed: ${error.message}`));
        } else {
          resolve(outputs);
        }
      });
    });
  }

  /**
   * Get model metadata
   */
  getMetadata(): ModelMetadata | null {
    return this.metadata;
  }

  /**
   * Get peak memory usage in bytes
   */
  getPeakMemoryUsage(): number {
    return this.nativeEngine.peakMemoryUsage();
  }

  /**
   * Unload model and free resources
   */
  dispose(): void {
    if (this.nativeEngine) {
      this.nativeEngine.dispose();
      this.modelPath = null;
      this.metadata = null;
    }
  }
}

/**
 * Utility functions
 */
export class MLEUtils {
  /**
   * Inspect .mle file and return metadata
   */
  static async inspectModel(path: string): Promise<ModelMetadata> {
    const addon = require('../build/Release/mle_node');
    return new Promise((resolve, reject) => {
      addon.inspectModel(path, (error: Error | null, metadata: any) => {
        if (error) {
          reject(error);
        } else {
          resolve(metadata);
        }
      });
    });
  }

  /**
   * Verify model signature
   */
  static async verifyModel(path: string, publicKey: string): Promise<boolean> {
    const addon = require('../build/Release/mle_node');
    return new Promise((resolve, reject) => {
      addon.verifyModel(path, publicKey, (error: Error | null, valid: boolean) => {
        if (error) {
          reject(error);
        } else {
          resolve(valid);
        }
      });
    });
  }
}

export default MLEEngine;
