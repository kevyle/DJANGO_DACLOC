Django demo project (minimal)
- Custom user model: core.Account (subclass of AbstractUser), set in AUTH_USER_MODEL
- Post model: core.Post, fields: author (Account), content, image, video
- Views:
  - user_create: creates a user (similar structure to the one you provided)
  - post_create: creates a post (structure analogous to your example)
Setup:
  1. Create virtualenv and install requirements.txt
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
  2. Run migrations:
     python manage.py makemigrations
     python manage.py migrate
  3. Create superuser if desired:
     python manage.py createsuperuser
  4. Run server:
     python manage.py runserver
Media files will be saved to the 'media' folder.
