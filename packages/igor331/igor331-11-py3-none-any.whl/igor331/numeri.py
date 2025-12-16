'''
  converti_float - convert numero in float
  n2ita - numero float in formato italiano
  i2ita - numero intero in formato italiano


'''
def converti_float(importo):
      try:
         ret=float(importo)
      except:
         ret=0
      return(ret)

def n2ita(numero):
      try:
         numero = f"{numero:,.2f}"
         ret=numero.replace(".","_").replace(",",".").replace("_",",")
      except:
         ret=""
      return(ret)

def i2ita(numero):
      try:
         numero = f"{numero:,.0f}"
         ret=numero.replace(".","_").replace(",",".").replace("_",",")
      except:
         ret=""
      return(ret)

def main():
    print("function numeri")
    f = 10.5
    print(float(f))
    f = 111110.5
    print(n2ita(f))
    f = 10
    print(i2ita(f))
  
if __name__== "__main__":    
   main()
