import nlu 

def biobert_mapper(input):
    list_of_lines = []
    for line in input:
        list_of_lines.append(nlu.load('biobert').predict(line))
    print(list_of_lines)


# pipe = nlu.load('biobert').predict('He was suprised by the diversity of NLU')

# print(pipe)