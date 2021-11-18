import nlu 
import pandas as pd
# import Math

def biobert_mapper(input):
    # embeddings_types = []
    # text = ['heart attack', 'high blood pressure']
    # complete_embeddings = nlu.load('en.embed_sentence.biobert.pmc_base_cased').predict(text, output_level='sentence')
    print('in biobert')
    list_embeddings = []
    list_lines = []
    nlu_loader = nlu.load('en.embed_sentence.biobert.pmc_base_cased')
    for line in input:

        list_lines.append(line)

        # embeddings = nlu_loader.predict(line, output_level='sentence')
        # if type(embeddings) == None:
        #     print(line)
        # else:
        #     print("okay!")
        # embeddings_types.append(type(embedding))
        # embeddings.append(embedding)
    # print(list_lines[0:10])
    # list_lines = list_lines[0:10]
    # print('list of lines', list_lines)
    # print('before embedding')
    embeddings = nlu_loader.predict(list_lines, output_level='sentence')
    # print('embeddings before drop')
    complete_embeddings = embeddings.drop('sentence', 1)
    # print('done', complete_embeddings)
    # print('line 32')
    #print("complete embeddings: ", complete_embeddings)
    for element in complete_embeddings.values:
        list_embeddings.append(element[0])
    #print('list_embeddings: ', list_embeddings)
    print('line 37')
    return list_embeddings


# def cal_cosine(vec1, vec2):
#     return inner(vec1, vec2)/sqrt(np.dot(vec1, vec1)*dot(vec2, vec2))