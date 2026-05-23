from fastapi import HTTPException, status

class AuthenticationFailed(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = ("Incorrect authentication credentials.",)

    def __init__(self, detail=None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class PermissionDenied(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = ("You do not have permission to perform this action.",)

    def __init__(self, detail=None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)
