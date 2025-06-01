from app.models import db
from app.models.user import User
from app.services.emotional_module import EmotionalMemory # For potential profile summary

class ProfileService:
    def get_user_profile(self, user_id: int):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        # Optionally, fetch some emotional summary if desired for the profile
        # emotional_memory = EmotionalMemory(user_id=user_id)
        # context = emotional_memory.get_user_context(days=30) # Example: 30-day summary

        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            # "current_wellness_score": context.wellness_score, # Example additional data
            # "dominant_themes": [t[0] for t in context.dominant_themes] # Example
        }
        return profile_data, None

    def update_user_profile(self, user_id: int, data: dict):
        user = User.query.get(user_id)
        if not user:
            return None, "User not found"

        errors = {}
        # Update username if provided and different
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                errors['username'] = "Username already taken."
            else:
                user.username = data['username']

        # Update email if provided and different
        if 'email' in data and data['email'] != user.email:
            if User.query.filter_by(email=data['email']).first():
                errors['email'] = "Email already registered."
            else:
                user.email = data['email']

        # Update password if 'current_password' and 'new_password' are provided
        if 'current_password' in data and 'new_password' in data:
            if not user.check_password(data['current_password']):
                errors['password'] = "Current password incorrect."
            elif len(data['new_password']) < 6: # Example minimum length
                errors['password'] = "New password must be at least 6 characters."
            else:
                user.set_password(data['new_password'])
        elif ('current_password' in data and 'new_password' not in data) or \
             ('current_password' not in data and 'new_password' in data):
            errors['password'] = "Both current and new password are required to change password."


        if errors:
            return None, errors

        try:
            db.session.commit()
            # Fetch updated profile data to return
            updated_profile_data, _ = self.get_user_profile(user_id)
            return updated_profile_data, None
        except Exception as e:
            db.session.rollback()
            # Log the exception e
            return None, {"database_error": str(e)}
