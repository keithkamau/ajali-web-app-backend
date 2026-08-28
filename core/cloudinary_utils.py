import cloudinary
import cloudinary.uploader
from django.conf import settings

def get_cloudinary_config():
    """Get Cloudinary configuration from settings"""
    cloudinary_storage = getattr(settings, 'CLOUDINARY_STORAGE', {})
    return {
        'cloud_name': cloudinary_storage.get('CLOUD_NAME', ''),
        'api_key': cloudinary_storage.get('API_KEY', ''),
        'api_secret': cloudinary_storage.get('API_SECRET', ''),
    }

def configure_cloudinary():
    """Configure Cloudinary with settings"""
    config = get_cloudinary_config()
    if config['cloud_name'] and config['api_key'] and config['api_secret']:
        cloudinary.config(
            cloud_name=config['cloud_name'],
            api_key=config['api_key'],
            api_secret=config['api_secret'],
        )
        return True
    return False

def generate_upload_signature(folder="ajali/incidents", timestamp=None):
    """Generate a Cloudinary upload signature for client-side uploads"""
    configure_cloudinary()
    if not timestamp:
        import time
        timestamp = int(time.time())
    
    config = get_cloudinary_config()
    signature = cloudinary.utils.api_sign_request(
        {
            'timestamp': timestamp,
            'folder': folder,
            'upload_preset': getattr(settings, 'CLOUDINARY_UPLOAD_PRESET', ''),
        },
        config['api_secret']
    )
    return {
        'signature': signature,
        'timestamp': timestamp,
        'cloud_name': config['cloud_name'],
        'api_key': config['api_key'],
        'folder': folder,
    }

def upload_to_cloudinary(file, folder='ajali/incidents', resource_type='auto'):
    """Upload a file to Cloudinary"""
    if not configure_cloudinary():
        return {
            'url': None,
            'public_id': None,
            'format': None,
            'size': 0,
            'width': None,
            'height': None,
        }
    
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type=resource_type,
            allowed_formats=['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'avi', 'mov', 'webm'],
        )
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
            'format': result.get('format'),
            'size': result.get('bytes'),
            'width': result.get('width'),
            'height': result.get('height'),
        }
    except Exception as e:
        raise ValueError(f'File upload failed: {str(e)}')

def delete_from_cloudinary(public_id):
    """Delete a file from Cloudinary"""
    if not configure_cloudinary():
        return True
    
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        raise ValueError(f'File deletion failed: {str(e)}')