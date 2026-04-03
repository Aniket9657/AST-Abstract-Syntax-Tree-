"""n=5
while n>0:
    print("  "*(5-n), end=" ")
    print(n* " *  ")

    n-=1"""

"""n=0
while n<=5:
    print("  "*(5-n), end=" ")
    print(n* "  *  ")
    n+=1    """
    




"""L1 = input("Enter the List of Numbers: ")
print(L1)
L1 = L1.split(",")

print(L1)
L1.sort()
print(L1)

"""

"""L1 = input("Enter the List of Numbers: ")
L1 = L1.split(",")

print(L1)"""




def caught_speeding(speed, is_birthday):

    if is_birthday:
        speed -= 5   # 🎯 this is the +5 tolerance

    if speed <= 60:
        return "No Ticket"
    elif speed <= 80:
        return "Small Ticket"
    else:
        return "Big Ticket"
    
    
    
print(caught_speeding(64, 3/4))

    
    
         
                
            
        