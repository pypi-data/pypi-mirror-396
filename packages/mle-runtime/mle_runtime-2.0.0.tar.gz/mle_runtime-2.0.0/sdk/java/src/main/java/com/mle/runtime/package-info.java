/**
 * MLE Runtime - Java Client Library
 * 
 * Fast ML inference runtime with memory-mapped loading.
 * 10-100x faster than traditional serialization tools.
 * 
 * <h2>Quick Start</h2>
 * <pre>{@code
 * try (MLEEngine engine = new MLEEngine(Device.CPU)) {
 *     engine.loadModel("model.mle");
 *     List<float[]> outputs = engine.run(inputs);
 * }
 * }</pre>
 * 
 * <h2>Features</h2>
 * <ul>
 *   <li>10-100x faster loading - Memory-mapped binary format</li>
 *   <li>50-90% smaller files - Optimized weight storage</li>
 *   <li>Zero Python overhead - Native C++ execution via JNI</li>
 *   <li>Cross-platform - Works on Linux, macOS, Windows</li>
 *   <li>AutoCloseable - Automatic resource management</li>
 * </ul>
 * 
 * @since 1.0.0
 */
package com.mle.runtime;
