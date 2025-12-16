#include "security.h"
#include "mle_format.h"
#include "compression.h"
#include <fstream>
#include <stdexcept>
#include <cstring>
#include <chrono>
#include <iostream>

// Cryptographic libraries
#ifdef ENABLE_CRYPTO
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/aes.h>
#include <openssl/gcm.h>
#include <ed25519.h>
#endif

namespace mle {

void ModelSigner::generate_keypair(uint8_t* public_key, uint8_t* private_key) {
#ifdef ENABLE_CRYPTO
    // Generate ED25519 key pair
    ed25519_create_keypair(public_key, private_key, nullptr);
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

void ModelSigner::sign_model(const std::string& model_path, const uint8_t* private_key) {
#ifdef ENABLE_CRYPTO
    // Read the model file
    std::ifstream file(model_path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open model file for signing");
    }
    
    // Read header to get structure
    MLEHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(header));
    if (header.magic != MLE_MAGIC) {
        throw std::runtime_error("Invalid MLE file format");
    }
    
    // Compute hash of model content (excluding signature section)
    std::string model_hash = compute_hash_excluding_signature(model_path);
    
    // Create signature
    SignatureHeader sig_header = {};
    sig_header.algorithm = 1;  // ED25519
    sig_header.hash_algorithm = 1;  // SHA256
    sig_header.timestamp = std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    
    // Extract public key from private key
    uint8_t public_key[32];
    ed25519_get_public_key(public_key, private_key);
    memcpy(sig_header.public_key, public_key, 32);
    
    // Convert hash string to bytes
    ModelSigner::hex_to_bytes(model_hash, sig_header.model_hash, 32);
    
    // Sign the model hash
    ed25519_sign(sig_header.signature, sig_header.model_hash, 32, public_key, private_key);
    
    // Update header with signature information
    header.feature_flags |= static_cast<uint32_t>(FeatureFlags::SIGNING);
    header.signature_offset = file.tellg();
    header.signature_size = sizeof(SignatureHeader);
    
    // Write signature to file
    file.seekp(0, std::ios::end);
    file.write(reinterpret_cast<const char*>(&sig_header), sizeof(sig_header));
    
    // Update header
    file.seekp(0);
    file.write(reinterpret_cast<const char*>(&header), sizeof(header));
    
    file.close();
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

bool ModelSigner::verify_model(const std::string& model_path, const uint8_t* public_key) {
#ifdef ENABLE_CRYPTO
    std::ifstream file(model_path, std::ios::binary);
    if (!file) {
        return false;
    }
    
    // Read header
    MLEHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(header));
    if (header.magic != MLE_MAGIC) {
        return false;
    }
    
    // Check if model is signed
    if (!(header.feature_flags & static_cast<uint32_t>(FeatureFlags::SIGNING))) {
        return false;  // Model is not signed
    }
    
    // Read signature
    file.seekg(header.signature_offset);
    SignatureHeader sig_header;
    file.read(reinterpret_cast<char*>(&sig_header), sizeof(sig_header));
    
    // Verify public key matches
    if (memcmp(sig_header.public_key, public_key, 32) != 0) {
        return false;
    }
    
    // Compute current model hash
    std::string current_hash = ModelSigner::compute_hash_excluding_signature(model_path);
    uint8_t current_hash_bytes[32];
    ModelSigner::hex_to_bytes(current_hash, current_hash_bytes, 32);
    
    // Verify signature
    return ed25519_verify(sig_header.signature, current_hash_bytes, 32, public_key) == 1;
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

std::string ModelSigner::compute_hash(const std::string& model_path) {
#ifdef ENABLE_CRYPTO
    std::ifstream file(model_path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open file for hashing");
    }
    
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    
    char buffer[8192];
    while (file.read(buffer, sizeof(buffer)) || file.gcount() > 0) {
        SHA256_Update(&ctx, buffer, file.gcount());
    }
    
    uint8_t hash[SHA256_DIGEST_LENGTH];
    SHA256_Final(hash, &ctx);
    
    return bytes_to_hex(hash, SHA256_DIGEST_LENGTH);
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

std::string ModelSigner::compute_hash_excluding_signature(const std::string& model_path) {
#ifdef ENABLE_CRYPTO
    std::ifstream file(model_path, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Cannot open file for hashing");
    }
    
    // Read header to get signature location
    MLEHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(header));
    
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    
    // Hash everything except the signature section
    file.seekg(0);
    char buffer[8192];
    size_t total_read = 0;
    size_t signature_start = header.signature_offset;
    size_t signature_end = header.signature_offset + header.signature_size;
    
    while (file.read(buffer, sizeof(buffer)) || file.gcount() > 0) {
        size_t bytes_read = file.gcount();
        size_t chunk_start = total_read;
        size_t chunk_end = total_read + bytes_read;
        
        // Skip signature section
        if (chunk_end <= signature_start || chunk_start >= signature_end) {
            // Chunk is completely outside signature section
            SHA256_Update(&ctx, buffer, bytes_read);
        } else if (chunk_start < signature_start && chunk_end > signature_start) {
            // Chunk starts before signature section
            size_t before_sig = signature_start - chunk_start;
            SHA256_Update(&ctx, buffer, before_sig);
            
            if (chunk_end > signature_end) {
                // Chunk also extends past signature section
                size_t after_sig_offset = signature_end - chunk_start;
                size_t after_sig_size = chunk_end - signature_end;
                SHA256_Update(&ctx, buffer + after_sig_offset, after_sig_size);
            }
        } else if (chunk_start < signature_end && chunk_end > signature_end) {
            // Chunk starts in signature section but extends past it
            size_t after_sig_offset = signature_end - chunk_start;
            size_t after_sig_size = chunk_end - signature_end;
            SHA256_Update(&ctx, buffer + after_sig_offset, after_sig_size);
        }
        // If chunk is completely within signature section, skip it
        
        total_read += bytes_read;
    }
    
    uint8_t hash[SHA256_DIGEST_LENGTH];
    SHA256_Final(hash, &ctx);
    
    return bytes_to_hex(hash, SHA256_DIGEST_LENGTH);
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

bool ModelSigner::verify_integrity(const std::string& model_path) {
    std::ifstream file(model_path, std::ios::binary);
    if (!file) {
        return false;
    }
    
    // Read header
    MLEHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(header));
    if (header.magic != MLE_MAGIC) {
        return false;
    }
    
    // Verify header checksum
    uint32_t stored_checksum = header.header_checksum;
    MLEHeader temp_header = header;
    temp_header.header_checksum = 0;  // Exclude checksum field itself
    
    uint32_t computed_checksum = Compressor::checksum(&temp_header, sizeof(temp_header));
    if (stored_checksum != computed_checksum) {
        return false;
    }
    
    // Verify section checksums
    if (!ModelSigner::verify_section_checksum(file, header.metadata_offset, header.metadata_size, header.metadata_checksum) ||
        !ModelSigner::verify_section_checksum(file, header.graph_offset, header.graph_size, header.graph_checksum) ||
        !ModelSigner::verify_section_checksum(file, header.weights_offset, header.weights_size, header.weights_checksum)) {
        return false;
    }
    
    return true;
}

bool ModelSigner::verify_section_checksum(std::ifstream& file, uint64_t offset, uint64_t size, uint32_t expected_checksum) {
    if (size == 0) return true;
    
    file.seekg(offset);
    std::vector<uint8_t> data(size);
    file.read(reinterpret_cast<char*>(data.data()), size);
    
    uint32_t computed_checksum = Compressor::checksum(data.data(), size);
    return computed_checksum == expected_checksum;
}

std::string ModelSigner::bytes_to_hex(const uint8_t* bytes, size_t length) {
    std::string hex;
    hex.reserve(length * 2);
    
    const char* hex_chars = "0123456789abcdef";
    for (size_t i = 0; i < length; ++i) {
        hex += hex_chars[bytes[i] >> 4];
        hex += hex_chars[bytes[i] & 0x0f];
    }
    
    return hex;
}

void ModelSigner::hex_to_bytes(const std::string& hex, uint8_t* bytes, size_t length) {
    if (hex.length() != length * 2) {
        throw std::runtime_error("Invalid hex string length");
    }
    
    for (size_t i = 0; i < length; ++i) {
        char high = hex[i * 2];
        char low = hex[i * 2 + 1];
        
        uint8_t high_val = (high >= '0' && high <= '9') ? (high - '0') :
                          (high >= 'a' && high <= 'f') ? (high - 'a' + 10) :
                          (high >= 'A' && high <= 'F') ? (high - 'A' + 10) : 0;
        
        uint8_t low_val = (low >= '0' && low <= '9') ? (low - '0') :
                         (low >= 'a' && low <= 'f') ? (low - 'a' + 10) :
                         (low >= 'A' && low <= 'F') ? (low - 'A' + 10) : 0;
        
        bytes[i] = (high_val << 4) | low_val;
    }
}

// Model encryption implementation
void ModelEncryptor::encrypt_model(
    const std::string& input_path,
    const std::string& output_path,
    const uint8_t* key,
    const uint8_t* iv) {
#ifdef ENABLE_CRYPTO
    std::ifstream input(input_path, std::ios::binary);
    std::ofstream output(output_path, std::ios::binary);
    
    if (!input || !output) {
        throw std::runtime_error("Cannot open files for encryption");
    }
    
    // Read and encrypt in chunks
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create encryption context");
    }
    
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), nullptr, key, iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize encryption");
    }
    
    char buffer[8192];
    uint8_t encrypted[8192 + 16];  // Extra space for GCM tag
    int encrypted_len;
    
    while (input.read(buffer, sizeof(buffer)) || input.gcount() > 0) {
        if (EVP_EncryptUpdate(ctx, encrypted, &encrypted_len, 
                             reinterpret_cast<uint8_t*>(buffer), input.gcount()) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            throw std::runtime_error("Encryption failed");
        }
        output.write(reinterpret_cast<char*>(encrypted), encrypted_len);
    }
    
    // Finalize encryption
    if (EVP_EncryptFinal_ex(ctx, encrypted, &encrypted_len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Encryption finalization failed");
    }
    output.write(reinterpret_cast<char*>(encrypted), encrypted_len);
    
    // Get authentication tag
    uint8_t tag[16];
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to get authentication tag");
    }
    output.write(reinterpret_cast<char*>(tag), 16);
    
    EVP_CIPHER_CTX_free(ctx);
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

void ModelEncryptor::decrypt_model(
    const std::string& input_path,
    const std::string& output_path,
    const uint8_t* key,
    const uint8_t* iv) {
#ifdef ENABLE_CRYPTO
    std::ifstream input(input_path, std::ios::binary);
    std::ofstream output(output_path, std::ios::binary);
    
    if (!input || !output) {
        throw std::runtime_error("Cannot open files for decryption");
    }
    
    // Get file size to extract tag
    input.seekg(0, std::ios::end);
    size_t file_size = input.tellg();
    input.seekg(0);
    
    if (file_size < 16) {
        throw std::runtime_error("File too small to contain authentication tag");
    }
    
    // Read authentication tag from end of file
    uint8_t tag[16];
    input.seekg(file_size - 16);
    input.read(reinterpret_cast<char*>(tag), 16);
    input.seekg(0);
    
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        throw std::runtime_error("Failed to create decryption context");
    }
    
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), nullptr, key, iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to initialize decryption");
    }
    
    char buffer[8192];
    uint8_t decrypted[8192];
    int decrypted_len;
    size_t total_read = 0;
    
    while (total_read < file_size - 16 && 
           (input.read(buffer, std::min(sizeof(buffer), file_size - 16 - total_read)) || input.gcount() > 0)) {
        if (EVP_DecryptUpdate(ctx, decrypted, &decrypted_len,
                             reinterpret_cast<uint8_t*>(buffer), input.gcount()) != 1) {
            EVP_CIPHER_CTX_free(ctx);
            throw std::runtime_error("Decryption failed");
        }
        output.write(reinterpret_cast<char*>(decrypted), decrypted_len);
        total_read += input.gcount();
    }
    
    // Set authentication tag
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, 16, tag) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Failed to set authentication tag");
    }
    
    // Finalize decryption
    if (EVP_DecryptFinal_ex(ctx, decrypted, &decrypted_len) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        throw std::runtime_error("Decryption failed - authentication tag mismatch");
    }
    output.write(reinterpret_cast<char*>(decrypted), decrypted_len);
    
    EVP_CIPHER_CTX_free(ctx);
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

void ModelEncryptor::generate_key(uint8_t* key, uint8_t* iv) {
#ifdef ENABLE_CRYPTO
    if (RAND_bytes(key, 32) != 1 || RAND_bytes(iv, 12) != 1) {
        throw std::runtime_error("Failed to generate random key/IV");
    }
#else
    throw std::runtime_error("Cryptographic support not compiled");
#endif
}

} // namespace mle