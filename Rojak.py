import numpy as np 
import pandas as pd
import os
import random
import logging
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer

DATASET = 'data/kaggle_epi_dataset.csv'
stopwords_en =  set(stopwords.words('english'))
CHOOSE_N_DISHES = 10

class Rojak(object):
    sentimentAnalyzer = SentimentIntensityAnalyzer()
    
    def __init__(self):
        # Dataset source: https://www.kaggle.com/hugodarwood/epirecipes#epi_r.csv
        self.df = pd.read_csv(DATASET) 
        self.map_dish = {}
        self.dishes = {}
        self.dish_rating = {
            1:set(), 2:set(), 3:set()
        }

        self.dish_calories = {
            'low': set(), 'mid': set(), 'high': set()
        }
        
        print("Total features count: %d" % len(self.df.keys()))
        self.data_cleaning()
        self.data_reading()
        
    
    def data_cleaning(self):
        # drop duplicated titles
        self.df = self.df.drop_duplicates(['title'])

        # fill in NaN with 0
        self.df = self.df.fillna(0)

        # drop features that isn't proper (not alphanumeric)
        self.df = self.df.drop([x for x in self.df.columns if not x.isalpha()],axis=1)

        # cleaning title: strip
        #TODO : can clean further
        self.df['title'] = self.df['title'].apply(lambda x: x.strip())
        print("Processed features count: %d" % len(self.df.keys()))

    def data_reading(self):
        """
        map_dish      : map index to dish
        dishes        : dish to ingredients
        dish_rating   : rating to dish
        dish_calories : calories to dish
        """
        for i, row in self.df.iterrows():
            title = row.title
            rate = row.rating
            calorie = row.calories
            self.map_dish[i] = title
            self.dishes[title] = {k : v for k,v in row.items() if v != 0 or isinstance(v, str)}

            if rate <= 1.5:
                self.dish_rating[1].add(i)
            if rate <= 4:
                self.dish_rating[2].add(i)
            else:
                self.dish_rating[3].add(i)

            if calorie <= 300:
                self.dish_calories['low'].add(i)
            if calorie <= 700:
                self.dish_calories['mid'].add(i)
            else:
                self.dish_calories['high'].add(i)

        print("Processed %d dishes" % len(self.map_dish))
        for x in self.dish_rating.keys():
            print('Rating %d has %d dishes' % (x, len(self.dish_rating[x])))

        for x in self.dish_calories.keys():
            print('Calories %s has %d dishes' % (x, len(self.dish_calories[x])))
    
    def find_best_pair(self, list_of_list, index):
        if index >= len(list_of_list):
            return 0, set()

        score1, set1 = self.find_best_pair(list_of_list, index+1)
        score1 += len(list_of_list[index])
        score2, set2 = self.find_best_pair(list_of_list, index+1)

        if score1 == 0:
            return score2, set(list_of_list[index])
        if score2 == 0:
            return score1, set(list_of_list[index])

        if score1 < score2:
            return score1, set1&set2
        return score2, set1&set2

    def search(self, string):
        input_kw = set(string.split(' '))
        input_kw -= (input_kw & stopwords_en)
        dataset_kw = set(self.df.keys()[1:])

        # what if there's no intersection?
        intersection_keywords = input_kw & dataset_kw
        potential_dishes_index = set()
        dishes_index_every_key_list = []

        # list of [list of dishes indexes per key]
        for key in intersection_keywords:
            dishes_index_every_key_list.append(self.df.index[self.df[key] != 0].tolist())

        print("Initial dishes per key list: %d" % len(dishes_index_every_key_list))

        if dishes_index_every_key_list:
            shortlisted = self.find_best_pair(dishes_index_every_key_list, 0)
            print("Shortlisted count: %d" % shortlisted[0])
            
            highest_match_score = -1
            top_two_highest_score = [[], []]
            hs_counter = 0
            for i in shortlisted[1]:
                title = set(self.dishes[self.map_dish[i]]['title'].lower().split())
                naming_score = len(input_kw & title)

                if naming_score > highest_match_score:
                    if highest_match_score > 0:
                        hs_counter += 1
                        if len(top_two_highest_score[hs_counter%2]) > 1:
                            top_two_highest_score[hs_counter%2] = []
                            
                    highest_match_score = naming_score
                    top_two_highest_score[hs_counter%2] = []

                if naming_score >= highest_match_score:
                    top_two_highest_score[hs_counter%2].append(self.dishes[self.map_dish[i]])
            
            top1_list = top_two_highest_score[hs_counter%2]
            top2_list = top_two_highest_score[(hs_counter+1)%2] if len(top_two_highest_score[(hs_counter+1)%2]) > 0 else []
            both_list = top1_list + top2_list
            #TODO: include probability?
            number_of_item_to_choose = min(CHOOSE_N_DISHES, len(both_list))
            chosen_dishes = np.random.choice(both_list, number_of_item_to_choose, replace=False)

        else:
            print("X Initial keywords index list is empty. \n... Fallback to sentiment anaylsis.")
            # use sentiment analysis as a fallback mechanism
            # in case input string doesn't contain any information about foods
            sentimentScore = sentimentAnalyzer.polarity_scores(string)

            if sentimentScore['pos'] >= sentimentScore['neg']:
                dishes_index_list = list(dish_rating[3])
            elif sentimentScore['neu'] > sentimentScore['neg']:
                dishes_index_list = list(dish_rating[2])
            else:
                dishes_index_list = list(dish_rating[1])

            print("Sentiment analysis technique dishes count: %d" % len(dishes_index_list))
            # randomly choose top 10 dishes for now
            random_pick_dishes_index = np.random.choice(dishes_index_list, min(CHOOSE_N_DISHES, len(highest_match_dishes)), replace=False)
            chosen_dishes =  [dishes[self.map_dish[i]] for i in random_pick_dishes_index]


        chosen_dishes = sorted(chosen_dishes, key=lambda x: x['rating'], reverse=True)
        print(len(chosen_dishes))
        return chosen_dishes

