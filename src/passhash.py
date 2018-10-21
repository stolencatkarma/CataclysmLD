# Utility functions for managing salted hash passwords
import os
import hashlib


# Simply pass in a raw text password. The output is a salted, hashed
# password. Note, this function generates different output with every
# call, even with identical inputs. Which is, after all, entirely
# purpose of a salted hash password. Which is why the salt is part
# of the output. The output should be securely stored in its entirety.
def hashPassword( password ):
    salt = hashlib.sha256()
    salt.update(os.urandom(60))
    hexSalt = salt.hexdigest()

    hash = hashlib.sha256()
    hash.update((password + hexSalt).encode('utf-8'))
    hexHash = hash.hexdigest()
    newPass = hexSalt + hexHash

    return newPass


# This function accepts a raw text password and the stored
# salted hash password it is to be compared. Returns
# true if the password matches. False if they do not.
def validatePassword( password, saltedHash):
    salt = saltedHash[:64]
    saltedPass = password + salt

    hash = hashlib.sha256()
    hash.update( saltedPass.encode('utf-8') )
    calcSaltedHash = hash.hexdigest()

    return saltedHash[64:] == calcSaltedHash




if __name__ == '__main__':
    password =  'hownowbrowncow'
    saltedHash = hashPassword( password )
    print(saltedHash)
    print("EQUAL TRUE: {}".format(validatePassword( password, saltedHash )))
    print("EQUAL FALSE: {}".format(validatePassword( password*2, saltedHash )))

