import os
import pickle
from nlp_surveillance.annotator import *
from nlp_surveillance.utils.my_utils import matching_elements

example_who_don = """
New measures to overcome obstacles in responding to the Ebola virus disease (EVD) outbreak in the Democratic
Republic of the Congo are having a positive impact. The Ministry of Health (MoH), WHO and partners continue to be
confident that, despite challenges, the outbreak can be contained. Over the past week (7 – 13 November),
transmission continued in several areas of North Kivu Province, while a geographical expansion of the outbreak to
two new health zones (Kyondo and Mutwanga) was observed (Figure 1).
The first cases reported from these health zones were exposed through contact with cases in Butembo and Beni,
respectively. During the reporting period, 31 new confirmed EVD cases were reported from Beni, Mutwanga, Kalunguta,
Butembo, Vuhovi, Kyondo and Musienene. Four of the new cases were newborn babies and infants aged less than two
years, three were children aged between 2 – 17 years and three were women who were pregnant or breastfeeding. Three
health workers from Beni and Butembo were among the newly infected; 31 health workers have been infected to date.
Twelve additional survivors were discharged from Beni (nine), Butembo (two) and Mabalako (one) Ebola treatment
centres (ETCs) and reintegrated into their communities; 103 patients have recovered to date. During the past week,
a review and reconciliation of case records was conducted. This review resulted in the addition of 14 probable cases
, invalidation of 11 past deaths previously reported as probable cases and exclusion of duplicate cases. In addition
, some confirmed and probable cases were recategorized to health zones where their infection most likely occurred,
as opposed to the location of the ETC where they were admitted. As of 13 November, 341 EVD cases (303 confirmed and
38 probable), including 215 deaths (177 confirmed and 38 probable)1, have been reported in 11 health zones in North
Kivu Province and three health zones in Ituri Province (Figure 1). The overall trends in weekly case incidence
reflect the continuation of community transmission in several cities and villages in North Kivu (Figure 2). Given
the expected delays in case detection and ongoing data reconciliation activities, trends, especially in the most
recent weeks, must be interpreted cautiously. The risk of the outbreak spreading to other provinces in the
Democratic Republic of the Congo, as well as to neighbouring countries, remains very high. Over the course of the
past week, alerts have been reported from South Sudan and Uganda; EVD has been ruled out for all alerts to date. The
 vaccination of health and frontline workers at priority sites in Uganda began on 7 November, and preparations are
 ongoing for the vaccination of health and frontline workers in Rwanda and South Sudan."""

# Not explicitly testing the annotate function, since it only calls EpiTator, and if the object is created, it worked
path = os.path.join("..", "nlp_surveillance", "pickles", "example_who_don_annotated.p")
example_exists = os.path.exists(path)
if not example_exists:
    print("Annotating example text...")
    example_who_don_annotated = annotate(example_who_don)
    del example_who_don_annotated.tiers["spacy.nes"]
    del example_who_don_annotated.tiers["spacy.noun_chunks"]
    del example_who_don_annotated.tiers["spacy.sentences"]
    del example_who_don_annotated.tiers["spacy.tokens"]
    del example_who_don_annotated.tiers["nes"]
    del example_who_don_annotated.tiers["ngrams"]
    del example_who_don_annotated.tiers["tokens"]
    pickle.dump(example_who_don_annotated, open(path, "wb"))
else:
    print("Retrieving saved and annotated example text... ")
    example_who_don_annotated = pickle.load(open(path, "rb"))
    if example_who_don_annotated:
        print("...successfully retrieved. ")
    else:
        print("...retrieve failed. Pickle might be corrupted. Delete example_who_don.p and try again.")


def test_geonames():
    assert geonames(example_who_don_annotated) == Entity(entity='geonames',
                                                         resolved=['Republic of Uganda', 'South Sudan']),\
        "geonames failed"


def test_keywords():
    assert keywords(example_who_don_annotated) == Entity(entity='keywords', resolved=['Ebola hemorrhagic fever']),\
        "keywords failed"

    assert keywords(example_who_don_annotated,
                    with_label=True) == Entity(entity='keywords', resolved=[{
                                                    'id': 'http://purl.obolibrary.org/obo/DOID_4325',
                                                    'label': 'Ebola hemorrhagic fever', 'type': 'disease'}])


def test_cases():
    case_numbers = cases(example_who_don_annotated, raw=True)
    expected_case_numbers = Entity(entity='cases', resolved=[2, 1, 31, 4, 3, 3, 3, 31, 12, 9, 2, 103, 14, 11, 341, 303,
                                                             38, 215, 177, 38, 11, 3, 1, 2])
    assert isinstance(case_numbers, Entity), "Cases has wrong entity"
    assert case_numbers[0] == "cases", "Wrong entity"
    matches = matching_elements(case_numbers[1], expected_case_numbers[1])
    # Assert that majority is correct, since analysis is not deterministic and the test otherwise fails sometimes
    assert len(matches) > int(len(expected_case_numbers[1]) * 0.8)


def test_dates():
    assert dates(example_who_don_annotated) == Entity(entity='dates', resolved=['2018-11-07']), "dates failed"


def test_database_creation():
    print("Testing database creation...")
    database = create_annotated_database(example_who_don, [geonames, (keywords, {"raw": False, "with_label": True})])
    del database["texts"]
    assert database == {'dates': [], 'cases': [], 'keywords': [
        [{'id': 'http://purl.obolibrary.org/obo/DOID_4325', 'label': 'Ebola hemorrhagic fever', 'type': 'disease'}]],
                        'geonames': [['Democratic Republic of the Congo', 'Republic of Uganda', 'South Sudan']]}
