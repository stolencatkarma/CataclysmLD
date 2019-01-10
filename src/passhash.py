import os
import hashlib

# server has SALT and HASHED_PASSWORD
# client has password but needs SALT


def makeSalt():
    _salt = hashlib.sha256()
    _salt.update(os.urandom(60))
    # print(_salt.hexdigest())
    return _salt.hexdigest()


def hashPassword(password, salt):
    hash = hashlib.sha256()
    hash.update((password + salt).encode("utf-8"))
    return hash.hexdigest()


if __name__ == "__main__":
    _salt = makeSalt()
    print("hashed:", hashPassword("password", _salt))


# login process
# client logs in with username -> server sends SALT -> client sends back (hash(password + SALT)) -> server verifies against HASHED_PASSWORD
# at no time does the server or client send or recieve a plain text password.

# creation process
# server doesn't know about username
# user logs in and sends username
# if no account exists by that name create salt and send it.
# if client recieves salt ask if this is new user. if no, return and restart login.
# if yes, hash and salt the password and send to server.
# server stores hashed password along with the salt it generated.

# /accounts/username/SALT
# /accounts/username/HASHED_PASSWORD
# /accounts/username/characters/name1.character
# /accounts/username/characters/name1.character
