from werkzeug.security import generate_password_hash

# Input the password you want to hash
password = 'larry123'

# Generate the hashed password
hashed_password = generate_password_hash(password)

# Print the hashed password
print(hashed_password)
