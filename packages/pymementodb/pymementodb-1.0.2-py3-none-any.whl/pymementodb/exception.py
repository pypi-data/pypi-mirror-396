import json


class MementoBaseException(Exception):
    """ Base exception class for Memento.

    Attributes:
        message(str, optional): Exception message
        http_body(str, optional): HTTP body
        http_status(int, optional): HTTP status code
        http_headers(:obj:`dict`, optional): Dict containing header key and value
        errors(:obj:`json`, optional): JSON errors
    """
    def __init__(
        self,
        message=None,
        http_body=None,
        http_status=None,
        http_headers=None
    ):
        """
          Args:
                message(str, optional): Exception message
                http_body(str, optional): HTTP body
                http_status(int, optional): HTTP status code
                http_headers(:obj:`dict`, optional): Dict containing header key and value
        """
        super(MementoBaseException, self).__init__(message)

        if http_body and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = (
                    "<Could not decode body as utf-8>"
                )

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.http_headers = http_headers or {}
        self.errors = {}
        if self.http_body:
            try:
                body = json.loads(self.http_body)
                if "error" in body:
                    self.errors = {"base": body["error"]}
                if "errors" in body:
                    self.errors = body["errors"]
            except Exception:
                pass

    def __str__(self):
        msg = self._message or "<empty message>"
        return msg

    def __repr__(self):
        return "%s(message=%r, http_status=%r)" % (
            self.__class__.__name__,
            self._message,
            self.http_status
        )

    def setMessage(self, message):
        """ Sets the exception message
          Args:
                message(str): Exception message
        """
        self._message = message


class MementoException(MementoBaseException):
    """ Exception based on requests library Response.
    """
    def __init__(
        self,
        message,
        response=None
    ):
        """ Exception based on requests library Response.
        Args:
            message(str): Exception message
            response(:obj:`requests.Response`, optional): response object from requests library
        """
        super(MementoException, self).__init__(
            message=message
        )

        if response is not None:
            self.http_body = response.content,
            self.http_status = response.status_code,
            self.http_headers = response.headers


class MementoUnauthorizedException(MementoException):
    """ Exception when request to memento is unauthorized
    """
    pass


class MementoBadRequestException(MementoException):
    """ Exception when request returns bad request
    """
    pass


class MementoNotAllowedException(MementoException):
    """ Exception when request to memento is not allowed
    """
    pass

class MementoRateLimitException(MementoNotAllowedException):
    """ Exception when request to memento is not allowed
    """
    pass


class MementoNotFoundException(MementoException):
    """ Exception when request to memento returns not found
    """
    pass