import os

class Config:
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'federation.db')
    
    # Federation configuration
    FEDERATION_ENTITY_ID = os.getenv('FEDERATION_ENTITY_ID', 'https://federation.example.com')
    ORGANIZATION_NAME = os.getenv('ORGANIZATION_NAME', 'Example Federation')
    
    # Key configuration
    KEY_SIZE = 2048
    KEY_ALGORITHM = 'RS256'
    
    # Statement validity
    STATEMENT_LIFETIME = 86400  # 24 hours in seconds
    
    # API configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Well-known paths
    WELL_KNOWN_FEDERATION = '/.well-known/openid-federation'
