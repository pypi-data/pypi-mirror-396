from scientiflow_cli.services.request_handler import make_no_auth_request, make_auth_request
from scientiflow_cli.cli.auth_utils import setAuthToken
import os
import re

class AuthService:
    def login(self, email: str, password: str):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return {
                "success": False,
                "message": f"{email} is not a valid email."
            }

        payload = {
            "email": email,
            "password": password,
            "device_name": "Google-Windows",
            "remember": True
        }

        response = make_no_auth_request(endpoint="/auth/login", method="POST", data=payload)
        if response.status_code == 200:
            auth_token = response.json().get("token")
            if auth_token:
                setAuthToken(auth_token)
                return {
                    "success": True,
                    "message": "Login successful!"
                }
            else:
                return {
                    "success": False,
                    "message": "No token received from the server."
                }
        else:
            return {
                "success": False,
                "message": response.json().get('message', 'Unknown error')
            }

    def logout(self):
        try:
            response = make_auth_request(endpoint="/auth/logout", method="POST", error_message="Unable to Logout!")
            if response.status_code == 200:
                token_file_path = os.path.expanduser("~/.scientiflow/token")
                key_file_path = os.path.expanduser("~/.scientiflow/key")
                os.remove(token_file_path)
                os.remove(key_file_path)
                return {
                    "success": True,
                    "message": "Logout successful!"
                }
        except Exception as e:
            error_message = f"Error during logout: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nDetails: {e.response.text}"
            return {
                "success": False,
                "message": error_message
            }
        return {
            "success": False,
            "message": "Unknown error during logout."
        }

    def get_user_info(self):
        try:
            response = make_auth_request(endpoint="/auth/user-info", method="GET", error_message="Unable to fetch user info!")
            if response.status_code == 200:
                user_info = response.json()
                return {
                    "success": True,
                    "data": user_info
                }
            else:
                # Handles cases like 401 Unauthorized
                error_message = response.json().get("message", "Unknown error")
                return {
                    "success": False,
                    "message": error_message
                }
        except Exception as e:
            error_message = f"Error fetching user info: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f"\nDetails: {e.response.text}"
            return {
                "success": False,
                "message": error_message
            }