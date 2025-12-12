from ruamel.yaml import YAML
import argparse
import os

def update_data_settings_getdp_path(file_path, env_variable):
    # Load the YAML file
    yaml = YAML()

    with open(file_path, 'r') as file:
        config = yaml.load(file)

    # Get the value of the environment variable
    env_value = os.environ.get(env_variable)
    if env_value is None:
        raise ValueError(f"Environment variable '{env_variable}' is not set.")

    # Update the GetDP_path with the expanded value
    config['GetDP_path'] = "C:/cerngetdp/getdp_" + env_value + ".exe"
    # Save the updated YAML file, preserving formatting
    with open(file_path, 'w') as file:
        yaml.dump(config, file)

    print(f"Updated 'GetDP_path' to use environment variable: {env_variable}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Update GetDP_path in a YAML file to use an environment variable.")
    parser.add_argument("file", help="Path to the YAML file.")
    parser.add_argument("env_variable", help="Name of the environment variable to use for GetDP_path.")
    args = parser.parse_args()
    
    # Call the function with the provided arguments
    update_data_settings_getdp_path(args.file, args.env_variable)