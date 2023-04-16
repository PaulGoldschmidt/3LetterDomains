import string

# Define the TLD we're interested in
tld = ".com"

# Define the set of characters that can be used in a two-letter domain
letters = string.ascii_lowercase

# Ask the user if they want to include numbers in the SLD
include_numbers = input("Include numbers in the SLD? (y/n): ").lower() == "y"

# Create a list of all possible two-letter combinations with or without numbers
if include_numbers:
    characters = letters + string.digits
else:
    characters = letters
    
combinations = [a + b for a in letters for b in characters]

# Create a list of all valid two-letter domains for the TLD
valid_domains = [combo + tld for combo in combinations]

# Write the list of valid domains to a file
with open("com_twoletterdomains.txt", "w") as file:
    for domain in valid_domains:
        file.write(domain + "\n")

# Print the number of valid domains
print(f"Found {len(valid_domains)} valid domains for {tld}")