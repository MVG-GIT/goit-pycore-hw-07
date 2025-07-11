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
        # Валідація: номер телефону має бути 10 цифр
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
        return False

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
        # Ключ - ім'я контакту
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




if __name__ == "__main__":
    # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john = Record("John")
    john.add_phone("1234567890")
    john.add_birthday("14.07.1990")
    # Додавання запису John до адресної книги
    book.add_record(john)

    # Створення та додавання нового запису для Jane
    jane = Record("Jane")
    jane.add_phone("5555555555")
    jane.add_birthday("13.07.1995")
    # Додавання запису Jane до адресної книги
    book.add_record(jane)
    
    
    # Обробка помилок
    cole = Record("Cole")
    try:
        cole.add_phone("123012312031203")
    except ValueError as e:
        print(f"Caught an error: {e}")
    cole.add_phone("1234567890")   
    
    try:
        cole.add_birthday("13.07.1995 12:31:31")
    except ValueError as e:
        print(f"Caught an error: {e}")
    cole.add_birthday("13.07.1995")
    
    
    # Додавання запису Jane до адресної книги
    book.add_record(cole)
    
    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    upcoming = book.get_upcoming_birthdays()
    print("Upcoming birthdays this week:")
    for entry in upcoming:
        print(f"Don't forget to congratulate {entry['name']} on {entry['congratulation_date']}")
    
    # Видалення запису Jane
    book.delete("Jane")

