# config.py
import os
import json
CFG_PATH = './static/config.json'

def load_config(config_file=CFG_PATH):
    """Load configuration from JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        # Return default configuration if file can't be loaded
        return get_default_config()


def get_default_config():
    """Return default configuration if config file is not available."""
    return {
        "global": {
            "buffer_size": "1000",
            "sample_rate": 50
        },
        "plots": [
            {
                "title": f"Signal Monitor {i + 1}",
                "channels": [f"Dev1/ai{i}"] if i < 4 else [],
                "legend_strings": [],  # Empty means use channel names
                "y_scale_mode": "auto",
                "y_min": -10,
                "y_max": 10,
                "width": 600,
                "height": 200,
                "display_samples": "1000"
            }
            for i in range(4)
        ]
    }


def save_config(config_data, config_file=CFG_PATH):
    """Save configuration to JSON file."""
    try:
        # Plot properties
        # Fix any issues with the config data
        for i, plot in enumerate(config_data.get("plots", [])):
            if not plot.get("title"):
                plot["title"] = f"Signal Monitor {i + 1}"

            # Ensure legend_strings exists
            if "legend_strings" not in plot:
                plot["legend_strings"] = []
        # Save with pretty formatting
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config file: {e}")
        return False


def update_config(new_data, config_file=CFG_PATH):
    """Update configuration by merging new data with existing config."""
    try:
        # print(f"Data to merge into config: \n{new_data}")

        # Load existing config
        config_old = load_config(config_file)
        # print(f"Existing config loaded successfully")

        # Create a copy of the old config and update it
        config_new = config_old.copy()  # Make a shallow copy
        config_new.update(new_data)  # Update with new data

        # print(f"Config after merging: \n{config_new}")

        # Save the updated config
        success = save_config(config_new, config_file)

        if success:
            # print("Config updated successfully")
            # Update the global config instance
            global config
            config = config_new

        return success
    except Exception as e:
        print(f"Error updating config: {e}")
        return False


# def update_config(config_data, config_file=CFG_PATH):
#     """Update configuration from JSON file."""
#     # Save with pretty formatting
#     with open(config_file, 'w') as f:
#         json.dump(config_data, f, indent=2)


# Create a config instance that can be imported by other modules
config = load_config()