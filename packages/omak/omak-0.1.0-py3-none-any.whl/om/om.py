def cum(input:str):
  print(input)

def teasing(input1:str):
  import random
  
  x=random.randint(2,10000) #for x to be >1
  ln=len(input1)//x
  cum(input1[ln])  

def penetration(alist:list):
  for i in alist:
    alist.pop()
    cum(i)

def hedonism():
  import random
  random_num=random.randint(0,10)
  x=input("please input a number from 0-10: ")
  if x==random_num:
    cum("ommak")
  else:
    cum("your Operating system has been cummed on thank you for the good time")

def cuddling(): 
  xlist=["you are being bitcoin mined","omak","slaylaylay",""]
  for i in xlist:
    cum(i)

def fwb():
  cuddling()
  x=["we're just friends", "you're so iconic"]
  penetration(x)
  teasing("let's fuck we're just friends")
  cum("I dont have feelings for you btw")
