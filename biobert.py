import nlu 
import pandas as pd
# import Math

def biobert_mapper(input):
    embeddings = []
    # embeddings_types = []
    for line in input:
        embedding = nlu.load('biobert').predict(line, output_level='sentence')
        # embeddings_types.append(type(embedding))
        embeddings.append(embedding)
    complete_embeddings = pd.concat(embeddings)
    return complete_embeddings


# def cal_cosine(vec1, vec2):
#     return inner(vec1, vec2)/sqrt(np.dot(vec1, vec1)*dot(vec2, vec2))