nums = [3, 2, 3]
target = 6
def twoSum(nums, target):
    hesh_map = {}
    for i, num in enumerate(nums):
        yak_nazvatb = target - num
        if yak_nazvatb in hesh_map:
            return [hesh_map[yak_nazvatb], i]
        if num not in hesh_map:
            hesh_map[num] = i

result = twoSum(nums, target)
print(result)