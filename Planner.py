import pandas as pd
import numpy as np
from datetime import datetime

# Input Files
data_v2 = pd.read_csv('data_v2.csv', encoding="latin1")
congress = pd.read_csv('Congress.csv', encoding="latin1")
map = pd.read_csv('Map.csv', encoding="latin1")
asco = pd.read_csv('asco.csv', encoding="latin1")
asco_disease = pd.read_csv('asco_disease.csv', encoding="latin1")
matrix = pd.read_csv('matrix.csv', encoding="latin1")
sort = pd.read_csv('sort.csv', encoding="latin1")
input_disease = pd.read_csv('disease.csv', encoding="latin1")

# Provide Input
Input = "Relapsed Multiple Myeloma"


def change_to_datetime(row):
    return pd.to_datetime(row, dayfirst=True)


def format_date(row):
    return row.apply(lambda x: '{:%B %d, %Y}'.format(x))


# CongressList
TA = pd.DataFrame(data_v2['TA'][data_v2['Indication'] == Input].unique(), columns={'TA'})
TA['n'] = 1
DiseaseList = pd.DataFrame(map['Indication'][map['Key'] == Input])
DiseaseList['k'] = 1
congress = congress.merge(TA, on='TA', how='left')
congress = congress[congress['n'] == 1]
congress = congress.merge(DiseaseList, on='Indication', how='left')
# Filter only  USEU congresses and do not filter congresses that have indication (non - empty) and whose k value is null
congress = congress[(congress['USEU'] == 1) & ~((congress['k'].isnull()) & ~(congress['Indication'].isnull()))]
congress = congress.sort_values(['Top', 'Indication', 'GoogleHits'], ascending=[False, True, True]).drop_duplicates()
congress = congress[['Congress', 'Country', 'City', 'StartDate', 'EndDate', 'Cost']]
congress['StartDate'] = change_to_datetime(congress['StartDate'])
congress['EndDate'] = change_to_datetime(congress['EndDate'])
congress['Cost'] = congress['Cost'].apply(lambda x: "${:.2f}".format(float(x)) if len(x) > 1 else x)
congress.rename(columns={"StartDate": "Start Date", "EndDate": "End Date", "Cost": "Cost (USD)"}, inplace=True)
CongressList = pd.DataFrame(congress.head(15).sort_values(by='Start Date'))
CongressList['Start Date'] = format_date(CongressList['Start Date'])
CongressList['End Date'] = format_date(CongressList['End Date'])

CongressList.to_csv(r'CongressList.csv', index=False)

# Keywords
Keywords = pd.DataFrame(map['Indication'][map['Key'] == Input])
Keywords['n'] = 1
Keywords = data_v2.merge(Keywords, on='Indication', how='left')
Keywords = Keywords[Keywords['n'] == 1]
Keywords = Keywords[['id', 'Generic', 'Brand', 'Firm', 'Indication', 'TA']]

Keywords.to_csv(r'KeywordsList.csv', index=False)

# Planner
Planner = pd.DataFrame(asco.merge(asco_disease, how='left'))
Planner['Relevance'] = Planner['Indication'].apply(lambda x: 1 if x == Input.lower() else 0)
Planner.sort_values(by='Relevance', ascending=False, inplace=True)
Planner.drop_duplicates(subset='id', keep='first', inplace=True)
# Planner.to_csv(r'InterimPlanner.csv', index=False)
Planner = Planner[Planner.columns.difference(['Indication'])]
Planner = Planner.merge(matrix, how='left')
# Planner.to_csv(r'InterimPlanner2.csv', index=False)
Planner['Priority'] = np.where(Planner['Relevance'] == 1, Planner.Priority, 'Not Relevant')
Planner['Date'] = change_to_datetime(Planner['Date'])
Planner = Planner[['Abstract_Title', 'Session_Title', 'Date', 'Relevance', 'Priority']].sort_values(
    ['Priority', 'Date'])
Planner['Date'] = format_date(Planner['Date'])
Planner.to_csv(r'PlannerList.csv', index=False)

# SummaryPlanner
SummaryPlanner = Planner.groupby(['Priority']).size().reset_index(name='Count')
SummaryPlanner = SummaryPlanner.merge(sort, how='left')
SummaryPlanner.sort_values(by='Sort', inplace=True)
SummaryPlanner = SummaryPlanner[SummaryPlanner.columns.difference(['Sort'])]
SummaryPlanner = SummaryPlanner.reindex(columns=['Priority', 'Count'])

SummaryPlanner.to_csv(r'SummaryPlannerList.csv', index=False)
