def Student(*args,**kwargs):
    print(args)
    for arg in args:
        print(arg)
    
    for k in kwargs:
        print(k,kwargs[k])
     
    print(kwargs)   
    
 
Student(1,2,3,name="jake",age=20)


 
 