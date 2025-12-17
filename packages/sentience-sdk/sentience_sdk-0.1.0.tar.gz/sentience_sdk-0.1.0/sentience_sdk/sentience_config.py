from sentience_sdk.configuration import Configuration

class SentienceConfiguration(Configuration):
    """Custom Configuration wrapper for Sentience API with simplified authentication."""
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__(**kwargs)
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")
        # Automatically set the Authorization header with Bearer token
        self.api_key['Authorization'] = f"Bearer {api_key}" if not api_key.startswith('Bearer ') else api_key
