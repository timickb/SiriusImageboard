def getDictFromTuple(tpl, table):
    USERS = ('id', 'login', 'password', 'email', 'regTime')
    TOPICS = ('id', 'title', 'creationTime', 'authorID', 'rating')
    MESSAGES = ('id', 'text', 'creationTime', 'topicID', 'authorID', 'image')
    gresult = []
    for element in tpl:
        result = {}
        if table == 'users':
            for i in range(len(element)):
                result[USERS[i]] = element[i]
        elif table == 'topics':
            for i in range(len(element)):
                result[TOPICS[i]] = element[i]
        else:
            for i in range(len(tpl)):
                result[MESSAGES[i]] = element[i]
        gresult.append(result)
    return gresult

r = getDictFromTuple(( (1, 'timickb', 'a23bc444', 'timi@ss.ru', '23782'), (2, 'timickb', 'a23bc444', 'timi@ss.ru', '23782') ), 'users')
print(r)