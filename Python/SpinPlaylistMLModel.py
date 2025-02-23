import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import math
import numpy as np
import win32com.client as win32

pd.options.mode.chained_assignment = None  # default='warn'

#### Define function for determining the applicable RPM range for each song (ex. 120 to 130 RPM)
def RPMrange(x):
    if str(int(round(x)))[-1] == '0':
        y = str((math.ceil(x / 10.0)) * 10) + ' to ' + str(((math.ceil(x / 10.0)+1) * 10)-1) + ' RPM'
    else:
        y = str((math.ceil(x / 10.0)-1) * 10) + ' to ' + str(((math.ceil(x / 10.0)) * 10)-1) + ' RPM'
    return y

#### Define function for determining whether or not track duration is 5 minutes or more
def DurCheck(x):
    if x >= 300:
        return 1
    else:
        return 0

#### Read Excel file into DataFrame

#### Insert blank column for RPM range (ex. 120 to 130 rpm)
df["RPM Range"] = ""

#### Insert blank column for over 5 minutes
df["Over 5 Minutes"] = ""

#### Convert Duration column to number of seconds
df['Duration'] = df['Duration'].astype(str).str[:8]
df['Duration'] = pd.to_timedelta(df['Duration']).dt.total_seconds()

#### Fill in new columns with corresponding values
x = 0
while x < df.shape[0]:
    df["RPM Range"][x] = RPMrange(df["Used RPM"][x])
    df["Over 5 Minutes"][x] = DurCheck(df["Duration"][x])
    x = x + 1

#### Select only rows that have a category
rslt_df = df[df['Category'].notnull()]
rslt_df = rslt_df[rslt_df['Category'] != 'reflection']

#### Replace various hill types with blanket "Hill" category
rslt_df.loc[rslt_df['Category'] == 'hill climb', 'Category'] = 'hill'
rslt_df.loc[rslt_df['Category'] == 'hill choreo', 'Category'] = 'hill'
rslt_df.loc[rslt_df['Category'] == 'hill back 4', 'Category'] = 'hill'
rslt_df.loc[rslt_df['Category'] == 'hill heavy', 'Category'] = 'hill'
rslt_df.loc[rslt_df['Category'] == 'hill break away', 'Category'] = 'hill'

#### Winnow down to only the variables we need
rslt_df = rslt_df[['URL','Category','Name','Artist','Used RPM','RPM Range','Over 5 Minutes','Duration']]

#### Create dummy variables for RPM Range column
rslt_df = pd.get_dummies(rslt_df, prefix='RPM Range', columns=['RPM Range'])

#### Convert dummy variables from boolean to binary 1 or 0
rslt_df["RPM Range_90 to 99 RPM"] = rslt_df["RPM Range_90 to 99 RPM"].astype(int)
rslt_df["RPM Range_80 to 89 RPM"] = rslt_df["RPM Range_80 to 89 RPM"].astype(int)
rslt_df["RPM Range_70 to 79 RPM"] = rslt_df["RPM Range_70 to 79 RPM"].astype(int)
rslt_df["RPM Range_60 to 69 RPM"] = rslt_df["RPM Range_60 to 69 RPM"].astype(int)
rslt_df["RPM Range_50 to 59 RPM"] = rslt_df["RPM Range_50 to 59 RPM"].astype(int)
rslt_df["RPM Range_100 to 109 RPM"] = rslt_df["RPM Range_100 to 109 RPM"].astype(int)
rslt_df["RPM Range_110 to 119 RPM"] = rslt_df["RPM Range_110 to 119 RPM"].astype(int)
rslt_df["RPM Range_120 to 129 RPM"] = rslt_df["RPM Range_120 to 129 RPM"].astype(int)
rslt_df["RPM Range_130 to 139 RPM"] = rslt_df["RPM Range_130 to 139 RPM"].astype(int)

#### Normalize data
df_norm = rslt_df[['Used RPM','Duration']]

scaler = MinMaxScaler() 
arr_scaled = scaler.fit_transform(df_norm)

df_norm = pd.DataFrame(arr_scaled, columns=df_norm.columns, index=df_norm.index)

rslt_df[['Used RPM','Duration']] = df_norm[['Used RPM','Duration']]

#### Set target variable, ID column
target_col = rslt_df['Category']

#### Set features
features = rslt_df.drop(['URL','Category','Name','Artist'], axis=1)

#### Split into Train and Test sets
X_train, X_test, y_train, y_test = train_test_split(features, target_col, test_size=0.3, shuffle=True,stratify=target_col)
##print(X_train)
##print(X_test)
##print(y_train)
##print(y_test)

#### Create and train model
model = LogisticRegression()
model.fit(X_train, y_train)

#### Evaluate the trained model on training data
y_pred = model.predict(X_test)
print(y_pred)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))

##print(rslt_df[rslt_df['Category']=='weights'])
##print(model.predict(rslt_df[rslt_df['Category']=='weights'].drop(['ID','Name','Artist','Category','Danceability','Energy'], axis=1)))
##print(garbage)

#### Compute the confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Get list of distinct ride categories
ride_categories = ['hill','jog','jumps','run','sprint','warmup','weight']

#### Plotting the confusion matrix using Matplotlib
fig, ax = plt.subplots(figsize=(8, 8))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
ax.figure.colorbar(im, ax=ax)
ax.set(xticks=np.arange(cm.shape[1]),
       yticks=np.arange(cm.shape[0]),
       xticklabels=ride_categories, yticklabels=ride_categories,
       title='Confusion Matrix',
       ylabel='Predicted Ride Category',
       xlabel='Predicted Ride Category')
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
fmt = 'd'
thresh = cm.max() / 2.
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, format(cm[i, j], fmt),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black")
fig.tight_layout()
#saving figure
plt.savefig('C:\\Users\\andre\\OneDrive\\Documents\\Spinning\\ConfusionMatrix.png')

################################# Run model on new spreadsheet, input predicted ride category field values #################################################

#### Insert blank column for RPM range (ex. 120 to 130 rpm)
df2["RPM Range"] = ""

#### Insert blank column for over 5 minutes
df2["Over 5 Minutes"] = ""

#### Convert Duration column to number of seconds
df2['Duration'] = df2['Duration'].astype(str).str[:8]
df2['Duration'] = pd.to_timedelta(df2['Duration']).dt.total_seconds()

#### Fill in new columns with corresponding values
x = 0
while x < df2.shape[0]:
    df2["RPM Range"][x] = RPMrange(df["Used RPM"][x])
    df2["Over 5 Minutes"][x] = DurCheck(df2["Duration"][x])
    x = x + 1

#### Select only rows that have a category
rslt_df2 = df2[df2['Category'] != 'reflection']
rslt_df2 = rslt_df2[rslt_df2['Category'] != 'crunches']

#### Replace various hill types with blanket "Hill" category
rslt_df2.loc[rslt_df2['Category'] == 'hill climb', 'Category'] = 'hill'
rslt_df2.loc[rslt_df2['Category'] == 'hill choreo', 'Category'] = 'hill'
rslt_df2.loc[rslt_df2['Category'] == 'hill back 4', 'Category'] = 'hill'
rslt_df2.loc[rslt_df2['Category'] == 'hill heavy', 'Category'] = 'hill'
rslt_df2.loc[rslt_df2['Category'] == 'hill break away', 'Category'] = 'hill'

#### Winnow down to only the variables we need
rslt_df2 = rslt_df2[['URL','Category','Name','Artist','Used RPM','RPM Range','Over 5 Minutes','Duration']]

#### Create dummy variables for RPM Range column
rslt_df2 = pd.get_dummies(rslt_df2, prefix='RPM Range', columns=['RPM Range'])

#### Convert dummy variables from boolean to binary 1 or 0
rslt_df2["RPM Range_90 to 99 RPM"] = rslt_df2["RPM Range_90 to 99 RPM"].astype(int)
rslt_df2["RPM Range_80 to 89 RPM"] = rslt_df2["RPM Range_80 to 89 RPM"].astype(int)
rslt_df2["RPM Range_70 to 79 RPM"] = rslt_df2["RPM Range_70 to 79 RPM"].astype(int)
rslt_df2["RPM Range_60 to 69 RPM"] = rslt_df2["RPM Range_60 to 69 RPM"].astype(int)
rslt_df2["RPM Range_50 to 59 RPM"] = rslt_df2["RPM Range_50 to 59 RPM"].astype(int)
rslt_df2["RPM Range_100 to 109 RPM"] = rslt_df2["RPM Range_100 to 109 RPM"].astype(int)
rslt_df2["RPM Range_110 to 119 RPM"] = rslt_df2["RPM Range_110 to 119 RPM"].astype(int)
rslt_df2["RPM Range_120 to 129 RPM"] = rslt_df2["RPM Range_120 to 129 RPM"].astype(int)
rslt_df2["RPM Range_130 to 139 RPM"] = rslt_df2["RPM Range_130 to 139 RPM"].astype(int)

#### Normalize data
df2_norm = rslt_df2[['Used RPM','Duration']]

arr_scaled2 = scaler.fit_transform(df2_norm)

df2_norm = pd.DataFrame(arr_scaled2, columns=df2_norm.columns, index=df2_norm.index)

rslt_df2[['Used RPM','Duration']] = df2_norm[['Used RPM','Duration']]

### Open up new spreadsheet
##excel = win32.gencache.EnsureDispatch('Excel.Application')
##excel.Visible = False
##ws = wb.ActiveSheet

#### Run model on new dataset 
new_cat = model.predict(rslt_df2.drop(['URL','Name','Artist','Category'], axis=1))

x = 0

#### Iterate through predictions
for cat in new_cat:
    try:
        print(rslt_df2['Name'][x] + ' - ' + rslt_df2['Artist'][x] + ': ' + cat)
        x = x + 1
    except KeyError:
        try:
            x = x + 1
            print(rslt_df2['Name'][x] + ' - ' + rslt_df2['Artist'][x] + ': ' + cat)
            x = x + 1
        except KeyError:
            x = x + 1
            print(rslt_df2['Name'][x] + ' - ' + rslt_df2['Artist'][x] + ': ' + cat)
            x = x + 1

