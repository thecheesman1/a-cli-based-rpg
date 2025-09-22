with open('main.py', 'r') as f:
    lines = f.readlines()
    # Print from line 100 to the end
    for i, line in enumerate(lines):
        if i >= 100:
            print(line, end='')