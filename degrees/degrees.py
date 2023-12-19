import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def check_first_degree(source_neighbors, target):
    for neighbor in source_neighbors:
        if neighbor[1] == target:
            return [neighbor]
    return None

def is_related(neighbors, target):    
    for n in neighbors:
        if n[1] == target:
            return [n]
        # else:
            # return find_degree(neighbors_for_person(n[1]), target)

def check_first_degree(neighbors, target):
    for neighbor in neighbors:
        if neighbor[1] == target:
            return [neighbor]

def assemble_path(neighbor, path):
    return { 'neighbors': neighbors_for_person(neighbor[1]), 'path': path, "actual": neighbor}

# breadth first search
def find_degree(s_neighbors, target):
    ids_checked = []
    
    first_degree = check_first_degree(s_neighbors, target)
    if first_degree: return first_degree

    counter = 0
    possible_paths = []
    min_possible_path = 9999999
    for neighbor in s_neighbors:
        if neighbor not in ids_checked:
            ids_checked.append(neighbor[1])
            paths = dict({ neighbor[1]: assemble_path(neighbor, [neighbor]) })
            current = neighbor[1]
            while len(paths) > 0:
                counter += 1
                if current not in list(paths.keys()):
                    current = list(paths.keys())[0]    
                cur_path = paths.pop(current)

                
                match = check_first_degree(cur_path["neighbors"], target)
                if match: 
                    if len(cur_path["path"]) == 1:
                        return [*cur_path["path"], *match]
                    possible_paths.append([*cur_path["path"], *match])
                    len_pp = len([*cur_path["path"], *match])
                    print('possible rel degree of:', len_pp)
                    if len_pp <= min_possible_path: min_possible_path = len_pp

                for neigh in cur_path['neighbors']:
                    neigh_id = neigh[1]
                    if neigh_id not in ids_checked:
                        ids_checked.append(neigh_id)
                        if len([*cur_path["path"], neigh]) < min_possible_path:
                            paths.update({neigh_id: assemble_path(neigh, [*cur_path["path"], neigh])})
                            current = neigh_id
                    elif len(paths.keys()) > 0:
                        current = list(paths.keys())[0]
    
    print('evaluated paths:', counter)
    print('possible paths:', len(possible_paths))
    if len(possible_paths) > 0:
        possible_paths.sort(key=lambda e: len(e))
        return possible_paths[0]
    return None


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    source_neighbors = neighbors_for_person(source)
    
    # first degree
    # has_first_degree = check_first_degree(source_neighbors, target)
    # if (has_first_degree): return has_first_degree
    return find_degree(source_neighbors, target)

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
