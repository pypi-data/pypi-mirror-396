package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/zalando/go-keyring"
)

const (
	// ServiceName is the service name used in the keyring
	ServiceName = "tinker-cli"
	// APIKeyUser is the username for the API key credential
	APIKeyUser = "api-key"
	// BridgeURLUser is the username for the bridge URL credential
	BridgeURLUser = "bridge-url"
)

// Config holds the application configuration
type Config struct {
	APIKey    string
	BridgeURL string
}

// ConfigFile represents the JSON config file structure
type ConfigFile struct {
	APIKey    string `json:"api_key,omitempty"`
	BridgeURL string `json:"bridge_url,omitempty"`
}

// getConfigDir returns the config directory path
// Uses XDG_CONFIG_HOME on Linux/macOS, or %APPDATA% on Windows
func getConfigDir() string {
	// Check XDG_CONFIG_HOME first (Linux/macOS standard)
	if xdgConfig := os.Getenv("XDG_CONFIG_HOME"); xdgConfig != "" {
		return filepath.Join(xdgConfig, "tinker-cli")
	}

	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}

	// On Windows, use %APPDATA%/tinker-cli
	// On Unix, use ~/.config/tinker-cli
	if os.Getenv("APPDATA") != "" {
		return filepath.Join(os.Getenv("APPDATA"), "tinker-cli")
	}

	return filepath.Join(home, ".config", "tinker-cli")
}

// getConfigFilePath returns the full path to the config file
func getConfigFilePath() string {
	return filepath.Join(getConfigDir(), "config.json")
}

// loadConfigFile loads configuration from the JSON file
func loadConfigFile() (*ConfigFile, error) {
	path := getConfigFilePath()
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return &ConfigFile{}, nil
		}
		return nil, err
	}

	var cfg ConfigFile
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

// saveConfigFile saves configuration to the JSON file
func saveConfigFile(cfg *ConfigFile) error {
	dir := getConfigDir()
	if dir == "" {
		return fmt.Errorf("could not determine config directory")
	}

	// Create directory with restricted permissions (owner only)
	if err := os.MkdirAll(dir, 0700); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}

	// Write file with restricted permissions (owner read/write only)
	if err := os.WriteFile(getConfigFilePath(), data, 0600); err != nil {
		return fmt.Errorf("failed to write config file: %w", err)
	}

	return nil
}

// GetAPIKey retrieves the API key from environment, config file, or keyring
// Priority: 1. Environment variable, 2. Config file, 3. Keyring (legacy fallback)
func GetAPIKey() (string, error) {
	// 1. First check environment variable (highest priority)
	if key := os.Getenv("TINKER_API_KEY"); key != "" {
		return key, nil
	}

	// 2. Check config file (primary storage method)
	cfg, err := loadConfigFile()
	if err == nil && cfg.APIKey != "" {
		return cfg.APIKey, nil
	}

	// 3. Fallback to keyring (for backwards compatibility with existing users)
	// This also handles migration - if key exists in keyring, it will be found
	key, err := keyring.Get(ServiceName, APIKeyUser)
	if err == nil && key != "" {
		return key, nil
	}

	return "", fmt.Errorf("API key not configured. Please set it in Settings or via TINKER_API_KEY environment variable")
}

// SetAPIKey stores the API key in the config file
// This replaces the keyring-based storage to avoid macOS Keychain issues
func SetAPIKey(key string) error {
	key = strings.TrimSpace(key)
	if key == "" {
		return fmt.Errorf("API key cannot be empty")
	}

	// Load existing config to preserve other settings
	cfg, _ := loadConfigFile()
	if cfg == nil {
		cfg = &ConfigFile{}
	}

	cfg.APIKey = key

	if err := saveConfigFile(cfg); err != nil {
		return fmt.Errorf("failed to save API key: %w", err)
	}

	return nil
}

// DeleteAPIKey removes the API key from config file and keyring
func DeleteAPIKey() error {
	// Remove from config file
	cfg, _ := loadConfigFile()
	if cfg != nil {
		cfg.APIKey = ""
		saveConfigFile(cfg)
	}

	// Also try to remove from keyring for cleanup (ignore errors)
	keyring.Delete(ServiceName, APIKeyUser)

	return nil
}

// HasAPIKey checks if an API key is configured (env, config file, or keyring)
func HasAPIKey() bool {
	if os.Getenv("TINKER_API_KEY") != "" {
		return true
	}

	cfg, err := loadConfigFile()
	if err == nil && cfg.APIKey != "" {
		return true
	}

	_, err = keyring.Get(ServiceName, APIKeyUser)
	return err == nil
}

// GetAPIKeySource returns where the API key is configured
func GetAPIKeySource() string {
	if os.Getenv("TINKER_API_KEY") != "" {
		return "environment"
	}

	cfg, err := loadConfigFile()
	if err == nil && cfg.APIKey != "" {
		return "config"
	}

	_, err = keyring.Get(ServiceName, APIKeyUser)
	if err == nil {
		return "keyring"
	}

	return "not configured"
}

// GetBridgeURL retrieves the bridge URL from environment, config file, or keyring
func GetBridgeURL() string {
	// First check environment variable
	if url := os.Getenv("TINKER_BRIDGE_URL"); url != "" {
		return url
	}

	// Check config file
	cfg, err := loadConfigFile()
	if err == nil && cfg.BridgeURL != "" {
		return cfg.BridgeURL
	}

	// Fallback to keyring (legacy)
	url, err := keyring.Get(ServiceName, BridgeURLUser)
	if err == nil && url != "" {
		return url
	}

	// Default
	return "http://127.0.0.1:8765"
}

// SetBridgeURL stores the bridge URL in the config file
func SetBridgeURL(url string) error {
	url = strings.TrimSpace(url)
	if url == "" {
		return fmt.Errorf("bridge URL cannot be empty")
	}

	// Load existing config to preserve other settings
	cfg, _ := loadConfigFile()
	if cfg == nil {
		cfg = &ConfigFile{}
	}

	cfg.BridgeURL = url

	if err := saveConfigFile(cfg); err != nil {
		return fmt.Errorf("failed to save bridge URL: %w", err)
	}

	return nil
}

// MaskAPIKey returns a masked version of the API key for display
func MaskAPIKey(key string) string {
	if len(key) <= 8 {
		return strings.Repeat("•", len(key))
	}
	return key[:4] + strings.Repeat("•", len(key)-8) + key[len(key)-4:]
}

// LoadConfig loads all configuration
func LoadConfig() (*Config, error) {
	apiKey, _ := GetAPIKey() // Don't error if not found
	bridgeURL := GetBridgeURL()

	return &Config{
		APIKey:    apiKey,
		BridgeURL: bridgeURL,
	}, nil
}

// GetConfigFilePath returns the config file path (exported for display in UI)
func GetConfigFilePath() string {
	return getConfigFilePath()
}
