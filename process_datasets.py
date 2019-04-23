# Author: samueljklee
# Extract data from Yummly28K

import argparse
import numpy
import json
import math
import os
import re
import uuid
import random
import nltk
nltk.download('punkt')
from nltk import word_tokenize 
from nltk.corpus import stopwords
from nltk.util import ngrams

EXTRACT_DATA = "data/recipe_raw.tsv"
MODELS = "models/"
NAMES_COUNTER_NPY = "names_counter.npy"
UUID_DISH_NPY = "uuid_dish.npy"

blacklist = {'with','and','&','-','in'}

"""
uuid
NAME
INGREDIENTS
RATING
TIME
FLAVORS
ATTRIBUTES
NUTRITION
IMAGES
"""
def analyze_model():
    counter = 0

    name_freq_dict = dict()
    name_dish_dict = dict()
    uuid_dish = []

    with open(EXTRACT_DATA, 'r') as fpr:
        for row in fpr:
            split_ = row.split('\t')
            uuid = split_[0]
            dish_name = split_[2]
            ingredients = split_[3]
            rating = split_[4]
            time = split_[5]
            flavors = split_[6]
            nutrition = split_[7]
            images = split_[8]
            uuid_dish.append((uuid, dish_name, ingredients, rating, time, flavors, nutrition, images))

            # name
            name_ = re.sub(r'[\{\}\(\)\[\]-_,\'\"\.”“‘’–]', '', dish_name)
            name = re.split(r'[ -]', name_)
            counter += 1
            for n_ in name:
                n = n_.lower()
                if n in blacklist: continue
                if n not in name_freq_dict: name_freq_dict[n] = 0
                if n not in name_dish_dict: name_dish_dict[n] = set()
                name_freq_dict[n] += 1
                name_dish_dict[n].add(uuid)

    fpr.close()

    names_counter = [ (k, math.log(v/counter), name_dish_dict[k]) for k, v in name_freq_dict.items() ]
    names_counter.sort(key=lambda x: x[1], reverse=True)
    numpy.save(MODELS+NAMES_COUNTER_NPY, names_counter)
    numpy.save(MODELS+UUID_DISH_NPY, uuid_dish)

def read_model():
    names_model = numpy.load(MODELS+NAMES_COUNTER_NPY)
    uuid_dish_model = numpy.load(MODELS+UUID_DISH_NPY)
    name_obj = dict()
    uuid_dish = dict()
    bigram_dish = dict()

    for uuid_to_dish in uuid_dish_model:
        uuid = uuid_to_dish[0]
        if uuid not in uuid_dish: 
            uuid_dish[uuid] = {
                    "name" : uuid_to_dish[1],
                    "ingredients" : uuid_to_dish[2],
                    "rating" : uuid_to_dish[3],
                    "time" : uuid_to_dish[4],
                    "flavors" : uuid_to_dish[5],
                    "nutrition" : uuid_to_dish[6],
                    "images" : uuid_to_dish[7]
                }

        token = nltk.word_tokenize(uuid_dish[uuid]["name"].lower())
        bigram = list(ngrams(token, 2)) 
        for bg in bigram:
            if bg not in bigram_dish: bigram_dish[bg] = []
            bigram_dish[bg].append(uuid)

    for name_freq_map in names_model:
        name = name_freq_map[0]
        likelihood = name_freq_map[1]
        mapping = name_freq_map[2]

        if name not in name_obj: 
            name_obj[name] = {'score': likelihood, 'dishes': mapping}
        else:
            raise ValueError("Same value in names to likelihood model")

    return name_obj, uuid_dish, bigram_dish

def predict(string, name_obj, uuid_dish, bigram_dish):
    
    search_dish = string.lower()
    tokenized_search_dish = search_dish.split()
    all_dishes = []
    dish_count = dict()

    token = nltk.word_tokenize(search_dish)
    bigram = list(ngrams(token, 2)) 

    found_dishes = list()

    for bg in bigram:
        if len(set(bg) - blacklist) != len(bg): 
            bigram_index += 1
            continue

        if bg in bigram_dish:
            for dish_uuid in bigram_dish[bg]:
                ingredients = re.split(r'\', \'' , re.sub(r'(\[\'|\'\])', '', uuid_dish[dish_uuid]["ingredients"]) )
                found_dishes.append({"name": uuid_dish[dish_uuid]["name"], "ingredients": ingredients})

    for word in tokenized_search_dish:
        if word in name_obj:
            print("Word: {} Score: {}".format(word, name_obj[word]['score']))
            all_dishes.append((name_obj[word]['score'],name_obj[word]['dishes']))

            for dish in name_obj[word]['dishes']:
                if dish not in dish_count: dish_count[dish] = 0
                dish_count[dish] += 1
        else:
            print("{} doesn't exist".format(word))
        
    all_dishes.sort(key=lambda x: x[0], reverse=True)

    print("Number of possible dishes: {}".format(len(dish_count)))
    
    dish_score = []
    for id in dish_count.keys():
        dish_score.append((uuid_dish[id], edit_distance(search_dish,uuid_dish[id]["name"])))

    if len(dish_score) == 0:
        raise ValueError("No dishes found")

    dish_score.sort(key=lambda x:x[1])

    for dish_data, ed_score in dish_score[:3]:
        name = dish_data["name"]
        ingredients = re.split(r'\', \'' , re.sub(r'(\[\'|\'\])', '', dish_data["ingredients"]) )
        #images = json.loads(dish_data['images'])
        found_dishes.append({"name": name, "ingredients": ingredients})

    print("Finding: ", string)

    #print(found_dishes)
    chosen_dish = random.choice(found_dishes)

    return {
        'name': chosen_dish["name"],
        'ingredients': chosen_dish["ingredients"]
    }
    

# https://stackoverflow.com/questions/2460177/edit-distance-in-python
def edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Cari Makan Ni")
    parser.add_argument("-a", action="store_true")
    return parser.parse_args()

# Global
args = parse_arguments()
if args.a:
    analyze_model()
else:
    print("Skipping reanalyzing model...")

name_obj, uuid_dish, bigram_dish = read_model()
print(predict("rosemary deep fried porkchops", name_obj, uuid_dish, bigram_dish))