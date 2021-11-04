import nlu 
# import Math

def biobert_mapper(input):
    list_of_lines = []
    for line in input:
        list_of_lines.append(nlu.load('biobert').predict(line, output_level='sentence'))
    print(list_of_lines)

# def cal_cosine(vec1, vec2):
#     return inner(vec1, vec2)/sqrt(np.dot(vec1, vec1)*dot(vec2, vec2))