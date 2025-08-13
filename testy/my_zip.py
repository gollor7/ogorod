from collections import Counter

text = []
with open('text.txt', 'r') as file:
    for line in file:
        text.extend(line.strip().split())

word_counts = Counter(text)
print(word_counts)
for word in text:
    if not word_counts[word]:
        word_counts[word]=0
    word_counts[word]+=1
print(word_counts)






