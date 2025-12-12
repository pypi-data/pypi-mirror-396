from trinity_connect_client.exceptions import UnauthorisedError, ResourceNotFoundError


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            raise
        except UnauthorisedError:
            raise
        except PermissionError:
            raise
        except ResourceNotFoundError:
            raise
        except Exception:
            raise

    return wrapper
