import datetime


def oggi3():
    oggi3 = datetime.datetime.today()
    oggi3_st = str(oggi3.year) +str(oggi3.month).rjust(2,'0')  + str(oggi3.day).rjust(2,'0')+ str(oggi3.hour).rjust(2,'0')+ str(oggi3.minute).rjust(2,'0')
    return(str(oggi3))

def main():
    x=oggi3()
    print(x)

  
if __name__== "__main__":    
   main()
