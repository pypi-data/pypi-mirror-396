package com.mle.runtime;

import java.nio.FloatBuffer;
import java.nio.file.Path;
import java.util.List;

/**
 * MLE Runtime Engine for Java
 * Fast ML inference with memory-mapped loading
 */
public class MLEEngine implements AutoCloseable {
    
    private long nativeHandle;
    private Device device;
    private ModelMetadata metadata;
    
    static {
        // Load native library
        System.loadLibrary("mle_jni");
    }
    
    /**
     * Create a new MLE engine
     * @param device Device to run inference on (CPU or CUDA)
     */
    public MLEEngine(Device device) {
        this.device = device;
        this.nativeHandle = nativeCreate(device.ordinal());
        if (this.nativeHandle == 0) {
            throw new RuntimeException("Failed to create MLE engine");
        }
    }
    
    /**
     * Load a model from .mle file
     * @param modelPath Path to .mle model file
     * @throws MLEException if loading fails
     */
    public void loadModel(String modelPath) throws MLEException {
        if (nativeHandle == 0) {
            throw new IllegalStateException("Engine has been closed");
        }
        
        String metadataJson = nativeLoadModel(nativeHandle, modelPath);
        if (metadataJson == null) {
            throw new MLEException("Failed to load model: " + modelPath);
        }
        
        this.metadata = ModelMetadata.fromJson(metadataJson);
    }
    
    /**
     * Run inference on input tensors
     * @param inputs List of input tensors as float arrays
     * @return List of output tensors as float arrays
     * @throws MLEException if inference fails
     */
    public List<float[]> run(List<float[]> inputs) throws MLEException {
        if (nativeHandle == 0) {
            throw new IllegalStateException("Engine has been closed");
        }
        if (metadata == null) {
            throw new IllegalStateException("No model loaded");
        }
        
        float[][] inputArrays = inputs.toArray(new float[0][]);
        float[][] outputs = nativeRun(nativeHandle, inputArrays);
        
        if (outputs == null) {
            throw new MLEException("Inference failed");
        }
        
        return List.of(outputs);
    }
    
    /**
     * Run inference with FloatBuffer inputs (zero-copy)
     * @param inputs List of input tensors as FloatBuffers
     * @return List of output tensors as FloatBuffers
     * @throws MLEException if inference fails
     */
    public List<FloatBuffer> runDirect(List<FloatBuffer> inputs) throws MLEException {
        if (nativeHandle == 0) {
            throw new IllegalStateException("Engine has been closed");
        }
        if (metadata == null) {
            throw new IllegalStateException("No model loaded");
        }
        
        FloatBuffer[] inputBuffers = inputs.toArray(new FloatBuffer[0]);
        FloatBuffer[] outputs = nativeRunDirect(nativeHandle, inputBuffers);
        
        if (outputs == null) {
            throw new MLEException("Inference failed");
        }
        
        return List.of(outputs);
    }
    
    /**
     * Get model metadata
     * @return Model metadata or null if no model loaded
     */
    public ModelMetadata getMetadata() {
        return metadata;
    }
    
    /**
     * Get peak memory usage in bytes
     * @return Peak memory usage
     */
    public long getPeakMemoryUsage() {
        if (nativeHandle == 0) {
            return 0;
        }
        return nativeGetPeakMemory(nativeHandle);
    }
    
    /**
     * Get current device
     * @return Device (CPU or CUDA)
     */
    public Device getDevice() {
        return device;
    }
    
    @Override
    public void close() {
        if (nativeHandle != 0) {
            nativeDestroy(nativeHandle);
            nativeHandle = 0;
        }
    }
    
    // Native methods
    private native long nativeCreate(int device);
    private native String nativeLoadModel(long handle, String path);
    private native float[][] nativeRun(long handle, float[][] inputs);
    private native FloatBuffer[] nativeRunDirect(long handle, FloatBuffer[] inputs);
    private native long nativeGetPeakMemory(long handle);
    private native void nativeDestroy(long handle);
}
