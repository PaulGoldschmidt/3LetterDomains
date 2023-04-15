import string

# Generate all possible three-letter combinations of letters and digits without a hyphen
combinations = [a + b + c + '.de' for a in string.ascii_lowercase + string.digits for b in string.ascii_lowercase + string.digits for c in string.ascii_lowercase + string.digits]

# Generate all possible combinations of one letter or digit, a hyphen, and one letter or digit, with the hyphen in the middle
combinations_with_hyphen = [a + '-' + b + '.de' for a in string.ascii_lowercase + string.digits for b in string.ascii_lowercase + string.digits]

# Combine the two lists of combinations
combinations += combinations_with_hyphen

# Write the combinations to a file
with open('threeletterdomains.txt', 'w') as file:
    file.write('\n'.join(combinations))
