#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace mle {

// Cryptographic signature support
class ModelSigner {
public:
    // Generate ED25519 key pair
    static void generate_keypair(
        uint8_t* public_key,   // 32 bytes
        uint8_t* private_key   // 64 bytes
    );
    
    // Sign model file
    static void sign_model(
        const std::string& model_path,
        const uint8_t* private_key
    );
    
    // Verify model signature
    static bool verify_model(
        const std::string& model_path,
        const uint8_t* public_key
    );
    
    // Compute model hash (SHA256)
    static std::string compute_hash(const std::string& model_path);
    
    // Verify integrity (checksum)
    static bool verify_integrity(const std::string& model_path);
};

// Model encryption (AES-256-GCM)
class ModelEncryptor {
public:
    // Encrypt model weights
    static void encrypt_model(
        const std::string& input_path,
        const std::string& output_path,
        const uint8_t* key,  // 32 bytes
        const uint8_t* iv    // 12 bytes
    );
    
    // Decrypt model weights
    static void decrypt_model(
        const std::string& input_path,
        const std::string& output_path,
        const uint8_t* key,
        const uint8_t* iv
    );
    
    // Generate random key
    static void generate_key(uint8_t* key, uint8_t* iv);
};

// Access control
struct AccessPolicy {
    std::vector<std::string> allowed_users;
    std::vector<std::string> allowed_hosts;
    uint64_t expiration_timestamp;
    bool require_signature;
    bool require_encryption;
};

class AccessController {
public:
    // Check if access is allowed
    static bool check_access(
        const std::string& model_path,
        const std::string& user,
        const std::string& host
    );
    
    // Set access policy
    static void set_policy(
        const std::string& model_path,
        const AccessPolicy& policy
    );
    
    // Get access policy
    static AccessPolicy get_policy(const std::string& model_path);
};

} // namespace mle
