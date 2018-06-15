# PredictJournalArticles
Create a model for predicting what journal articles the Voth Group should be reading

## Model Details

Four steps are necessary to parse the data, add the data to the database, build the model, and predict new relevant journal articles:

1. `gather_dois.py` : This python script parses the csv files, and creates a list of dois
2. `parse_crossref.py`: This python script does the following
 * creates the databse
 * reads the list of dois, retrieves the information for each doi, add the record to the database
 * looks at the journals that have been read, retrieves all articles published in these articles over the given timespan, and adds them to the databse
3. `Build_model.ipynb`: This jupyter notebook script builds a linear SVM from the data in the database
4. `Check_New_Articles.ipynb`: This jupyter notebook script retrieves new articles and uses the linear SVM to predict whether or not they are relevant

The model is biased (weighted) to give more false positives, as we expect that the number of actually relevant articles to be greater than the list of relevant articles in the database. Here, the confusion matrix shows that the model predicts almost everything perfectly, but it predicts some extra articles to be relevant, which is exactly what we wanted. 

![alt text][logo]

[logo]: https://github.com/mocohen/PredictJournalArticles/blob/master/confusion_matrix.png "Confusion Matrix"
