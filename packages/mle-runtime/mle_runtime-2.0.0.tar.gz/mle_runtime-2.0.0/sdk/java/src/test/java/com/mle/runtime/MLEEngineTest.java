package com.mle.runtime;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

/**
 * Unit tests for MLEEngine
 */
public class MLEEngineTest {
    
    private static final String TEST_MODEL = "test_model.mle";
    
    @Test
    public void testEngineCreation() {
        try (MLEEngine engine = new MLEEngine(Device.CPU)) {
            assertNotNull(engine);
            assertEquals(Device.CPU, engine.getDevice());
        }
    }
    
    @Test
    public void testLoadModel() throws MLEException {
        try (MLEEngine engine = new MLEEngine(Device.CPU)) {
            // This will fail if test model doesn't exist
            // In real tests, you'd have a fixture model
            assertThrows(MLEException.class, () -> {
                engine.loadModel("nonexistent.mle");
            });
        }
    }
    
    @Test
    public void testRunWithoutModel() {
        try (MLEEngine engine = new MLEEngine(Device.CPU)) {
            float[] input = {1.0f, 2.0f, 3.0f};
            
            assertThrows(IllegalStateException.class, () -> {
                engine.run(List.of(input));
            });
        }
    }
}
