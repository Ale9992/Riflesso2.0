from flask import Blueprint, request, jsonify
from app.routes.auth import token_required
from app.models.user import User # Injected by token_required
from app.services.profile_service import ProfileService

profile_bp = Blueprint('profile', __name__)
profile_service = ProfileService() # Instantiate the service

@profile_bp.route('/', methods=['GET'])
@token_required
def get_profile(current_user: User):
    profile_data, error = profile_service.get_user_profile(current_user.id)
    if error:
        return jsonify({'message': error}), 404 # Or appropriate error code
    return jsonify(profile_data), 200

@profile_bp.route('/', methods=['PUT'])
@token_required
def update_profile(current_user: User):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided for update'}), 400

    updated_profile, errors = profile_service.update_user_profile(current_user.id, data)

    if errors:
        if isinstance(errors, str): # Single string error
            return jsonify({'message': errors}), 400
        else: # Dictionary of field errors
            return jsonify({'errors': errors}), 400

    return jsonify({'message': 'Profile updated successfully', 'profile': updated_profile}), 200
