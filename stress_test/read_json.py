with open('./format.json', 'r') as f: 
    for line in f: 
        line = line.strip('\n')
        format_line = f'"{line}",'
        print(format_line)