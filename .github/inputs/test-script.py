import pandas as pd


def extractTerms(
    goldStandard="https://raw.githubusercontent.com/EBISPOT/EFO-UKB-mappings/master/UK_Biobank_master_file.tsv",
    columnName="ZOOMA QUERY",
    fileName="./terms.txt",
):
    """
    extracts the terms in the column columnName of the goldStandard .tsv file
    and saves them
    """
    biobank = pd.read_csv(
        goldStandard,
        sep="\t",
        header=0,
    )

    terms = ""
    for term in biobank[columnName]:
        terms += term + "\n"
    terms = terms[:-1]  # remove trailing newline

    with open(fileName, "w") as f:
        f.write(terms)
