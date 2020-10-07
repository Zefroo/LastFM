# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 21:56:35 2020

@author: -
"""
from pandas import DataFrame
import pandas as pd


def topNArtists(n, last_fm_df):
    """
    Parameters
    ----------
    n : int
        The number of top artists to print
    last_fm_df : DataFrame
        The DataFrame of last_fm information

    Returns
    -------
    top_n_artists : DataFrame
        DataFrame with n artists who have the highest play counts
    """
    print('1. Who are the top artists?')
    # group by name and artistID to get weight sums
    group_by_weight = last_fm_df.groupby(['name', 'artistID']).sum()
    # get nlargest as output (n can be set to 10)
    top_n_artists = group_by_weight.nlargest(n,'weight')
    return top_n_artists


def mostListened(n, last_fm_df):
    """
    Parameters
    ----------
    n : int
        The number of top artists to print
    last_fm_df : DataFrame
        The DataFrame of last_fm information

    Returns
    -------
    most_listened : DataFrame
        DataFrame with n artists with the most unique listeners
    """
    print('2. What artists have the most listeners?')
    # put users in a column to group it
    reindexed = last_fm_df.reset_index(level='userID')
    # group by artistID/name and get unique userID's
    unique_users = DataFrame(reindexed.groupby(["name","artistID"])
                             ["userID"].nunique())
    # get top n results
    most_listened = unique_users.nlargest(n, columns="userID")
    return most_listened


def topUsers(n, user_artists_df):
    """
    Parameters
    ----------
    n : int
        The number of top users to print
    user_artists_df : DataFrame
        The DataFrame of user and artist information

    Returns
    -------
    top_users: DataFrame
        DataFrame with n users with the highest play counts
    """   
    print('3. Who are the top users?')
    # group by user ID and sum by weight
    group_by_user = DataFrame(user_artists_df.groupby("userID")
                              ["weight"].sum())
    # get top 10 users
    top_users = group_by_user.nlargest(n, columns="weight")
    return top_users

        
def highestAverage(n, last_fm_df):
    """
    Parameters
    ----------
    n : int
        The number of top artists to print
    last_fm_df : DataFrame
        The DataFrame of last_fm information

    Returns
    -------
    top_average : DataFrame
        DataFrame with n artists with the highest average play counts
    """ 
    print('4. What artists have the top mean number of plays per listener?')
    # first get the total number of users per artist
    user_per_artist = DataFrame(last_fm_df.groupby(["name", "artistID"])
            ["weight"].count())
    # get the total number of listens per artist
    total_listens = last_fm_df.groupby(['name', 'artistID']).sum()
    # divide the two dataframes to get the average
    average_listens = total_listens.floordiv(user_per_artist,
            axis='weight').rename(columns={'weight':'Average'})
    # add the total weight column back 
    average_listens.insert(1,"Weight", total_listens['weight'])
    # get top n results
    top_average = average_listens.nlargest(n, columns="Average")
    return top_average
        

def highFixedAverage(n, last_fm_df):
    """
    Parameters
    ----------
    n : int
        The number of top artists to print
    last_fm_df : DataFrame
        The DataFrame of last_fm information

    Returns
    -------
    top_avg_fixed : DataFrame
        DataFrame with n artists with 50 or more listeners the highest average
        play counts
    """ 
    print('5.What artists with at least 50 listeners have the highest' + 
          ' average number of plays per listener?')
    # Call MostListened on 50 
    top_50 = mostListened(50, last_fm_df).rename(columns=
            {'userID':'userCount'})
    # Get the playcounts for all artists
    get_playcount = last_fm_df.groupby(['name', 'artistID']).sum()
    # merge top 50 with their playcounts
    top_50_avg = pd.merge(top_50, get_playcount, left_index=True, 
            right_index=True).rename(columns={'weight':'playCount'})
    # get the average by adding a column that is playCount / userCount
    top_50_avg['Average'] = top_50_avg.apply(lambda row: 
            int(round(row.playCount / row.userCount)), axis=1)
    # get the top 10 from top_50_avg
    top_avg_fixed = top_50_avg.nlargest(n, columns="Average")
    return top_avg_fixed
    

def friendSongCounts(n, last_fm_df):
    """
    Parameters
    ----------
    n : int
        The number of top users to print
    last_fm_df : DataFrame
        The DataFrame of last_fm information

    Returns
    -------
    five_plus_avg : int
        The sum of play counts for all users with 5+ friends
    under_five_avg : int
        The average of play counts for all users with under 5 friends

    """
    # get user_friends df
    user_friends_df = pd.read_table('user_friends.dat', encoding="utf-8", 
            sep="\t", index_col='userID')
    # merge with rest of last_fm dataframe
    friends_fm = pd.merge(user_friends_df, last_fm_df, left_on="userID", 
            right_on="userID").reset_index()
    # group by userID and get counts of friendID's
    friends_count = DataFrame(friends_fm.groupby(["userID"]).agg({"friendID": 
            "nunique", "weight": "sum"})).rename(columns=
            {'friendID':'friends', 'weight':'plays'})
    # filter to get rows where friends >= 5 
    over_five = friends_count['friends'] >= 5
    under_five = friends_count['friends'] < 5 
    # get averages
    five_plus_avg = int(round(friends_count[over_five]["plays"].mean()))
    under_five_avg = int(round(friends_count[under_five]["plays"].mean()))
    return (five_plus_avg, under_five_avg)


def artist_sim(aid1, aid2, artists_df):
    """
    Parameters
    ----------
    aid1 : int
        The firts artistID to compare similarity with
    aid2 : int
        The second artistID to compare similarity with
    artists_df : DataFrame
        The DataFrame of artist information

    Returns
    ------
    None
   
    Prints 
    ------
    artist names, artistID's and the jaccard index
    """
    print('\n', '!' * 40, '\n')
    a1_name = artists_df.loc[aid1, 'name']
    a2_name = artists_df.loc[aid2, 'name']
    print("7. How similar are the artists " + a1_name +  
          " and " + a2_name + "?")
    # get artist tag data
    tagged_artist_df = pd.read_table('user_taggedartists.dat', encoding="utf-8", 
            sep="\t", index_col='artistID')
    # filter userID's for artist 1 and artist 2 
    artist1_df = tagged_artist_df.loc[aid1] 
    artist2_df = tagged_artist_df.loc[aid2] 
    # make sets out of all userID's 
    user_set_a1 = set(artist1_df['userID'])
    user_set_a2 = set(artist2_df['userID'])
    # get union and intersection to calculate Jaccard Similarity
    intersection = user_set_a1.intersection(user_set_a2)
    union = user_set_a1.union(user_set_a2)
    # get the jaccard index
    jaccard_index =len(intersection)/len(union)
    # print out the artist names and jaccard index
    print(a1_name + "(" + str(aid1) + ")", "and", a2_name + "(" + str(aid2) 
          + ")", "have a Jaccard Index of:", jaccard_index)
    
    


def main():
    """
    Main function to print results of query functions on last_fm_df
    
    Prints results based on data provided in the returned DataFrame or object,
    in the general in the indexed order the data is presented:
        <index[0]>. . .<index[n]> <column[0]> . . .<column[n]>
    """
    # create dataframes
    artists_df = pd.read_table('artists.dat', encoding="utf-8",sep="\t", 
        index_col='id')
    user_artists_df = pd.read_table('user_artists.dat',encoding="utf-8", 
        sep="\t", index_col=['userID', 'artistID'])
    # merge the two df's
    last_fm_df = pd.merge(artists_df, user_artists_df, left_index=True, 
                  right_on="artistID")
    #----START RUNNING FUNCTIONS----#
    print('\n', '!' * 40, '\n')
    # print top 10 artists
    for index, row in topNArtists(10, last_fm_df).iterrows():
        print(index[0] + '(' + str(index[1]) + ')' + ' ' + str(row['weight']))
    print('\n', '!' * 40, '\n')
    # print top 10 most listened artists
    for index, row in     mostListened(10, last_fm_df).iterrows():
        print(index[0] + '(' + str(index[1]) + ')' + ' ' + str(row['userID']))
    print('\n', '!' * 40, '\n')
    # print top 10 users who listen the most
    for index, row in topUsers(10, user_artists_df).iterrows():
        print(str(index) + ' ' + str(row['weight']))
    print('\n', '!' * 40, '\n')
    # print 10 artists with highest average listeners
    for index, row in highestAverage(10, last_fm_df).iterrows():
        print(index[0] + '(' + str(index[1]) + ')' + ' ' 
              + str(row['Weight']) + ' ' + str(row['Average']))
    print('\n', '!' * 40, '\n')
    # print 10 artists with 50+ listeners that have highest avg listeners
    for index, row in highFixedAverage(10, last_fm_df).iterrows():
        print(index[0] + '(' + str(index[1]) + ')' + ' ' + 
              str(row['playCount']) + ' ' + str(row['userCount']) 
              + ' ' +str(row['Average']))
    print('\n', '!' * 40, '\n')
    print('6. Do users with five or more friends listen to more songs?')
    print("Five or more friends:", friendSongCounts(10, last_fm_df)[0],
          "\nLess than 5 friends:", friendSongCounts(10, last_fm_df)[1])
    # get Jaccard Index of various artist ID's 
    artist_sim(735, 562, artists_df)
    artist_sim(735, 89, artists_df)
    artist_sim(735, 289, artists_df)
    artist_sim(89, 289, artists_df)
    artist_sim(89, 67, artists_df)
    artist_sim(67, 735, artists_df)


if __name__ == "__main__":
    main()