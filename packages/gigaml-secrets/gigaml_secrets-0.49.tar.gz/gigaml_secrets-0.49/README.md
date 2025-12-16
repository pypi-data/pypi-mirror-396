# GigaML Secrets

A library to manage AWS secrets with caching and environment variable integration.

## Installation

To install the package, use pip:

    pip install gigaml_secrets

## Setup

Ensure you have your AWS credentials configured. You can set them up using the AWS CLI:

    aws configure

## Usage

After installing the package, you can use the library in your scripts as follows:

1. **Use the library in your script**:

    ```python
    from gigaml_secrets import CachedSecretsManager, load_secrets
    import os

    def main():
        # Specify the environment and list of secrets to load
        env = 'prod'
        secret_names = ['ADMIN_API_KEY', 'BACKEND_API']
        load_secrets(env, secret_names)

        # Now you can access the secrets from environment variables
        admin_api_key = os.getenv('ADMIN_API_KEY')
        backend_api = os.getenv('BACKEND_API')

        print(f"ADMIN_API_KEY: {admin_api_key}")
        print(f"BACKEND_API: {backend_api}")

    if __name__ == "__main__":
        main()
    ```

2. **Run your script**:

    python your_script.py

## Example

Here is an example script (`main.py`) that demonstrates how to use the `gigaml_secrets` package:

    ```python
    import os
    from gigaml_secrets import CachedSecretsManager, load_secrets

    def main():
        # Initialize the CachedSecretsManager
        env = 'prod'
        secret_names = ['ADMIN_API_KEY', 'BACKEND_API']
        load_secrets(env, secret_names)

        # Fetch and set secrets as environment variables
        for name in secret_names:
            print(f"Environment variable {name}: {os.getenv(name)}")

    if __name__ == "__main__":
        main()
    ```

## License

This project is licensed under the MIT License.