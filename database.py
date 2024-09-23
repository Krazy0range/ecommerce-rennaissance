import csv


class Database:

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.headers = []
        self.data = []

    def read_data(self, just_headers=False, func=None):
        with open(self.csv_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            self.headers = next(reader)
            if just_headers:
                return
            for row in reader:
                if func:
                    func(row)
                self.data.append(row)

    def write_data(self):
        with open(self.csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(self.headers)
            writer.writerows(self.data)

    def copy_db(self, db):
        self.headers = list(db.headers)
        self.data = list(db.data)
