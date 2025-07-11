from collections import UserDict
from datetime import datetime, timedelta
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, number: str):
        phone = Phone(number)
        self.phones.append(phone)
        
    def remove_phone(self, number: str):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == number:
                phone_to_remove = phone
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
            return True
        return False

    def edit_phone(self, old_number: str, new_number: str):
        for i, phone in enumerate(self.phones):
            if phone.value == old_number:
                self.phones[i] = Phone(new_number)
                return True
        raise ValueError("Old phone not found.")

    def find_phone(self, number: str):
        for phone in self.phones:
            if phone.value == number:
                return phone.value
        return None

    def add_birthday(self, bday: str):
        self.birthday = Birthday(bday)

    def __str__(self):
        phones_str = "; ".join(str(p) for p in self.phones) if self.phones else "No phones"
        bday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "no birthday listed"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {bday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        congratulations = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year).date()
                # Якщо день народження вже був цього року — дивимось наступний рік
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                if today <= birthday_this_year <= next_week:
                    congrats_date = birthday_this_year
                    # Якщо день народження припадає на суботу або неділю, переносимо на понеділок
                    if congrats_date.weekday() >= 5:
                        days_to_monday = 7 - congrats_date.weekday()
                        congrats_date += timedelta(days=days_to_monday)
                    congratulations.append({
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y")
                    })

        return congratulations


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(birthday_date)



def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter the argument for the command"
        except KeyError:
            return "Contact not found. Please enter a valid user name."
        except ValueError as e:
            return str(e) 
    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError()
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError()
    return "; ".join(p.value for p in record.phones)

@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts yet."
    return "\n".join(str(rec) for rec in book.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, bday_str, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError()
    record.add_birthday(bday_str)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return "Birthday not found."
    return record.birthday.value.strftime("%d.%m.%Y")

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays this week."
    return "\n".join([f"{name}: {date}" for name, date in upcoming])


def parse_input(user_input):
    parts = user_input.strip().split()
    # Порожній ввід — повертаємо порожні значення
    if not parts:
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args




def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["exit", "close"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
