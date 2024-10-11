import os
import django

# Thay thế 'web_blog_project' bằng tên chính xác của dự án của bạn
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_blog_project.settings')

# Khởi động Django
django.setup()

from django.contrib.auth.models import User
from faker import Faker

fake = Faker()

def populate_users(n=20):
    for _ in range(n):
        username = fake.user_name()
        email = fake.email()
        password = 'testpassword123'

        User.objects.create_user(username=username, email=email, password=password)

    print(f'{n} users have been created successfully.')

if __name__ == '__main__':
    populate_users()
