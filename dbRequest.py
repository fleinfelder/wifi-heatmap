

class dbRequest:

    connection = None

    def __init__(self, con):
        self.connection = con

    def getCursor(self):
        return self.connection.cursor()

    def fetchAsArray(self, query, assoc=False):
        cur = self.getCursor()
        cur.execute(query)
        data = cur.fetchall()
        result = []
        if (assoc):
            dic = {}
            for row in data:
                if row == None:
                    return
                desc = cur.description
                for (name, value) in zip(desc, row):
                    dic[name[0]] = value
                result.append(dic)
        else:
            for row in data:
                result.append(row)
        return result
