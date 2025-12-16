import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import com.mle.runtime.*;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Spring Boot server with MLE inference
 */
@SpringBootApplication
@RestController
public class SpringBootServer {
    
    private MLEEngine engine;
    private boolean modelLoaded = false;
    
    @PostConstruct
    public void init() {
        try {
            engine = new MLEEngine(Device.CPU);
            String modelPath = System.getenv().getOrDefault("MODEL_PATH", "model.mle");
            engine.loadModel(modelPath);
            modelLoaded = true;
            
            System.out.println("Model loaded successfully");
            ModelMetadata metadata = engine.getMetadata();
            if (metadata != null) {
                System.out.println("Model: " + metadata.getModelName());
                System.out.println("Framework: " + metadata.getFramework());
            }
        } catch (MLEException e) {
            System.err.println("Failed to load model: " + e.getMessage());
            System.exit(1);
        }
    }
    
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "healthy");
        response.put("modelLoaded", modelLoaded);
        response.put("memory", engine.getPeakMemoryUsage());
        return response;
    }
    
    @PostMapping("/predict")
    public ResponseEntity<?> predict(@RequestBody PredictionRequest request) {
        if (!modelLoaded) {
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)
                .body(Map.of("error", "Model not loaded"));
        }
        
        try {
            List<float[]> outputs = engine.run(List.of(request.getFeatures()));
            
            Map<String, Object> response = new HashMap<>();
            response.put("prediction", outputs.get(0));
            response.put("memory", engine.getPeakMemoryUsage());
            
            return ResponseEntity.ok(response);
        } catch (MLEException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }
    
    @PreDestroy
    public void cleanup() {
        if (engine != null) {
            engine.close();
        }
    }
    
    public static void main(String[] args) {
        SpringApplication.run(SpringBootServer.class, args);
    }
    
    static class PredictionRequest {
        private float[] features;
        
        public float[] getFeatures() { return features; }
        public void setFeatures(float[] features) { this.features = features; }
    }
}
