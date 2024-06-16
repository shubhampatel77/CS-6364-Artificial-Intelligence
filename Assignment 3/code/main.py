import sys

# Read the knowledge base, return a list of clauses
def read_kb(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().split('\n')
    kb = [(line.split()) for line in lines[:-1]]
    kb = [[clause,-1, -1] for clause in kb]
    test_clause = lines[-1].split()
    return kb, test_clause

# Negate a clause
def negate_clause(clause):
    new_clauses = [['~' + literal] if literal[0] != '~' else [literal[1:]] for literal in clause ]
    new_clauses = [[clause,-1, -1] for clause in new_clauses]
    return new_clauses

# Remove repeated and redundant literals
def remove_redundant_literals(clause):
    freq = {l: 0 for l in clause}
    for l in clause:
        freq[l] += 1
    for l in clause:
        if l[0] == '~':
            if l[1:] in freq:
                return []
    return [l for i, l in enumerate(freq)]

# Check if literals are negations of each other             
def are_negations(s1, s2):
    return (s1[0] == '~' and s1[1:] == s2) or (s2[0] == '~' and s2[1:] == s1)

# Check if a generated clause is not already present in the KB
def is_new(kb_set, result):
    result_set = set(result)
    for clause_set in kb_set:
        if clause_set == result_set:
            return False
    return True

# Resolves two clauses, updates the KB
def resolve(kb_set, kb, first, second):
    clause1 = kb[first][0]
    clause2 = kb[second][0]

    new_clause = []
    if len(clause1) == 1 and len(clause2) == 1 and are_negations(clause1[0], clause2[0]):
        kb += [[['Contradiction'], first+1, second+1]]
        return False
    for l1 in clause1:
        for l2 in clause2:
            if are_negations(l1, l2):
                new_clause = [x for x in clause1 if x != l1] + [x for x in clause2 if x != l2]
                break
    if new_clause:
        result = remove_redundant_literals(new_clause)
        if result:
            if is_new(kb_set, result):
                kb_set += [set(literal for literal in result)]
                kb += [[result, first+1, second+1]]
    return True
        
# Resolution of the entire KB
def resolution_algorithm(kb_set, kb):
    i = 1
    while i != len(kb) - 1:
        for j in range(i):
            if not resolve(kb_set, kb, i , j):
                return False
        i += 1
    
    return True

# Print in required format         
def print_formatted(res, kb):
    for idx in range(len(kb)):
        clause = " ".join([str(item) for item in kb[idx][0]])
        i = kb[idx][1]
        j = kb[idx][2]
        print(f'{idx+1}. {clause} {{{i}, {j}}}') if i != -1 and j != -1 else print(f'{idx+1}. {clause} {{}}')
    
    print('Fail') if res else print('Valid')

def main(file_path):

    knowledge_base, test_clause = read_kb(file_path)
    new_clauses = negate_clause(test_clause)

    knowledge_base += new_clauses
    # Set for easy memebership checks
    knowledge_base_set = [set(literal for literal in sentence[0]) for sentence in knowledge_base]


    res = resolution_algorithm(knowledge_base_set, knowledge_base)
    print(len(knowledge_base))
    print_formatted(res, knowledge_base)
   
if __name__ == "__main__":
    main(sys.argv[1])
