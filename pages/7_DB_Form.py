import streamlit as st
import scraper.quorascraper as qs
import chime


## DynamoDB stuff
import boto3
tableName = "theFieldInclusiveLanguageToolLabelling"

## dynamo functions to refactor
def pull_samples():
    print("PULLING NEW EXAMPLES FROM THE DB")
    # Get a batch of samples that are not yet labelled
    client = boto3.client('dynamodb')

    indexName = 'labelled'
    response = client.scan(
        ExpressionAttributeValues = {
            ":labelled": {
                'BOOL': False
            },
            ":throw": {
                'BOOL': False
            },
            ":review": {
                'BOOL': False
            }
        },
        FilterExpression='labelled = :labelled AND throw = :throw AND review = :review',
        TableName=tableName,
    )

    return response


def update_throw(uniqueID):

    client = boto3.client('dynamodb')
    response = client.update_item(
        TableName=tableName,
        ExpressionAttributeNames = {
            '#throw': 'throw'
        },
        ExpressionAttributeValues = {
            ':throw': {
                'BOOL': True
            }
        },
        Key={
            'uniqueID': {
                'S': uniqueID
            }
        },
        UpdateExpression='SET #throw = :throw'
    )

    return response

def update_mark_for_review(uniqueID):

    client = boto3.client('dynamodb')
    response = client.update_item(
        TableName=tableName,
        ExpressionAttributeNames = {
            '#review': 'review'
        },
        ExpressionAttributeValues = {
            ':review': {
                'BOOL': True
            }
        },
        Key={
            'uniqueID': {
                'S': uniqueID
            }
        },
        UpdateExpression='SET #review = :review'
    )
    return response


def update_db(uniqueID, classifications, labelled, sanitisedSentence):

    client = boto3.client('dynamodb')
    response = client.update_item(
        TableName=tableName,
        ExpressionAttributeNames = {
            '#labelled': 'labelled',
            '#classifications': 'classifications',
            '#sanitisedSentence': 'sanitisedSentence'
        },
        ExpressionAttributeValues = {
            ':labelled': {
                'BOOL': True
            },
            ':classifications': {
                'S': classifications
            },
            ':sanitisedSentence': {
                'S': sanitisedSentence
            },

        },
        Key={
            'uniqueID': {
                'S': uniqueID
            }
        },
        UpdateExpression='SET #labelled = :labelled, #classifications = :classifications, #sanitisedSentence = :sanitisedSentence'
    )
    return response

import random

try: len(st.session_state["items"])
except: 
    out = pull_samples()['Items']
    random.shuffle(out)
    st.session_state["items"] = out



categories = []

with open('categories.txt', 'r') as category_file:
    categories = category_file.read().split('\n') 

try: print(st.session_state.items_i)
except: st.session_state.items_i = 0

def update_screen():

    item_i = st.session_state.items_i
    uniqueIdOut = st.session_state["items"][item_i]['uniqueID']['S']
    print(uniqueIdOut)
    string_uid.markdown(f"#### Sentence: {uniqueIdOut}")
    string_to_see.markdown(f'>{st.session_state["items"][item_i]["sentence"]["S"]}')

st.markdown("#### Instructions")



with st.form("my_form", clear_on_submit=True):

    item_i = st.session_state.items_i

    print('working with item: ' + str(item_i))
    print(st.session_state["items"][item_i])
    print('___')

    string_uid = st.empty()
    uniqueIdOut = st.session_state["items"][item_i]['uniqueID']['S']
    string_uid.markdown(f"#### Sentence: {uniqueIdOut}")
    
    ## REFERENCE SENTENCE

    # subheader = st.subheader(f'Review sentence #{items[item_i]["uniqueID"]["S"]}')
    string_to_see = st.empty()
    string_to_see.markdown(f'>{st.session_state["items"][item_i]["sentence"]["S"]}')

    ## CHECK-BOXES
    st.markdown("#### Classification categories")
    category_boxes = []
    for category in categories:
        category_boxes.append(st.checkbox(category, value=False))


    ## TEXT BOX
    st.markdown("#### Sequence-to-sequence")
    text_to_change = st.empty()
    text = text_to_change.text_area(label="Change the phrasing of this text to something more inclusive.")


    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit Labels to DB")
    throw = st.form_submit_button("Throw Sentence Away")
    review = st.form_submit_button("Mark Sentence for Review")

    if submitted:
        st.write("Thank you! Database has been updated")

        # Setup variables for DB
        uniqueId = st.session_state["items"][item_i]["uniqueID"]["S"]
        print(f'updating {uniqueId} in the database')
        classifications = ",".join([categories[i] for i, x in enumerate(category_boxes) if x])
        labelled = True
        sanitisedSentence = text

        response = update_db(uniqueId, classifications, labelled, sanitisedSentence)
        # print(response)
        st.session_state.items_i += 1
        update_screen()

    if throw:
        st.write("Thanks, sentence thrown away")

        uniqueId = st.session_state["items"][item_i]["uniqueID"]["S"]
        print(f'updating {uniqueId} in the database')
        response = update_throw(uniqueId)
        # print(response)
        st.session_state.items_i += 1
        update_screen()

    if  review:
        st.write("Sentence has been marked for review")

        uniqueId = st.session_state["items"][item_i]["uniqueID"]["S"]
        print(f'updating {uniqueId} in the database')
        response = update_mark_for_review(uniqueId)
        # print(response)
        st.session_state.items_i += 1
        update_screen()