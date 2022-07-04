import streamlit as st
import scraper.quorascraper as qs
import chime


## DynamoDB stuff
import boto3
tableName = "theFieldInclusiveLanguageToolLabelling"

## dynamo functions to refactor

def pull_samples():
    # Get a batch of samples that are not yet labelled
    client = boto3.client('dynamodb')

    indexName = 'labelled'
    response = client.scan(
        ExpressionAttributeValues = {
            ":a": {
                'BOOL': False
            },
        },
        FilterExpression='labelled = :a',
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




items = pull_samples()['Items']



categories = []

with open('categories.txt', 'r') as category_file:
    categories = category_file.read().split('\n') 




try: print(st.session_state.items_i)
except: st.session_state.items_i = 0

# st.markdown(st.session_state.items_i)
# if item_i is None:/

def update_screen():

    string_uid.markdown(f"#### Sentence: {items[item_i]['uniqueID']['S']}")
    string_to_see.markdown(f'>{items[item_i]["sentence"]["S"]}')



with st.form("my_form", clear_on_submit=True):

    item_i = st.session_state.items_i


    string_uid = st.empty()
    string_uid.markdown(f"#### Sentence: {items[item_i]['uniqueID']['S']}")
    
    ## REFERENCE SENTENCE

    # subheader = st.subheader(f'Review sentence #{items[item_i]["uniqueID"]["S"]}')
    string_to_see = st.empty()
    string_to_see.markdown(f'>{items[item_i]["sentence"]["S"]}')

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
        st.session_state.items_i += 1

        # Setup variables for DB
        uniqueId = items[item_i]["uniqueID"]["S"]
        classifications = "".join([categories[i] for i, x in enumerate(category_boxes) if x])
        labelled = True
        sanitisedSentence = text

        update_db(uniqueId, classifications, labelled, sanitisedSentence)
        update_screen()
    if throw:
        st.write("Thanks, sentence thrown away")
        st.session_state.items_i += 1

        uniqueId = items[item_i]["uniqueID"]["S"]
        update_throw(uniqueId)
        update_screen()
    if  review:
        st.write("Sentence has been marked for review")
        st.session_state.items_i += 1

        uniqueId = items[item_i]["uniqueID"]["S"]
        update_mark_for_review(uniqueId)
        update_screen()



