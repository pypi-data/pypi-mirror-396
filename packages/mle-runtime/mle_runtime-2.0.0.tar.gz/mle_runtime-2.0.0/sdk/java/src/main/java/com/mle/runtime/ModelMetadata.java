package com.mle.runtime;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * Model metadata from .mle file
 */
public class ModelMetadata {
    
    @SerializedName("model_name")
    private String modelName;
    
    private String framework;
    
    private Version version;
    
    @SerializedName("input_shapes")
    private List<TensorShape> inputShapes;
    
    @SerializedName("output_shapes")
    private List<TensorShape> outputShapes;
    
    @SerializedName("export_timestamp")
    private Long exportTimestamp;
    
    public static class Version {
        private int major;
        private int minor;
        private int patch;
        
        public int getMajor() { return major; }
        public int getMinor() { return minor; }
        public int getPatch() { return patch; }
        
        @Override
        public String toString() {
            return major + "." + minor + "." + patch;
        }
    }
    
    public static class TensorShape {
        private List<Integer> dimensions;
        private String dtype;
        
        public List<Integer> getDimensions() { return dimensions; }
        public String getDtype() { return dtype; }
    }
    
    public String getModelName() { return modelName; }
    public String getFramework() { return framework; }
    public Version getVersion() { return version; }
    public List<TensorShape> getInputShapes() { return inputShapes; }
    public List<TensorShape> getOutputShapes() { return outputShapes; }
    public Long getExportTimestamp() { return exportTimestamp; }
    
    /**
     * Parse metadata from JSON string
     */
    public static ModelMetadata fromJson(String json) {
        Gson gson = new Gson();
        return gson.fromJson(json, ModelMetadata.class);
    }
    
    @Override
    public String toString() {
        return String.format("ModelMetadata{name='%s', framework='%s', version=%s}",
            modelName, framework, version);
    }
}
