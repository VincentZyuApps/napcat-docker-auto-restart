package config

import (
	"fmt"
	"os"
	"path/filepath"

	"gopkg.in/yaml.v3"
)

type ContainerConfig struct {
	Enabled     bool   `yaml:"enabled"`
	Name        string `yaml:"name"`
	SSHUser     string `yaml:"ssh_user"`
	SSHHost     string `yaml:"ssh_host"`
	WSPort      int    `yaml:"ws_port"`
	Token       string `yaml:"token"`
	AutoRestart bool   `yaml:"auto_restart"`
	UseSudo     bool   `yaml:"use_sudo"`
}

type AppConfig struct {
	CheckIntervalMS   int               `yaml:"check_interval_ms"`
	StaggerIntervalMS int               `yaml:"stagger_interval_ms"`
	Containers        []ContainerConfig `yaml:"containers"`
}

func LoadConfig() (*AppConfig, error) {
	// Try to find config.yaml
	configPath := "config.yaml"
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		// Try parent
		parentPath := filepath.Join("..", "config.yaml")
		if _, err := os.Stat(parentPath); err == nil {
			configPath = parentPath
		} else {
			// Try py directory
			pyPath := filepath.Join("..", "py", "config.yaml")
			if _, err := os.Stat(pyPath); err == nil {
				configPath = pyPath
			} else {
				return nil, fmt.Errorf("config.yaml not found in ., .., or ../py/")
			}
		}
	}

	fmt.Printf("Using config file: %s\n", configPath)

	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}

	// We'll use a temporary structure to handle defaults for bools
	type containerJSON struct {
		Enabled     *bool  `yaml:"enabled"`
		Name        string `yaml:"name"`
		SSHUser     string `yaml:"ssh_user"`
		SSHHost     string `yaml:"ssh_host"`
		WSPort      int    `yaml:"ws_port"`
		Token       string `yaml:"token"`
		AutoRestart *bool  `yaml:"auto_restart"`
		UseSudo     *bool  `yaml:"use_sudo"`
	}
	type configJSON struct {
		CheckIntervalMS   int             `yaml:"check_interval_ms"`
		StaggerIntervalMS int             `yaml:"stagger_interval_ms"`
		Containers        []containerJSON `yaml:"containers"`
	}

	var raw configJSON
	err = yaml.Unmarshal(data, &raw)
	if err != nil {
		return nil, err
	}

	cfg := &AppConfig{
		CheckIntervalMS:   raw.CheckIntervalMS,
		StaggerIntervalMS: raw.StaggerIntervalMS,
	}

	if cfg.CheckIntervalMS == 0 {
		cfg.CheckIntervalMS = 10000
	}
	if cfg.StaggerIntervalMS == 0 {
		cfg.StaggerIntervalMS = 500
	}

	for _, c := range raw.Containers {
		container := ContainerConfig{
			Name:    c.Name,
			SSHUser: c.SSHUser,
			SSHHost: c.SSHHost,
			WSPort:  c.WSPort,
			Token:   c.Token,
		}

		if c.Enabled == nil {
			container.Enabled = true
		} else {
			container.Enabled = *c.Enabled
		}

		if c.AutoRestart == nil {
			container.AutoRestart = true
		} else {
			container.AutoRestart = *c.AutoRestart
		}

		if c.UseSudo == nil {
			container.UseSudo = false
		} else {
			container.UseSudo = *c.UseSudo
		}

		cfg.Containers = append(cfg.Containers, container)
	}

	return cfg, nil
}
