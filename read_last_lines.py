with open('main.py', 'r') as f:
    lines = f.readlines()
    # Print the last 50 lines
    for line in lines[-50:]:
        print(line, end='')