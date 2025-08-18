from sys import exit
import functions_logik as fl


name_file = input("Введи шлях та назву банківського звіту разом з .csv")


def main():
    while True:

        print(fl.MENU)
        user_input = input("Обери команду: ").strip().lower()
        if user_input == "1":
            data_from_report = fl.extract_csv(name_file)
            fl.create_list_dict(data_from_report, fl.mcc_codes)
            print(fl.report_data_for_exel())
        elif user_input == "2":
            user_search = input("""
Пошук виконується по МСС-коду, назві компанії, сумі транзакції.
Введи шукане значення: """)
            fl.search_in_union_data(user_search)
        elif user_input == "3":
            print(fl.see_ready_data())
        elif user_input == "q" or user_input == "й":
            exit()
        else:
            print("Немає такої команди.\n")
        #     print(MENU)
        # user_input = input().strip().lower()


if __name__ == '__main__':
    main()
