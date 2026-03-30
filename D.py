nums = eval(input("Enter the list of numbers: "))
target = int(input("Enter the target sum: "))
#output = [(2,7)]

def check_sum(nums,target):
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if nums[i]+nums[j]==target:
                return (nums[i],nums[j])
            
print(check_sum(nums,target))            