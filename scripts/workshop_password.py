"""Print a salted workshop password hash; password is read from the terminal only."""
from getpass import getpass

from app.core.workshop_auth import hash_password


def main():
    password = getpass("Workshop password (16+ printable ASCII characters): ")
    if password != getpass("Repeat password: "):
        raise SystemExit("Passwords differ; no hash generated")
    try:
        print(hash_password(password))
    except ValueError as error:
        raise SystemExit(str(error)) from None


if __name__ == "__main__":
    main()
