import nlu 
import pandas as pd
from gensim.parsing.preprocessing import strip_multiple_whitespaces, strip_non_alphanum
import ontoutils

# import Math
# from biobert_embedding.embedding import BiobertEmbedding
# from scipy.spatial import di
# stance

def _preprocess(text):
        """
        Normalizes a given string by converting to lower case, removing non-word characters, stop words, white space
        :param text: Text to be normalized
        :return: Normalized string
        """
        text = strip_non_alphanum(text).lower()
        text = text.replace("_", " ")
        text = " ".join(w for w in text.split() if w not in ontoutils.STOP_WORDS)
        text = strip_multiple_whitespaces(text)
        return text

def biobert_mapper(input):
    # embeddings_types = []
    # text = ['heart attack', 'high blood pressure']
    # complete_embeddings = nlu.load('en.embed_sentence.biobert.pmc_base_cased').predict(text, output_level='sentence')
    print('in biobert')
    list_embeddings = []
    list_lines = []
    nlu_loader = nlu.load('en.embed_sentence.biobert.pmc_base_cased')
    for line in input:

        list_lines.append(_preprocess(line))

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

# def alt_biobert(input):
#      # embeddings_types = []
#     # text = ['heart attack', 'high blood pressure']
#     # complete_embeddings = nlu.load('en.embed_sentence.biobert.pmc_base_cased').predict(text, output_level='sentence')
#     list_embeddings = []
#     list_lines = []
#     # nlu_loader = nlu.load('en.embed_sentence.biobert.pmc_base_cased')
#     for line in input:

#         list_lines.append(line)

#     # embeddings = nlu_loader.predict(list_lines, output_level='sentence')
#     # complete_embeddings = embeddings.drop('sentence', 1)
#     df = pd.DataFrame({'Problem Assessment': list_lines})
#     biobert = BiobertEmbedding()
#     df['sentence embedding'] = df['Problem Assessment'].apply(lambda sentence: biobert.sentence_vector(sentence))
    

#     for element in df.values:
#         list_embeddings.append(element[0])
    
#     return list_embeddings


# if True:
#     result = ['China']
#     print(biobert_mapper(result))
