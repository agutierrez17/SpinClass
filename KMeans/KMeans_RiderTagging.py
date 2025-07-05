import pyodbc
import joblib
import pandas as pd
import warnings
from sklearn import preprocessing
from sklearn.metrics import silhouette_score
from datetime import date, datetime, time
from time import sleep
warnings.filterwarnings("ignore")

# Get today's date
today = date.today()
print()
print("Today is " + str(today))
print()

# Load KMeans model
kmeans = joblib.load('KMeans_Spin.pkl')

# Load Principal Components
pca = joblib.load('PCA_Spin.pkl')

# Connect to database and open SQL cursor
print('Connecting to database...')
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
print('')

# Query Riders view
print('Querying Rider Data...')
sql = """
SELECT 
[Rider ID],
[First Name],
[Last Name],
[Email],
[First Ride],
[Most Recent Ride],
[Most Recent Ride Format],
[Most Recent Ride Location],
[Most Recent Ride Playlist],
[Number of Rides],
[Number of Locations],
[Top Location],
[Number of Rides - Last Month],
[Number of Rides - Last Three Months],
[Number of Rides - Last Six Months],
[Number of Rides - Last Twelve Months],
[Days Between First and Last Ride],
[Days Since First Ride],
[Days Since Last Ride],
[Average Days Between Rides],
[Average Weeks Between Rides],
[Rides per Month]
FROM [SpinClass].[dbo].[Riders]
"""
df = pd.read_sql(sql,conn)
print('')

# Pull out features to use with model
features = df[['Rider ID','First Name','Last Name','Number of Rides','Number of Locations','Number of Rides - Last Month','Number of Rides - Last Three Months','Number of Rides - Last Six Months','Number of Rides - Last Twelve Months','Days Between First and Last Ride','Days Since First Ride','Days Since Last Ride','Average Days Between Rides','Average Weeks Between Rides','Rides per Month']]

# Pull out features that need to be normalized
var_norms = ['Number of Rides','Number of Locations','Number of Rides - Last Month','Number of Rides - Last Three Months','Number of Rides - Last Six Months','Number of Rides - Last Twelve Months','Days Between First and Last Ride','Days Since First Ride','Days Since Last Ride','Average Days Between Rides','Average Weeks Between Rides','Rides per Month']

# Normalize features
print('Normalizing features...')
features_norm = preprocessing.normalize(features[var_norms])
features_norm = pd.DataFrame(features_norm, columns=features[var_norms].columns)
features_norm = pd.concat([features[features.columns.difference(features_norm.columns)], features_norm], axis=1)
print('')

# Fit PCA on normalized features
print('Fitting principal components...')
features_pca = pca.transform(features_norm[var_norms])
features = pd.concat([features, pd.DataFrame(features_pca,columns=['Component 1','Component 2','Component 3'])], axis=1)
print(features_pca)
print('')

# Run cluster model on riders dataset
print('Running KMeans model on dataset...')
clusters = kmeans.fit_predict(features_pca)
clusters = pd.DataFrame(clusters,columns=['Cluster'])
features = pd.concat([features, clusters], axis=1)
features['Date'] = today
print(clusters)
print('')

# Calculate silhouette score for model
sil_score = silhouette_score(features_pca, kmeans.fit_predict(features_pca))
print('Silhouette Score: ' + str(sil_score))
print('')

# Set variables for database insert
insert_vars = ['Rider ID','Date','Cluster','Component 1','Component 2','Component 3']

# Run KMeans Cluster Archive procedure
cursor.execute("""EXEC [dbo].[KMeans_Archive];""")
cursor.commit()

# Insert clusters and components into KMeans Cluster table
print('Inserting KMeans data into database...')
print('')
cursor.executemany("""
INSERT INTO [dbo].[KMeans_Clusters] ([Rider ID],[DateFormatted],[Cluster],[Component 1],[Component 2],[Component 3]) VALUES (?,?,?,?,?,?)""", features[insert_vars].values.tolist())
cursor.commit()
sleep(1)

print('All cluster data inserted')
print('')

# Insert Silhouette Score data into table
row = (today, sil_score)
print('Inserting silhouette score into database...')
print('')
cursor.execute("""INSERT INTO [dbo].[KMeans_SilhouetteScores] ([Date],[Silhouette Score]) VALUES (?,?)""", row)
cursor.commit()
sleep(1)

print('Silhouette score inserted')
print('')

# Run KMeans Changes Insert procedure
cursor.execute("""EXEC [dbo].[KMeans_Changes_Insert];""")
cursor.commit()

cursor.close()
conn.close()
