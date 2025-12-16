package com.mle.runtime;

/**
 * Exception thrown by MLE runtime operations
 */
public class MLEException extends Exception {
    
    public MLEException(String message) {
        super(message);
    }
    
    public MLEException(String message, Throwable cause) {
        super(message, cause);
    }
}
