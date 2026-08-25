from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a super admin user'
    
    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--password', type=str, required=True, help='Admin password')
        parser.add_argument('--name', type=str, default='Admin', help='Admin full name')
    
    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists'))
            return
        
        user = User.objects.create_superuser(
            email=email,
            password=password,
            full_name=name,
            role='admin',
            is_verified=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin: {email}'))