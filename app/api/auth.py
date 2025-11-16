from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, set_access_cookies
from flask_babel import gettext as _
from app.application.common.mediator import mediator
from app.application.users.commands.commands import LoginCommand
from app.security.auth import init_jwt
from app.api.schemas.auth_schema import LoginSchema
from app.utils.response import success_response, error_response

auth_bp = Blueprint("auth", __name__)

# JWT is now initialized in create_app(), so we don't need this hook
# @auth_bp.record_once
# def on_load(state):
#     app = state.app
#     init_jwt(app)

@auth_bp.post("/login")
def login():
    """Login endpoint - returns JWT token on success and sets it as a cookie."""
    try:
        data = LoginSchema().load(request.get_json() or {})
        command = LoginCommand(username=data['username'], password=data['password'])
        user_dto = mediator.dispatch(command)
        
        if user_dto is None:
            return error_response(_('Invalid username or password'), status_code=401)
        
        # Create success response - get the Response object
        response_tuple = success_response({
            'access_token': user_dto.token,
            'user': {
                'id': user_dto.id,
                'username': user_dto.username,
                'role': user_dto.role
            }
        }, message=_('Login successful'))
        
        # Extract Response object from tuple
        response_obj = response_tuple[0] if isinstance(response_tuple, tuple) else response_tuple
        
        # Set JWT token as HTTP-only cookie for frontend page loads
        # This allows verify_jwt_in_request() to find the token in cookies
        set_access_cookies(response_obj, user_dto.token)
        
        return response_tuple
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return error_response(_('Login failed: {}').format(str(e)), status_code=500)


@auth_bp.get("/me")
@jwt_required()
def me():
    claims = get_jwt()
    return jsonify({
        "user_id": claims.get("sub"),
        "username": claims.get("username"),
        "roles": claims.get("roles", []),
    })