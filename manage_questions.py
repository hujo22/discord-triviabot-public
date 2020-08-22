# imports and manages trivia questions

import pandas as pd
import os
import shutil

class Questions:
    def __init__(self, file_name):
        #get directory of current script and make data frame
        self.__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.csv_file = os.path.join(self.__location__, file_name)
        try:
            self.df = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            #if file not found, make a  copy of original trivia_questions.csv
            self.src_file = os.path.join(self.__location__, 'trivia_questions.csv')
            shutil.copyfile(self.src_file, self.csv_file)
            self.df = pd.read_csv(self.csv_file)

    def get_categories(self):
        #returns list of all categories
        self.categories = pd.DataFrame(self.df.Category.unique(), columns = ['Categories'])
        self.categories = self.categories.sort_values(by='Categories') #sort alphabetically
        self.categories = self.categories.reset_index(drop=True)
        self.cat_llist = self.categories.values.tolist() #convert dataframe to list of lists
        self.cat_list = [item for sublist in self.cat_llist for item in sublist] #convert to list
        return self.cat_list

    def get_question(self, category = None):
        #returns a question, its answer, and its category
        if category == None: #if no category is given
            q = self.df.iloc[0] #question to be returned is the first one on the list
            self.df = self.df.drop(0)
            self.df = self.df.append(q, ignore_index=True)
        else:
            for i in range(len(self.df.index)):
                if category.lower() == self.df.loc[i, 'Category'].lower():
                    q = self.df.iloc[i]
                    self.df = self.df.drop(i)
                    self.df = self.df.append(q, ignore_index = True)
                    break
        
        return q.loc['Question'], q.loc['Answer'], q.loc['Category']

    def save_questions_state(self, output_filename):
        #saves current state of questions to prevent repeated questions
        self.df.to_csv(os.path.join(self.__location__, output_filename), index = False) #save to new csv
    
    def clean_csv(self):
        #clean up csv file
        # self.df = self.df.applymap(lambda x: x.strip() if isinstance(x, str) else x) #strip white space
        # self.df = self.df.replace('Technology & Video Games', 'Tech & Video Games') #replace 1st arg with 2nd arg
        # self.df = self.df.replace('Mathematics & Geometry', 'Mathematics')
        self.df = self.df.drop(['Used'], axis=1)
        self.df.to_csv(os.path.join(self.__location__, 'trivia_questions.csv'), index = False) #save to new csv

if __name__ == '__main__':
    import time
    t0 = time.time()
    
    print('run time: ', time.time() - t0)