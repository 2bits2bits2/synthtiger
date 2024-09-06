import random

def generate_confusing_strings(num_strings, max_length):
    confusing_pairs = [
        'rn', 'mn', 'nm', 'im', 'in', 'il', 'li', 'cl', 'dl',
        'RN', 'MN', 'NM', 'IM', 'IN', 'IL', 'LI', 'CL', 'DL',
        'Rn', 'Mn', 'Nm', 'Im', 'In', 'Il', 'Li', 'Cl', 'Dl'
    ]
    
    def generate_string():
        length = random.randint(2, max_length)
        pairs_needed = length // 2
        string = ''.join(random.choice(confusing_pairs) for _ in range(pairs_needed))
        if length % 2 != 0:
            string += random.choice(''.join(confusing_pairs))
        return string[:max_length]
    
    with open('confusing.txt', 'w') as f:
        for _ in range(num_strings):
            f.write(generate_string() + '\n')

# Example usage:
# generate_confusing_strings(10, 6)  # Generates 10 strings with maximum length of 6


