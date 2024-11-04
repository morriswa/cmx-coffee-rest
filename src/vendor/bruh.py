import os

# Get the list of all files in the current directory
current_dir = os.getcwd()  # Ensures the current working directory is correct
files = os.listdir(current_dir)  # List all files in the current directory

for filename in files:
    # Construct the full file path
    file_path = os.path.join(current_dir, filename)

    # Process only files, skip directories
    if os.path.isfile(file_path):
        print(f"\nReading File: {filename}\n" + '-' * 50)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    print(line, end='')  # Print each line without extra newlines
        except Exception as e:
            print(f"Error reading {filename}: {e}")
        print('\n' + '-' * 50)
