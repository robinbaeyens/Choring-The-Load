#######################################################################################
 #   ____ _                _               _____ _            _                    _  #
 #  / ___| |__   ___  _ __(_)_ __   __ _  |_   _| |__   ___  | |    ___   __ _  __| | #
 # | |   | '_ \ / _ \| '__| | '_ \ / _` |   | | | '_ \ / _ \ | |   / _ \ / _` |/ _` | #
 # | |___| | | | (_) | |  | | | | | (_| |   | | | | | |  __/ | |__| (_) | (_| | (_| | #
 #  \____|_| |_|\___/|_|  |_|_| |_|\__, |   |_| |_| |_|\___| |_____\___/ \__,_|\__,_| #
 #                                 |___/                                              #
 ######################################################################################

 # Robin Baeyens
 # March 2024j
 # Idea based on the 'Chorebuster' app

#######################################################################################
import numpy as np

class Chore_Distributor:
    """ Main class to read and distribute the chores. """


    def __init__(self, chore_info_path):
        """ Initialize the main object class with a chore info path.

        --- Parameter ---
        string: chore_info_path
            Full path to a folder containing all information containing the
            chores and past schedules.
        """
        self.chore_info_path = chore_info_path
        chorelist = self.find_chorelist()
        self.chorelist = self.read_chorelist(chorelist)


    def find_chorelist(self):
        """ Look in the info folder for a file containing the chores.

        --- Return ---
        string: chorelist
            File which lists all chores.
        """
        import glob
        # look for file names matching the expected pattern
        cip = self.chore_info_path
        matches = glob.glob(cip+'/chores*.ods') + glob.glob(cip+'/chores*.xlsx')

        # return if there's exactly one match
        if len(matches) == 0:
            raise ValueError('Error! No list of chores found in: ' + cip + '/\n' + \
                             "(The file names should start with 'chores' and have extension 'ods' or 'xlsx'.)")
        elif len(matches) > 1:
            raise ValueError('Oops, multiple files were found. Someone should implement a method to select one!')
        elif len(matches) == 1:
            chorelist = matches[0]
            return chorelist


    def read_chorelist(self, input_file):
        """ Read the given input file containing chores and weights.

        --- Parameter ---
        string: input_file
            Name of file containing the chores and weights.

        --- Returns ---
        df: pandas.DataFrame
            The list of chores with meta-data.
        """
        import pandas as pd
        df = pd.read_excel(input_file)

        # Do some basic input requirement checks
        if 'Chore' not in df.keys():
            raise ValueError(f'Input file {input_file} lacks "Chore" column.')
        if 'Frequency' not in df.keys():
            raise ValueError(f'Input file {input_file} lacks "Frequency" column.')
        if 'Dedicated' not in df.keys():
            raise ValueError(f'Input file {input_file} lacks "Dedicated" column.')
        if 'Weight' not in df.keys():
            raise ValueError(f'Input file {input_file} lacks "Weight" column.')
        if df['Chore'].duplicated().any():
            raise ValueError('Duplicate chores found in the "Chore" column.')
        for f in df['Frequency']:
            if not isinstance(f, int):
                raise ValueError('Non-integer value found in "Frequency" column.')
        for w in df['Weight']:
            if not isinstance(w, (int, float)):
                raise ValueError('Non-numerical value found in "Weight" column.')

        # Add column with 'Overdue' dates (days since chore was last done)
        df.insert(0, 'Overdue', np.ones_like(df['Chore'])*999)

        return df


    def new_week(self):
        """ Create a new week schedule based on the chore list and previous
        week's history.
        """
        self.update_overdue()
        self.week_schedule()


    def update_overdue(self):
        """ Update the 'Overdue' column of the chore list using the support
        log file.
        """
        import os.path
        overdue_log = self.chore_info_path+'/overdue.log'
        # If there's no overdue log file yet, make one
        if not os.path.isfile(overdue_log):
            print(f'[WARNING] No log file found at {overdue_log}. Creating new one.')
            with open(overdue_log, 'w') as f:
                for chore, val in zip(self.chorelist['Chore'], self.chorelist['Overdue']):
                    f.write(f'{chore},{val}\n')

        # Read overdue log and update/initialize the overdues of all chores
        with open(overdue_log, 'r') as f:
            for line in f.readlines():
                items = line.split(sep=',')
                self.chorelist.loc[self.chorelist['Chore']==items[0], 'Overdue'] = int(items[1])


    def is_overdue(self, chore_string):
        """ Return whether a chore is overdue.

        --- Parameter ---
        string: chore_string
            Name of the chore.

        --- Returns ---
        boolean: True/False
        """
        # Extract frequency and overdue values to compare
        cl = self.chorelist
        freq = cl.loc[cl['Chore'] == chore_string, 'Frequency'].item()
        over = cl.loc[cl['Chore'] == chore_string, 'Overdue'].item()

        if over >= freq:
            return True
        else:
            return False


    def week_schedule(self):
        """ Main algorithm to determine the schedule of this week's chores.
        """

#######################################################################################
if __name__ == "__main__":

    dist = Chore_Distributor('example')
    dist.new_week()
