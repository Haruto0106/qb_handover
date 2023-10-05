lst = [0,1,2]

def sanshou(lst):
    lst[0] = 3
print(lst)
sanshou(lst)
print(lst)

lst_1 = [0,1,2]

def sanshoushinai():
    # lst_1 = []
    lst_1.append(4)

print(lst_1)
sanshoushinai()
print(lst_1)

num = 5

def func(a):
    global num
    b = a + 4
    a = 7
    c = num + 5
    num += 1
func(num)