#!/usr/bin/env python3

# Logging and debugging
import pdb
import logging

# Manipulate files
import os
import re
import csv
from pathlib import Path

# Handle remote files
from urllib.request import urlopen

# Manipulate lists
#import random
import itertools
from operator import itemgetter

# Command-line interface
import typer
from typing_extensions import Annotated

"""
Functions to initialize the database.
"""

def add_new_word_to_index(word, column_name, position, index_list, word_positions):
    new_word_locations = {column_name: [position]}
    new_index_item = {'word': word, 'locations': new_word_locations}

    word_positions[word] = len(index_list)
    index_list.append(new_index_item)
    return index_list

def update_index(column, index_list, word_positions):
    column_name = column[0]

    column_position_dictionary = {}
    for position, this_string in enumerate(column):
        try:
            number = float(this_string)
            continue
        except:
            words = this_string.split(" ")

        for word in words:
            word_index_position = word_positions.get(word)
            if word_index_position:
                # This word has already been added to the index
                word_index_entry = index_list[word_index_position]
                #logging.debug(f"Word index entry: {word_index_entry}.")
                word_locations = word_index_entry['locations']
                this_column_positions = word_locations.get(column_name)
                if this_column_positions:
                    # This column has already been added to the locations for this word
                    #logging.debug(f"Column name: {column_name}, this column positions: {this_column_positions}")
                    this_column_positions.append(position)
                    # Convert the list to a set to get unique values
                    word_locations[column_name] = list(set(this_column_positions))
                else:
                    # I need to add this column added to locations
                    word_locations[column_name] = [position]
            else:
                # I need to add this word to the index
                index_list = add_new_word_to_index(word, column_name, position, index_list, word_positions)

def transpose_matrix(matrix):
    """Transpose a matrix represented as a list of lists.

    Arguments:
        matrix (list): A list of equal length lists.
    
    Returns:
        (list): A list of lists where all of the values have been transposed.
    """

    transposed_matrix = [[row[index] for row in matrix] for index in range(len(matrix[0]))]
    return transposed_matrix

def initialize_database():
    """Generate the index and associated data structures that are at the core of the database.
    
    Returns:
        (list): The primary index of words in the database stored as dictionaries with references to each location of each word in the database.
        (dict): The primary index represented as a dictionary where the key is the word and the value is a list of locations where that word occurs in the metadata dictionary.
        (dict): A mapping of each word to its position in the primary index.
    """

    index_list = [{"word": "index", "locations": {"index": [0]}}]
    word_positions = {"index": 0}
    return {
            "index_list": index_list, 
            "word_positions": word_positions
    }

def read_comma_separated_values_file_to_matrix(csv_path):
    if re.search("^https://", csv_path):
        # Handle remote objects
        # Reference: https://bobbyhadz.com/blog/read-csv-file-from-url-using-python#reading-a-csv-file-from-a-url-using-csv-and-urllib
        csv_handle = urlopen(csv_path)
        lower_stream = (line.decode('utf-8').lower() for line in csv_handle.readlines())
    else:
        # Handle local objects
        with open(csv_path, 'r') as csv_handle:
            lower_stream = (line.lower() for line in csv_handle.readlines())
    # Read data comma separated values into a matrix of rows
    csv_reader = csv.reader(lower_stream)
    return [row for row in csv_reader]

    """
    # Read file into a matrix of rows
    with open(csv_file, 'r') as csv_handle:
        lower_stream = (line.lower() for line in csv_handle)
        csv_reader = csv.reader(lower_stream)
        return [row for row in csv_reader]
    """

def add_loop_name_to_first_row_of_matrix(csv_file_path, matrix):
    stem_name = Path(csv_file_path).stem
    # Treat underscores as spaces
    stem_words = stem_name.split("_")
    stem_string = " ".join(stem_words)

    appended_first_row = [" ".join([stem_string, value]) for value in matrix[0]]
    matrix[0] = appended_first_row
    return matrix

def convert_data_matrix_to_metadata_matrix(data_matrix, word_positions):
    metadata_columns = []
    for column in data_matrix:
        metadata_column = []
        column_name = column[0]

        for position, value in enumerate(column):
            reference = read_string_to_reference(value, word_positions)
            metadata_column.append(reference)
        metadata_columns.append(metadata_column)
    return metadata_columns

def convert_metadata_matrix_to_dictionary(metadata_matrix):
    dictionary_keys = [tuple(references[0]['positions']) for references in metadata_matrix]
    metadata_dictionary = dict(zip(dictionary_keys, metadata_matrix))
    return metadata_dictionary

def read_string_to_reference(this_string, word_positions):
    try:
        number = float(this_string)
        return number
    except:
        this_string_positions = []
        words = this_string.split(" ")

    this_string_positions = [read_word_to_index_position(word, word_positions) for word in words] 
    this_string_reference = {
                             "column": "index",
                             "positions": this_string_positions
    }
    #logging.debug(f"Converted string '{this_string}' to reference {this_string_reference}.")
    return this_string_reference

def read_word_to_index_position(word, word_positions):
    if not isinstance(word, str):
        return ValueError(f"This word is not of type string: {word}.")

    word_position = word_positions.get(word)
    if word_position:
        return word_position
    else:
        raise ValueError(f"Could not find word {word} in word_positions: {word_positions}.")

def add_loop_name_to_ends_of_columns_in_matrix(column_matrix):
    # Add the next column name to the end of each column
    looped_column_matrix = column_matrix.copy()
    for current_position, column in enumerate(looped_column_matrix):
        next_position = current_position + 1
        if next_position >= len(column_matrix):
            next_column_name = column_matrix[0][0]
            column.append(next_column_name)
        else:
            next_column_name = column_matrix[current_position + 1][0]
            column.append(next_column_name)
    return looped_column_matrix

"""
Search algorithm functions.
"""

def get_columns_in_loop(metadata_column_dictionary, current_column_key, columns_traversed=[]):
    if current_column_key in columns_traversed:
        return columns_traversed

    columns_traversed.append(current_column_key)
    current_column = metadata_column_dictionary[current_column_key]

    next_column_key = tuple(current_column[-1]['positions'])
    return get_columns_in_loop(
                               metadata_column_dictionary,
                               next_column_key,
                               columns_traversed)

def column_traversal_search(metadata_column_dictionary, current_column_key, column_keys_to_look_for, columns_traversed=[], viable_paths={}):
    """Find all viable paths from the current column to the ones I am looking for.

    Args:
        metadata_column_dictionary (dict): A dictionary containing all of the database metadata.
        current_column_positions (tuple): A tuple listing the index position of each word in the name of the column.
        columns_to_look_for (list): A list of eligible destination files.
        columns_traversed (list): A list of the files that have already been traversed during search.

    Returns:
        columns_traversed (list): Once a destination file has been found this function will return the list of files traversed.
    """
    if current_column_key in columns_traversed:
        logging.debug(
               f"Completed a loop and returning results. "
               f"Current column key: {current_column_key}, "
               f"columns traversed: {columns_traversed}.")
        # Return all viable paths once I complete a loop
        return viable_paths

    columns_traversed.append(current_column_key)
    logging.debug(f"Current column key: {current_column_key}. "
                  f"Columns to look for: {column_keys_to_look_for}. "
                  f"Columns traversed: {columns_traversed}."
                  f"Viable paths: {viable_paths}.")

    # Add the current path to the list of viable paths 
    if current_column_key in column_keys_to_look_for:
        viable_paths[current_column_key] = columns_traversed.copy()
        logging.debug(
                      f"Added viable path. "
                      f"{current_column_key}: {viable_paths[current_column_key]}.")
    
    current_column= metadata_column_dictionary[current_column_key]
    # I need to convert the list of index positions into a tuple so that
    # I can use it as a dictionary key.
    next_column_key = tuple(current_column[-1]['positions'])
    return column_traversal_search(
                                   metadata_column_dictionary,
                                   next_column_key,
                                   column_keys_to_look_for,
                                   columns_traversed,
                                   viable_paths)

def convert_string_to_index_positions(this_string, word_positions):
    if not isinstance(this_string, str):
        raise ValueError(f"This {this_string} needs to be a string.")
    return [word_positions.get(word) for word in this_string.split()]

def get_query_word_column_locations(query, index_list, word_positions):
    # Constitute an index dictionary
    index_dictionary = {item["word"]: item["locations"] for item in index_list}
    
    query_words = query.split()

    query_word_location_lists = []
    for word in query_words:
        word_locations = index_dictionary.get(word)
        if not word_locations:
            raise ValueError(f"No index entry for '{word}'.")
       
        logging.debug(f"Word locations for word '{word}': {word_locations}.")
        # Example location{'player first name': [0]}       

        # Convert column names to index positions
        metadata_word_locations = []
        for column_name, positions in word_locations.items():
            metadata_column_locations = {
                "column": tuple(convert_string_to_index_positions(column_name, word_positions)),
                "positions": positions.copy()
            }
            metadata_word_locations.append(metadata_column_locations)        
        query_word_location_lists.append(metadata_word_locations)
        #logging.debug(f"Query word location lists: {query_word_location_lists}.")
    return query_word_location_lists

# Deprecated in favor of calculate_endpoints_score
def calculate_positions_score(first_position, second_position):
    if first_position == second_position:
        return 1
    else:
        return -1

def calculate_endpoints_score(first_endpoint, second_endpoint):
    # Columns and positions are identical
    if first_endpoint == second_endpoint:
        return 2
    # Positions are identical 
    elif first_endpoint[1] == second_endpoint[1]:
        return 1
    # Neither columns nor positions are identical
    else:
        return -1

def find_query_loops(metadata_column_dictionary, looped_query_word_locations):
    """
    Arguments:
        metadata_column_dictionary (dict): A dictionary of the database represented as references to the index.
        query_word_locations_lists (list): A list of lists of locations where each word in the query can be found. Each inner list corresponds to the word in the query at the same position.
    """
    edges_list = []
    for query_word_position, query_word_locations in enumerate(looped_query_word_locations):
        # Here query_word_locations is a list of locations that corresponds
        # to the query word.
        if query_word_position >= len(looped_query_word_locations) - 1:
            break
        
        for current_location in query_word_locations:
            logging.debug(f"Current location: {current_location}.")

            current_column = current_location["column"]
            # Use this list to filter locations of the next query word
            columns_in_loop = get_columns_in_loop(
                                                  metadata_column_dictionary,
                                                  current_column,
                                                  columns_traversed=[])
            current_positions = current_location["positions"]
            logging.debug(f"Current positions: {current_positions}.")

            # Create a list of locations that can be found on this loop.
            # Location format: {"column": (1), "positions": [1]}
            next_locations = looped_query_word_locations[query_word_position + 1]
            next_viable_locations = [
                                     location for location
                                     in next_locations
                                     if location["column"] in columns_in_loop]
            logging.debug(f"Next viable locations: {next_viable_locations}.")

            # If a location points to the column name at index zero
            # then the positions are effectively wildcards.
            # reference: https://stackoverflow.com/a/58265773
            next_wildcard_locations = next_viable_locations.copy()
            for this_location in next_wildcard_locations:
                if 0 in this_location['positions']:
                    this_location['positions'].remove(0)
                    this_location['positions'].extend(current_positions)
            logging.debug(f"Next wildcard locations: {next_wildcard_locations}.")

            # Replace wildcard position with all possible next positions
            if 0 in current_location["positions"]:
                current_location["positions"].remove(0)
                
                all_next_positions = []
                for location in next_wildcard_locations:
                    all_next_positions.extend(location["positions"])
                current_location["positions"].extend(all_next_positions)
                
            start_pointers = [
                              (current_location["column"], position)
                              for position in current_location["positions"]
            ]
            logging.debug(f"Start pointers: {start_pointers}.")

            end_pointers = []
            for location in next_wildcard_locations:
                for position in location['positions']:
                    end_pointers.append((location["column"], position))
            logging.debug(f"End pointers: {end_pointers}.")

            endpoint_pairs = list(itertools.product(start_pointers, end_pointers))
            logging.debug(f"Endpoint pairs: {endpoint_pairs}.")

            endpoint_scores = [
                               calculate_endpoints_score(endpoints[0], endpoints[1])
                               for endpoints in endpoint_pairs
            ]
            logging.debug(f"Endpoint scores: {endpoint_scores}.")
            max_endpoints_score = max(endpoint_scores)            

            scored_endpoints = zip(endpoint_pairs, endpoint_scores)
            max_score_endpoints = [
                                   endpoints for endpoints
                                   in scored_endpoints
                                   if endpoints[1] == max_endpoints_score]
            logging.debug(f"Max score endpoints: {max_score_endpoints}.")

            # Generate a list of viable edges
            max_score_edges = []
            for endpoints in max_score_endpoints:
                metadata_values = endpoints[0]
                score = endpoints[1]        
        
                start_reference = metadata_values[0]
                end_reference = metadata_values[1]
                
                edge_dictionary = {
                                   "start": start_reference,
                                   "end": end_reference,
                                   "score": score
                }
                max_score_edges.append(edge_dictionary)
            edges_list.append(max_score_edges)
            logging.debug(f"Max score edges: {max_score_edges}.")
            logging.debug("===")
            #pdb.set_trace()
    return edges_list

def calculate_edge_score(edge, edge_position, column_position_dictionaries):
    """
    Arguments:
        edge (dict): Keys are start, end, and score.
    """
    start_position = column_position_dictionaries[edge_position][tuple(edge['start'])]
    end_position = column_position_dictionaries[edge_position + 1][tuple(edge['end'])]

    if start_position == 0 or end_position == 0:
        max_position = max([start_position, end_position])
        start_position = max_position
        end_position = max_position

    position_score = abs(start_position - end_position)
    edge_score = position_score * edge["number_of_steps"]
    return edge_score

def choose_loop(list_of_viable_edges, previous_node=None):
    chosen_edges = []
    for position, viable_edges in enumerate(list_of_viable_edges):
        if previous_node:
            matching_viable_edges = [edge for edge in viable_edges if edge['start'] == previous_node]
        else:
            matching_viable_edges = viable_edges
        
        sorted_viable_edges = sorted(matching_viable_edges, key=lambda edge: edge['score'])
        chosen_edge = sorted_viable_edges[0]
        chosen_edges.append(chosen_edge)
    return chosen_edges

def make_a_loop(current_node, edges_dictionary, loop=[]):
    logging.debug(f"Making a loop from current node: {current_node}.")
    next_nodes = edges_dictionary.get(current_node)
    
    # What happens if I just throw out broken loops?
    if not next_nodes:
        return None

    # [(((column), position), score)]
    # [(((1, 16), 2), 1)]
    logging.debug(f"Current loop: {loop}.")
    logging.debug(f"Next potential nodes: {next_nodes}.")
    next_different_nodes = [node for node in next_nodes if node[0] != current_node]   
     
    maximum_score = max([node[1] for node in next_different_nodes])
    maximum_score_nodes = [node for node in next_different_nodes if node[1] == maximum_score]

    next_node = maximum_score_nodes[0] 

    # I deprecated this logic in favor of only getting highest scored nodes
    #positive_nodes = [node for node in next_different_nodes if node[1] > 0]
    #negative_nodes = [node for node in next_different_nodes if node[1] < 0]

    #if positive_nodes:
    #    next_node = random.choice(positive_nodes)
    #else:
    #    next_node = random.choice(negative_nodes)

    for next_node in maximum_score_nodes:
        logging.debug(f"Next node: {next_node}, first node: {loop[:1]}.")
        if loop and next_node[0] in loop[:1][0]:
            return tuple(loop)
        else:
            loop.append(next_node)
    return make_a_loop(next_node[0], edges_dictionary, loop)

    """Old logic.
    logging.debug(f"Next node: {next_node}, first node: {loop[:1]}.")    
    if loop and next_node[0] in loop[:1][0]:
        logging.debug(f"Completed loop: {loop}.")
        return tuple(loop)
    else:
        # I add the next node without adding the current node
        # because only the values in the edges_dictionary contain
        # edge scores which I use for prioritization.
        loop.append(next_node)
        return make_a_loop(next_node[0], edges_dictionary, loop)
    """

def import_comma_separated_values(database, csv_file_path):
    index_list = database["index_list"]
    word_positions = database["word_positions"]

    row_matrix = read_comma_separated_values_file_to_matrix(csv_file_path)
    looped_row_matrix = add_loop_name_to_first_row_of_matrix(csv_file_path, row_matrix)
    column_matrix = transpose_matrix(looped_row_matrix)
    
    column_name_words = [name.split(" ")[1:] for name in row_matrix[0]]
    column_names = [" ".join(words) for words in column_name_words]
    database["column_names"] = column_names
    #pdb.set_trace()   
 
    for column in column_matrix:
        update_index(column, index_list, word_positions)    

    # Add the next column name to the end of each column
    looped_column_matrix = add_loop_name_to_ends_of_columns_in_matrix(column_matrix)

    metadata_column_matrix = convert_data_matrix_to_metadata_matrix(
                                                                looped_column_matrix,
                                                                word_positions)
    metadata_column_dictionary = convert_metadata_matrix_to_dictionary(metadata_column_matrix)
    database["metadata_column_dictionary"] = metadata_column_dictionary
    return database

def create_dictionary_of_edges(edges):
    edges_dictionary = {}
    for edge_list in edges:
        for edge in edge_list:
            start_node = edge['start']
            end_node = edge['end']
            score = edge['score']

            if start_node == end_node:
                # Handle self-referencing edges
                logging.debug(
                              f"Found self-referencing edge with "
                              f"start: {start_node} "
                              f"and end: {end_node}.")
                for key, values in edges_dictionary.items():
                    for index, value in enumerate(values):
                        if value[0] == start_node:
                            logging.debug(f"Updating key: {key}, values: {values}.")
                            new_value = (value[0], value[1] + score)
                            values.pop(index)
                            edges_dictionary[key].insert(index, new_value)
                            logging.debug(f"New key: {key}, values: {edges_dictionary[key]}.")
            else: 
                value = (end_node, score)

                if edges_dictionary.get(start_node):
                    edges_dictionary[start_node].append(value)
                else:
                    edges_dictionary[start_node] = [value]
    return edges_dictionary

def create_loops_from_dictionary_edges(edges_dictionary):
    all_loops = []
    for start_node in edges_dictionary.keys():
        #logging.debug("===")
        logging.debug(f"Making a loop from start node: {start_node}.")
        loop = make_a_loop(start_node, edges_dictionary, loop=[])
        if loop:
            all_loops.append(loop)
        logging.debug(f"Length of all loops: {len(all_loops)}.")
        logging.debug("===")
    return all_loops

def calculate_loop_scores(loops):
    cumulatively_scored_loops = []
    for loop in loops:
        # Reference: https://stackoverflow.com/a/25047602
        cumulative_loop_score = sum(edge[-1] for edge in loop) / len(loop)
        scored_loop = (loop, cumulative_loop_score)
        cumulatively_scored_loops.append(scored_loop)
        logging.debug(f"Cumulative loop score for {loop}: {cumulative_loop_score}.")
    return cumulatively_scored_loops 

def create_matrix_of_loop_columns(loops):
    loop_columns = []
    for loop in loops:
        nodes = loop[0]
        node_columns = [node[0][0] for node in nodes]
        loop_columns.append(node_columns)
    return loop_columns

def get_most_symmetrical_loop(transposed_loop_columns, query_word_locations_list):
    loop_indexes = []
    for word_locations_list in query_word_locations_list:
        for word_locations in word_locations_list:
            word_column = word_locations["column"]
            for row in transposed_loop_columns:
                for index, value in enumerate(row):
                    if word_column == value:
                        loop_indexes.append(index)
                if loop_indexes:
                    return loop_indexes
    return None

def convert_loop_into_string(database, loop_nodes):
    metadata_column_dictionary = database["metadata_column_dictionary"]
    index_list = database["index_list"]

    result_string = []
    for node in loop_nodes:
        column = node[0][0]
        position = node[0][1]
        value = metadata_column_dictionary[column][position]
        if isinstance(value, dict):
            for position in value['positions']:
                word = index_list[position]['word']
                result_string.append(word)
        else:
            result_string.append(str(value))
    result = " ".join(result_string)
    return result

def convert_loop_into_dictionary(database, loop_nodes):
    """Convert a loop into a dictionary.

    Convert a loop into a dictionary so that I can share
    result values as well as column names.

    Args:
        database (dict): Dictionary of persistent database resources.
        loop_nodes (list): Locations of all the nodes in the loop.

    Returns:
        (dict): Dictionary of column names and loop values.
    """
    result_dictionary = {}
    metadata_column_dictionary = database["metadata_column_dictionary"]
    index_list = database["index_list"]

    for node in loop_nodes:
        column = node[0][0]
        position = node[0][1]
        column_locations = metadata_column_dictionary[column][0]
        value = metadata_column_dictionary[column][position]
        
        column_words = [
                        index_list[position]['word'] 
                        for position
                        in column_locations['positions'][1:]
        ]
        column_name = " ".join(column_words)

        if isinstance(value, dict):
            values = []
            for position in value['positions']:
                value = index_list[position]['word']
                values.append(value)
            value = " ".join(values)
        else:
            value = str(value)
        
        logging.debug(f"Column name: {column_name}, value: {value}.")
        #pdb.set_trace()
        result_dictionary[column_name] = value
    return result_dictionary

def process_query(database, query):
    index_list = database["index_list"]
    word_positions = database["word_positions"]
    metadata_column_dictionary = database["metadata_column_dictionary"]

    query_word_locations_list = get_query_word_column_locations(
                                                                query,
                                                                index_list,
                                                                word_positions)
    logging.debug(f"Query word location lists: {query_word_locations_list}.")

    looped_query_word_locations = query_word_locations_list.copy()
    looped_query_word_locations.append(looped_query_word_locations[0])

    # Find paths between adjacent seach terms
    logging.debug("Calling find_query_loops().")
    edges = find_query_loops(
                             metadata_column_dictionary,
                             looped_query_word_locations)
    logging.debug("Calling create_dictionary_of_edges().")
    edges_dictionary = create_dictionary_of_edges(edges)
    logging.debug(f"Edges dictionary: {edges_dictionary}.")
    #pdb.set_trace()

    # Find loops of contiguous edges
    all_loops = create_loops_from_dictionary_edges(edges_dictionary) 
    #pdb.set_trace()
    cumulatively_scored_loops = calculate_loop_scores(all_loops)
    logging.debug(f"Number of cumulatively scored loops: {len(cumulatively_scored_loops)}.")
    #pdb.set_trace()
   
     # Find the highest scored loops
    maximum_loop_score = max([loop[-1] for loop in cumulatively_scored_loops])
    highest_scored_loops = [
                        loop for loop 
                        in cumulatively_scored_loops
                        if loop[-1] == maximum_loop_score]
    highest_scored_loops = list(set(highest_scored_loops))
    sorted(highest_scored_loops)
    logging.debug(f"Highest scored loops: {highest_scored_loops}.")

    loop_columns = create_matrix_of_loop_columns(highest_scored_loops)
    transposed_loop_columns = transpose_matrix(loop_columns)

    loop_indexes = get_most_symmetrical_loop(transposed_loop_columns, query_word_locations_list)
    loops_to_return = [highest_scored_loops[loop_index] for loop_index in loop_indexes]

    loops_nodes = [loop[0] for loop in loops_to_return]
    #results = [convert_loop_into_string(database, loop_nodes) for loop_nodes in loops_nodes]
    results = [convert_loop_into_dictionary(database, loop_nodes) for loop_nodes in loops_nodes]
    return results

def circuity(
            csv_path: Annotated[str, typer.Option(help="The path to a comma separated values file to import")] = "https://storage.googleapis.com/espn-data/espn-nfl-rosters.csv",
            query: Annotated[str, typer.Option(help="A database query")] = "",
            debug: Annotated[bool, typer.Option(help="Set logging level to debug")] = False,
            columns: Annotated[bool, typer.Option(help="Show column names")] = False,
            examples: Annotated[bool, typer.Option(help="Show example queries")] = False
):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    if examples:
        example_queries = {
            "robert hainsey college": "Get the college that Robert Hainsey attended.",
            "trevor lawrence years of experience": "Get the number of years Trevor Lawrence has played in the National Football League.",
            "nick mullens height": "Get the height values of Nick Mullens.",
            "jaguars quarterback age": "Get the ages of all the quarterbacks on the Jacksonville Jaguars.",
            "jaguars wide receiver name age": "Get the names and ages of all the wide receivers on the Jacksonville Jaguars."
        }
        print("These are example queries designed to work with the default ESPN National Football League roster dataset available at https://storage.googleapis.com/espn-data/espn-nfl-rosters.csv.")
        print("Example database query: description")
        print("=")
        for example_query, description in example_queries.items():
            print(f"'{example_query}': {description}")
        print("===")
    """
    if not csv_path or not query:
        print(
              "I must provide the path to a comma separated values "
              "file with the data I would like to query as well as my "
              "query like so: '$circuity --csv-path data/players.csv --query 'justin age'.")
    else:
    """

    if columns:
        database = initialize_database()
        database = import_comma_separated_values(database, csv_path)    
        print(f"Column names: {database['column_names']}.")
        print("===")

    if query:
        database = initialize_database()
        database = import_comma_separated_values(database, csv_path)
        #logging.debug(f"Database index: {database['index_list']}.")
        results = process_query(database, query)
        merged_results_dictionary = {
                                      key: [dict[key] for dict in results] 
                                      for key in results[0]
        }
        result_values_matrix = transpose_matrix(list(merged_results_dictionary.values()))
        #pdb.set_trace()
        
        print(",".join(merged_results_dictionary.keys()))
        for result_values_list in result_values_matrix:
            print(",".join(result_values_list))
