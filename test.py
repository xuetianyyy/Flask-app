from werkzeug.security import generate_password_hash, check_password_hash


pwd = generate_password_hash('123')


print(pwd)
print(check_password_hash('pbkdf2:sha256:150000$Cy1ZOT4L$0595fd89a092703a0754a6172876493a66216a85bedc7103eecbcf9372c7ad75', '123'))
