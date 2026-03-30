from copy import deepcopy
from copy import copy
List1=[1,2,[3,4],5]
l1=copy(List1)

l1.insert(4,6)
print(l1)
print(List1)

l2=deepcopy(List1)
l2.insert(4,7)
print(l2)
print(List1)