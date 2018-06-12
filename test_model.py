import sqlite3
import time
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.utils import shuffle
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier


db_file = 'test.db'
db_conn = sqlite3.connect(db_file)
c = db_conn.cursor()


article_titles = []
article_isVoth = []
articles = []
results = c.execute('SELECT title, isVoth FROM Articles WHERE publisher=?', ('American Chemical Society (ACS)',))
for title, isVoth in results:
    article_titles.append(title)
    article_isVoth.append(isVoth)
    articles.append((title, isVoth))


data = pd.DataFrame.from_records(articles, columns=['title', 'isvoth'])
print(data)
print(data.groupby('isvoth').describe())
exit()
#print(len(article_titles), np.sum(article_isVoth))

article_titles, article_isVoth = shuffle(article_titles, article_isVoth)

train_X = article_titles[0::2]
train_y = article_isVoth[0::2]

test_X = article_titles[1::2]
test_y = article_isVoth[1::2]

# count_vect = CountVectorizer()
# X_train_counts = count_vect.fit_transform(train_X)
# print(X_train_counts.shape, len(train_X))
# print(count_vect.vocabulary_.get(u'algorithm'))

# tfidf_transformer = TfidfTransformer()
# X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
# print(X_train_tfidf.shape)

# from sklearn.naive_bayes import MultinomialNB
# clf = MultinomialNB().fit(X_train_tfidf, twenty_train.target)



# X_new_counts = count_vect.transform(test_X)
# X_new_tfidf = tfidf_transformer.transform(X_new_counts)

# predicted = clf.predict(X_new_tfidf)

# for doc, category in zip(test_X, predicted):
#     print('%r => %s' % (doc, twenty_train.target_names[category]))



from sklearn.pipeline import Pipeline
text_clf = Pipeline([('vect', CountVectorizer()),
                     ('tfidf', TfidfTransformer()),
                     ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                           alpha=1e-3, random_state=42,
                                           max_iter=2000, tol=None)),])


text_clf.fit(train_X, train_y)  
predicted = text_clf.predict(test_X)
print(np.mean(predicted == test_y))

#print(np.sum(predicted))


from sklearn import metrics
print(metrics.classification_report(test_y, predicted,
    target_names=['is not Voth', 'is voth']))

print(metrics.confusion_matrix(test_y, predicted))

