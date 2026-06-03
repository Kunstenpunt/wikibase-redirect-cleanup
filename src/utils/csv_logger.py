import csv

class Logger:
    def __init__(self, filename='log.csv'):
        self.filename = filename
    
    def write_row(self, row):
        with open(self.filename, mode='a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)
