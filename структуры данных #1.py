def trsl():
    print("задание со словарями:")

    translate_dict = {"blue": "синий", "red": "красный", "green": "зеленый"}
    a = input("your word: ")
    try:
        print(translate_dict[a])
    except:
        print("не нашел")


def list():
    print("задание с списками:")
    list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    slise5_10 = list[4:10]
    rev_slise5_10 = slise5_10[::-1]
    slise1_5 = list[0:5:1]
    rev_slise1_5 = slise1_5[::-1]
    чётные = list[1:10:2]
    нечётные = list[0:9:2]
    print("список: ", list)
    print("срез с 1 по 5: ", slise5_10)
    print("срез с 5 по 10: ", slise1_5)
    print("инверсия среза с 1 по 5: ", rev_slise1_5)
    print("инверсия среза с 5 по 10: ", rev_slise5_10)
    print("чётные:", чётные)
    print("нечётные", нечётные)


list()