import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from edu.models import ParentStudentDetails, Profile, TutorProfile

class Command(BaseCommand):
    help = 'Seed the database with dummy parent and tutor profiles'

    def handle(self, *args, **kwargs):
        # Malaysian cities and states
        cities_states = [
            {"city": "Kuala Lumpur", "state": "Wilayah Persekutuan"},
            {"city": "George Town", "state": "Penang"},
            {"city": "Johor Bahru", "state": "Johor"},
            {"city": "Ipoh", "state": "Perak"},
            {"city": "Shah Alam", "state": "Selangor"},
        ]

        # Seed 5 parent profiles
        for i in range(1, 6):
            username = f"parent{i}"
            email = f"parent{i}@example.com"
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'first_name': f"Parent {i}",
            })

            if created:
                user.set_password("password123")  # Hash the password
                user.save()
                self.stdout.write(f"User {username} created.")
            else:
                self.stdout.write(f"User {username} already exists.")

            # Check if Profile exists
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'parent_student'})
            if created:
                self.stdout.write(f"Profile created for user {username}. Role: parent_student")
            else:
                profile.role = 'parent_student'  # Ensure role is set
                profile.save()
                self.stdout.write(f"Profile for user {username} updated to role: parent_student.")

            # Create ParentStudentDetails if it doesn't exist
            ParentStudentDetails.objects.get_or_create(
                user=user,
                defaults={
                    'age': random.randint(30, 50),
                    'phone_number': f"+60{random.randint(100000000, 999999999)}",
                    'street': f"{random.randint(1, 100)} Jalan Example",
                    **random.choice(cities_states),
                    'postcode': f"{random.randint(10000, 99999)}",
                    'country': "Malaysia",
                    'favorite_subjects': random.choice(["Math, Science", "English, History", "Biology, Chemistry"]),
                }
            )

        # Seed 15 tutor profiles
        for i in range(1, 16):
            username = f"tutor{i}"
            email = f"tutor{i}@example.com"
            user, created = User.objects.get_or_create(username=username, defaults={
                'email': email,
                'first_name': f"Tutor {i}",
            })

            if created:
                user.set_password("password123")  # Hash the password
                user.save()
                self.stdout.write(f"User {username} created.")
            else:
                self.stdout.write(f"User {username} already exists.")

            # Check if Profile exists
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'tutor_center'})
            if created:
                self.stdout.write(f"Profile created for user {username}. Role: tutor_center")
            else:
                profile.role = 'tutor_center'  # Ensure role is set
                profile.save()
                self.stdout.write(f"Profile for user {username} updated to role: tutor_center.")

            # Create TutorProfile if it doesn't exist
            TutorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'qualifications': random.choice(["Bachelor's in Education", "Master's in Physics", "Diploma in Teaching"]),
                    'specializations': random.choice(["Math, Science", "English, Literature", "Physics, Chemistry"]),
                    'teaching_experience': random.randint(1, 20),
                    'certifications': random.choice(["TESL Certified", "Cambridge Certified", "STEM Certification"]),
                    'hourly_rate': random.uniform(30.00, 150.00),
                    'weekly_hours': random.randint(10, 40),
                    'subjects_offered': random.choice(["Math, Science", "English, History", "Biology, Chemistry"]),
                    'availability_schedule': "Mon-Fri, 8am-5pm",
                    'bio': f"Experienced tutor with a passion for teaching. Loves helping students excel in {random.choice(['Math', 'Science', 'English'])}.",
                    'phone_number': f"+60{random.randint(100000000, 999999999)}",
                    'youtube_link': "https://www.youtube.com/watch?v=example",
                    'school_level': random.choice(["primary", "secondary", "preuniversity"]),
                    'street': f"{random.randint(1, 100)} Jalan Tutor",
                    **random.choice(cities_states),
                    'postcode': f"{random.randint(10000, 99999)}",
                    'country': "Malaysia",
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 5 parent profiles and 15 tutor profiles'))
