#!/usr/bin/env python
# coding: utf-8

import numpy as np 
import pandas as pd 
import os
import sys
import random
import logging
import nltk
import json
import heapq
import string
from collections import defaultdict
from typing import List, Dict, Set, Tuple

from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
from nltk.stem import PorterStemmer 
from nltk.tokenize import word_tokenize 

RETURN_NUM_RESULTS = 10
STOPWORDS_EN =  set(stopwords.words('english'))
DATASET_FOLDER_PATH = './data'
DATASET_FILE_EXT = ".json"
CUSTOM_BLACKLIST = set(['ADVERTISEMENT'])
BLACKLIST_WORDS = CUSTOM_BLACKLIST.union(STOPWORDS_EN)
CACHE_STEMMED_WORDS = {}

class RecipeNode:
    def __init__(self, title="", ingredients=[], instructions="", tags=set()):
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.tags = tags

class KnowledgeGraph():
    def __init__(self):
        dataset_files = get_datasets_file_path()
        list_of_json_dish = read_dataset_to_json(dataset_files)
        df = create_dataframe(list_of_json_dish)
        self.KG = create_knowledge_graph(df)

    def __clean_query_to_list(self, query: str) -> List[str]:
        s1 = filter_BLACKLIST_WORDS_and_nonalpha_in_list(query.split())
        s2 = word_stemming(s1)
        return s2

    def __get_recipes(self, keywords: List[str]) -> List[str]:
        scores = defaultdict(int)
        for kw in keywords:
            if kw not in self.KG:
                continue
            candidates = self.KG[kw]
            for candidate in candidates:
                scores[candidate] += 1
        
        if not scores:
            logging.warning("No matching keywords in knowledge graph. Keywords: {}".format(keywords))
            top_results = []
            return top_results

        # heapq uses min-heap, invert scores
        ranking = [(-score, id(node), node) for node,score in scores.items()]
        top_results = heapq.nsmallest(RETURN_NUM_RESULTS, ranking)
        logging.debug("Top {} results: {}".format(RETURN_NUM_RESULTS, top_results))
        return top_results

    def __convert_object_to_json(self, top_x_results: List[Tuple[int, int, RecipeNode]]) -> List[Dict[str, str]]:
        res = []
        for _, _, node in top_x_results:
            res.append({
                "title": node.title,
                "ingredients": node.ingredients,
                "instructions": node.instructions.split('\n')
            })
        return res

    def search(self, query: str):
        keywords = self.__clean_query_to_list(query)
        top_x_results = self.__get_recipes(keywords)
        return self.__convert_object_to_json(top_x_results)

def get_datasets_file_path() -> List[str]:
    logging.debug("Retrieving datasets...")
    dataset_files = [ os.path.join(DATASET_FOLDER_PATH, f) for f in os.listdir(DATASET_FOLDER_PATH) if f.endswith(DATASET_FILE_EXT) ]
    logging.debug("Found datasets: {}".format(dataset_files))
    return dataset_files

def read_dataset_to_json(dataset_files: List[str]) -> List[Dict[str, str]]:
    # aggregate all datasets
    raw_json = {}
    for fp in dataset_files:
        with open(fp, 'r') as fh:
            raw_json.update(json.load(fh))

    # convert each dish to array
    list_of_json_dish = []
    for k, v in raw_json.items():
        list_of_json_dish.append(v)
    return list_of_json_dish

def filter_BLACKLIST_WORDS_and_nonalpha_in_list(l: List[str]) -> List[str]:
    return [w for w in l if w.isalpha() and w.lower() not in BLACKLIST_WORDS]

def word_stemming(l: List[str]) -> List[str]:
    res = []
    for w in l:
        if w not in CACHE_STEMMED_WORDS:
            CACHE_STEMMED_WORDS[w] = PorterStemmer().stem(w)
        res.append(CACHE_STEMMED_WORDS[w])
    return res

def extract_tag_from_ingredient(ingredient_list: List[str]) -> List[str]:
    l = word_tokenize(' '.join(ingredient_list))
    l = filter_BLACKLIST_WORDS_and_nonalpha_in_list(l)
    l = word_stemming(l)
    s = ','.join(l).encode("utf8").decode("ascii",'ignore')
    return s 

def get_tags_from_ingredients(ingredient_list: List[str]) -> List[str]:
    all_tags = []
    for ingredient in ingredient_list:
        if not isinstance(ingredient, list):
            all_tags.append([])
            continue
        all_tags.append(extract_tag_from_ingredient(ingredient))
    return all_tags

def clean_ingredients(ingredient_list: List[str]) -> List[str]:
    all_ingredients = []
    for ingredients in ingredient_list:
        if not ingredients or not isinstance(ingredients, list):
            all_ingredients.append([])
            continue
        for idx, ingredient in enumerate(ingredients):
            filter_blacklist = set(ingredient.split()).intersection(CUSTOM_BLACKLIST)
            if filter_blacklist:
                for w in filter_blacklist:
                    ingredients[idx] = ingredients[idx].replace(w, '').strip()
        all_ingredients.append(ingredients)
    return all_ingredients

def create_knowledge_graph(df: pd.DataFrame) -> Dict[str, Set[str]]:
    KG = defaultdict(set)
    for idx, row in df.iterrows():
        if len(row['tags']) == 0:
            continue
        tags = row['tags'].split(',')
        recipe = RecipeNode(
            title=row['title'],
            ingredients=row['ingredients'],
            instructions=row['instructions'],
            tags=set(tags)
        )
        for tag in tags:
            KG[tag].add(recipe)
    logging.debug("Number of tags: {}".format(len(KG)))
    return KG

def create_dataframe(list_of_json_dish: List[str]) -> pd.DataFrame:
    # pandas convert to dataframe
    df = pd.read_json(json.dumps(list_of_json_dish))
    logging.debug("Number of recipes: {}".format(len(df)))

    # filter blacklist words in ingredients
    df['ingredients'] = clean_ingredients(df['ingredients'].tolist())

    # add feature: tags -> food nouns in ingredients
    df['tags'] = get_tags_from_ingredients(df['ingredients'].tolist())
    return df
