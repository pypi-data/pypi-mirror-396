import com.mle.runtime.*;
import java.util.List;
import java.util.Arrays;

/**
 * Simple inference example using MLE Java SDK
 */
public class SimpleInference {
    
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: java SimpleInference <model.mle>");
            System.exit(1);
        }
        
        String modelPath = args[0];
        
        try (MLEEngine engine = new MLEEngine(Device.CPU)) {
            // Load model
            System.out.println("Loading model: " + modelPath);
            engine.loadModel(modelPath);
            
            // Print metadata
            ModelMetadata metadata = engine.getMetadata();
            if (metadata != null) {
                System.out.println("Model: " + metadata.getModelName());
                System.out.println("Framework: " + metadata.getFramework());
            }
            
            // Create input tensor (example: 1x20 features)
            float[] input = new float[20];
            for (int i = 0; i < 20; i++) {
                input[i] = i * 0.1f;
            }
            
            // Run inference
            System.out.println("Running inference...");
            List<float[]> outputs = engine.run(List.of(input));
            
            // Print results
            System.out.println("Output length: " + outputs.get(0).length);
            System.out.println("First output value: " + outputs.get(0)[0]);
            System.out.println("Peak memory usage: " + 
                engine.getPeakMemoryUsage() / 1024 + " KB");
            
        } catch (MLEException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }
}
