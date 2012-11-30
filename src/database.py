import datetime
import psycopg2

class DatabaseHandler():

    def __init__(self):
        print 'DatabaseHandler instantiated'


        self.connection = psycopg2.connect('dbname=fzr.db user=postgres password=bob')
        
        self.cursor = self.connection.cursor()

    def createScenarioTable(self):
        # Database is empty, create table
        self.cursor.execute('''CREATE TABLE if not exists scTable
                        (now timestamp, scenario integer);''')
        self.cursor.commit()

    def insertRowToScenarioTable(self, scenario):
        now = datetime.datetime.now()
        self.cursor.execute('INSERT INTO scTable (now, scenario) VALUES (%s, %s)', [now, scenario])
        #cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        self.cursor.commit()

    def getLastScenario(self):
        result = self.cursor.mogrify('SELECT (now, scenario) FROM scTable ORDER BY now DESC, LIMIT 1')
        print 'Now:', result[0]
        print 'Scenario:', result[1]

        self.cursor.commit()

    def printDBRows(self):
        print self.cursor.mogrify('SELECT * FROM scTable')