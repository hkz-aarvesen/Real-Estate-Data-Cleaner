"""This script takes in real estate data and cleans it up for regression analysis

Todo:
    *Build a column with the S&P/Case-Shiller National Home Price Index value
    *Build a column with inflation adjustment for ClosingPrice
"""

import pandas as pd
import numpy as np

input_file = 'Real Estate Model - Candler Park.csv'
output_file = 'cleaned_data_cp5.csv'
#lists of keywords to make dummy vars of if they are present in an observation's description  
Exterior_features = ['Porch','Patio','Deck','Fenced','Out-Building']
BasementDesc_features = ['Crawl Space','Slab', 'Basement']
ParkingDesc_features = ['Driveway','Carport', '1 Car Garage', '2 Car Garage', '3 Car Garage']
Stories_features = ['1 Story', '2 Story', 'More']

def make_YearBuilt_bins(df, size):
	'''Divides YearBuilt into bins and creates new column named YearBuiltBins

    Args:
        df (pandas DataFrame): The DataFrame to make bins on 
        size (int): The size of each bin

    Returns:
        pandas DataFrame: with an additional column named YearBuiltBins
    '''

	bin_cutoffs = df['YearBuilt'].min()
	bins = []
	while bin_cutoffs < df['YearBuilt'].max()+size:
	    bins.append(bin_cutoffs)
	    bin_cutoffs += size
	df['YearBuiltBins'] = pd.cut(df['YearBuilt'], bins)
	return df

def concatenate_address(df):
	'''Takes all pieces of address and concatenates them into a unique key column named Address

    Args:
        df (pandas DataFrame): The DataFrame to concatenate address on 

    Returns:
        pandas DataFrame: with an additional column named Address
    '''
	
	df['Address'] = df[['StreetNumber', 'StreetName', 'City', 'CountyOrParish', 
                    'StateOrProvince', 'PostalCode']].apply(lambda x: ' '.join(x.map(str)), axis=1)
	return df

def Basement_cleanup(x):
    #Recodes BasementDesc into three categories mapped onto a DataFrame	

    x = str(x)
    if 'Crawl Space' in x: 
        return 'Crawl Space'
    elif 'Slab' in x: 
        return 'Slab'
    else:
        return 'Basement'
    
def Stories_cleanup(x):
    #Recodes Stories into three categories mapped onto a DataFrame
    
    x = str(x)
    if '+' in x: 
        return 'More'
    elif '1 Story' in x: 
        return '1 Story'
    else:
        return '2 Story'

def extract_dummies(df, features, col):
    '''Takes a list and makes a column for each phrase in that list
    it places a 1 in that column if that phrase is present in the description else it places a 0 

    Args:
        df (pandas DataFrame): The DataFrame containing the descriptions
        features (list): The list of phrases that are being looked for in descriptions
        col (str): name of column which contains the descriptions  

    Returns:
        pandas DataFrame: without the column which contains descriptions plus 
        additional columns one for each word in features 
        
    '''
    
    for feature in features:
        df[feature] = np.where((df[col].str.contains(feature)),1,0)
    df.drop([col], axis=1, inplace=True)
    return df

def main():
	df = pd.read_csv(input_file)
	df.drop(df[df.SqFtTotal == 0].index, inplace=True)
	df['CloseDate']  = pd.to_datetime(df['CloseDate'])
	df = concatenate_address(df)
	df = extract_dummies(df, Exterior_features, col='Exterior')
	df['BasementDesc'] = df['BasementDesc'].apply(Basement_cleanup)
	df = extract_dummies(df, BasementDesc_features, col='BasementDesc')
	df = extract_dummies(df, ParkingDesc_features, col='ParkingDesc')
	df['Stories'] = df['Stories'].apply(Stories_cleanup) 
	df = extract_dummies(df, Stories_features, col='Stories')
	df = make_YearBuilt_bins(df, size=10)
	df['Year'] = pd.DatetimeIndex(df['CloseDate']).year
	df['Age'] = df['Year'] - df['YearBuilt']
	df['AssociationFee'] = np.where((df['AssociationFee']> 0),1,0)
	df['PoolonProperty'] = np.where((df['PoolonProperty'] !=  'None'),1,0)
	df['Bedrooms'] = df['UpperBedrooms'] + df['MainBedrooms']
	df['FullBaths'] = df['UpperFullBaths'] + df['MainFullBaths']
	df['HalfBaths'] = df['UpperHalfBaths'] + df['MainHalfBaths']
	df.drop(['StreetNumber', 'StreetName', 'City', 'CountyOrParish', 'StateOrProvince', 
			 'PostalCode','UpperBedrooms', 'MainBedrooms', 'UpperFullBaths', 'MainFullBaths', 
			 'UpperHalfBaths', 'MainHalfBaths'], axis=1, inplace=True)
	df.to_csv(output_file)

if __name__ == '__main__':
	main()

