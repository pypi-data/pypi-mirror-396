"""
Environment-agnostic configuration loader for testing-engine-core.

This module provides utilities to load test configuration from multiple sources:
1. Environment variables (highest priority)
2. Config files (JSON/Python)
3. Default values (fallback)

This enables tests to work across dev, staging, prod, etc. without hardcoded URLs.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


def load_config_from_file(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON or Python file.
    
    Args:
        config_path: Path to config file (e.g., config/dev.json, config/prod.json)
    
    Returns:
        Dictionary with configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is unsupported
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    if config_file.suffix == '.json':
        with open(config_file, 'r') as f:
            return json.load(f)
    elif config_file.suffix == '.py':
        # Import Python config file as module
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", config_file)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module.CONFIG
    else:
        raise ValueError(f"Unsupported config file format: {config_file.suffix}")


def get_test_config(config_file: Optional[str] = None, environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Get test configuration from environment or config file.
    
    Priority (highest to lowest):
    1. Environment variables (e.g., USER_SERVICE_URL, DB_HOST)
    2. Config file specified by config_file parameter
    3. Config file specified by TEST_CONFIG_FILE env var
    4. Environment-based config file (config/{env}.json where env from TEST_ENV)
    5. Default config file (config/dev.json)
    6. Fallback defaults (localhost)
    
    Args:
        config_file: Optional path to config file
        environment: Optional environment name (e.g., 'dev', 'staging', 'prod')
    
    Returns:
        Configuration dictionary with keys: services, database, rabbitmq, test
        
    Example:
        >>> config = get_test_config()
        >>> config = get_test_config(config_file='config/staging.json')
        >>> config = get_test_config(environment='prod')
    """
    # Determine which config file to use
    target_config_file = None
    
    if config_file:
        target_config_file = config_file
    elif os.getenv('TEST_CONFIG_FILE'):
        target_config_file = os.getenv('TEST_CONFIG_FILE')
    else:
        # Use environment-based config
        env = environment or os.getenv('TEST_ENV', 'dev')
        env_config = Path(f'config/{env}.json')
        if env_config.exists():
            target_config_file = str(env_config)
    
    # Try to load from config file
    if target_config_file:
        try:
            base_config = load_config_from_file(target_config_file)
        except Exception as e:
            print(f"⚠️  Failed to load config file '{target_config_file}': {e}")
            print("   Falling back to environment variables")
            base_config = _get_default_config()
    else:
        base_config = _get_default_config()
    
    # Override with environment variables (highest priority)
    return _merge_with_env_vars(base_config)


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration with localhost values."""
    return {
        'services': {},
        'database': {
            'host': 'localhost',
            'port': 5432,
            'username': 'testuser',
            'password': 'testpass',
            'database': 'testdb'
        },
        'rabbitmq': {
            'host': 'localhost',
            'port': 5672,
            'username': 'guest',
            'password': 'guest'
        },
        'test': {
            'timeout': 30,
            'retry_attempts': 3,
            'message_wait_timeout': 10
        }
    }


def _merge_with_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge configuration with environment variables (env vars take priority)."""
    
    # Services - check for individual service env vars
    services = config.get('services', {}).copy()
    
    # Check for custom services JSON
    custom_services_json = os.getenv('CUSTOM_SERVICES')
    if custom_services_json:
        try:
            services.update(json.loads(custom_services_json))
        except json.JSONDecodeError:
            print(f"⚠️  Invalid CUSTOM_SERVICES JSON: {custom_services_json}")
    
    # Check for individual service URLs
    # This allows any service name to be configured via {SERVICE_NAME}_SERVICE_URL
    for key in os.environ:
        if key.endswith('_SERVICE_URL'):
            service_name = key[:-12].lower()  # Remove _SERVICE_URL and lowercase
            services[service_name] = os.getenv(key)
    
    config['services'] = services
    
    # Database
    db = config.get('database', {}).copy()
    db['host'] = os.getenv('DB_HOST', db.get('host', 'localhost'))
    db['port'] = int(os.getenv('DB_PORT', str(db.get('port', 5432))))
    db['username'] = os.getenv('DB_USER', db.get('username', 'testuser'))
    db['password'] = os.getenv('DB_PASSWORD', db.get('password', 'testpass'))
    db['database'] = os.getenv('DB_NAME', db.get('database', 'testdb'))
    config['database'] = db
    
    # RabbitMQ
    mq = config.get('rabbitmq', {}).copy()
    mq['host'] = os.getenv('RABBITMQ_HOST', mq.get('host', 'localhost'))
    mq['port'] = int(os.getenv('RABBITMQ_PORT', str(mq.get('port', 5672))))
    mq['username'] = os.getenv('RABBITMQ_USER', mq.get('username', 'guest'))
    mq['password'] = os.getenv('RABBITMQ_PASSWORD', mq.get('password', 'guest'))
    config['rabbitmq'] = mq
    
    # Test settings
    test = config.get('test', {}).copy()
    test['timeout'] = int(os.getenv('TEST_TIMEOUT', str(test.get('timeout', 30))))
    test['retry_attempts'] = int(os.getenv('TEST_RETRY_ATTEMPTS', str(test.get('retry_attempts', 3))))
    test['message_wait_timeout'] = int(os.getenv('MESSAGE_WAIT_TIMEOUT', str(test.get('message_wait_timeout', 10))))
    config['test'] = test
    
    return config


def get_service_url(service_name: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get a specific service URL from configuration.
    
    Args:
        service_name: Name of the service (e.g., 'user', 'api', 'order')
        config: Optional configuration dict. If None, loads from get_test_config()
    
    Returns:
        Service URL
        
    Raises:
        KeyError: If service not found in configuration
        
    Example:
        >>> url = get_service_url('api')
        >>> url = get_service_url('order', config={'services': {'order': 'http://localhost:8001'}})
    """
    if config is None:
        config = get_test_config()
    
    url = config['services'].get(service_name)
    if not url:
        raise KeyError(f"Service '{service_name}' not found in configuration. Available: {list(config['services'].keys())}")
    
    return url


def print_current_config(config: Optional[Dict[str, Any]] = None):
    """
    Print the current configuration for debugging.
    
    Args:
        config: Optional configuration dict. If None, loads from get_test_config()
    """
    if config is None:
        config = get_test_config()
    
    print("\n" + "="*70)
    print("🔧 Current Test Configuration")
    print("="*70)
    
    if config['services']:
        print("\n📡 Services:")
        for name, url in config['services'].items():
            print(f"  • {name}: {url}")
    else:
        print("\n📡 Services: (none configured)")
    
    print("\n🗄️  Database:")
    db = config['database']
    print(f"  • Host: {db['host']}:{db['port']}")
    print(f"  • Database: {db['database']}")
    print(f"  • User: {db['username']}")
    
    print("\n🐰 RabbitMQ:")
    mq = config['rabbitmq']
    print(f"  • Host: {mq['host']}:{mq['port']}")
    print(f"  • User: {mq['username']}")
    
    print("\n⚙️  Test Settings:")
    test = config['test']
    print(f"  • Timeout: {test['timeout']}s")
    print(f"  • Retry Attempts: {test['retry_attempts']}")
    print(f"  • Message Wait: {test['message_wait_timeout']}s")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    # Demo: Print current configuration
    print_current_config()
    
    # Demo: Get specific service URL
    try:
        config = get_test_config()
        if config['services']:
            first_service = list(config['services'].keys())[0]
            url = get_service_url(first_service)
            print(f"{first_service} service URL: {url}")
    except Exception as e:
        print(f"Note: {e}")
