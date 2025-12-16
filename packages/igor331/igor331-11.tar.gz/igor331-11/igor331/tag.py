from functools import partial
'''
     vedere se servono virgolette in tag
'''

def tag(testo,valore_tag):
    #ret = "<"+valore_tag + ">\""+testo+"\"</"+valore_tag + ">"
    ret = "<"+valore_tag + ">"+testo+"</"+valore_tag + ">"
    return(ret)

h_html  = partial(tag,valore_tag="html") 
h_li    = partial(tag,valore_tag="li")

def main():
    x=tag("nome tag","valore tag")
    print(x)
    x = h_html("igor")
    print(x)
    y=h_li("prova")
    print(y)

if __name__== "__main__":    
   main()
