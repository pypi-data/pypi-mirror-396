import datetime


def oggi_ita():
    oggi = datetime.datetime.today()
    oggi = str(oggi.day).rjust(2,'0') + "/"+\
           str(oggi.month).rjust(2,'0') + "/"+\
           str(oggi.year) 
    return(str(oggi))

def main():
    x=oggi_ita()
    print(x)

  
if __name__== "__main__":    
   main()
