
def append_txt(filename, text):
    with open(filename, 'a') as f:
        f.write(text+'\n')

def w_diagonal(filename,n:int):
    with open(filename, 'w') as f:
        for i in range(n):
            print(i*' '+str(i+1),file=f)
