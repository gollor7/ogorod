strs = ["flower","flow","flight"]

def longestCommonPrefix(strs):
    letters = {}
    index = 0
    for word in strs:
        words = list(word)
        letters[index] = words
        index += 1
        print(letters)
    index = 0
    counter = 0
    for i in letters[index]:
        if i == letters[index][counter]:
            index += 1
            counter += 1
            return


longestCommonPrefix(strs)
