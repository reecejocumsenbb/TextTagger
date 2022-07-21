import streamlit as st
import scraper.quorascraper as qs
import chime
import datetime

## DynamoDB stuff
import boto3

#number of datapoints that need to be obtained
NUM_ENTRIES = 3000
tableName = "theFieldInclusiveLanguageToolLabelling"


## dynamo functions to refactor
def pull_samples():
    print("PULLING NEW EXAMPLES FROM THE DB")
    # Get a batch of samples that are not yet labelled
    client = boto3.client('dynamodb',region_name = 'ap-southeast-2',aws_access_key_id=st.secrets["ACCESS_ID"],aws_secret_access_key=st.secrets["ACCESS_KEY"])


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

    client = boto3.client('dynamodb',region_name = 'ap-southeast-2',aws_access_key_id=st.secrets["ACCESS_ID"],aws_secret_access_key=st.secrets["ACCESS_KEY"])

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

    client = boto3.client('dynamodb',region_name = 'ap-southeast-2',aws_access_key_id=st.secrets["ACCESS_ID"],aws_secret_access_key=st.secrets["ACCESS_KEY"])

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


def update_db(uniqueID, classifications, labelled, sanitisedSentence,uploader):

    client = boto3.client('dynamodb',region_name = 'ap-southeast-2',aws_access_key_id=st.secrets["ACCESS_ID"],aws_secret_access_key=st.secrets["ACCESS_KEY"])
    upload_datetime = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    response = client.update_item(
        TableName=tableName,
        ExpressionAttributeNames = {
            '#labelled': 'labelled',
            '#classifications': 'classifications',
            '#sanitisedSentence': 'sanitisedSentence',
            '#datetime': 'datetime',
            '#uploader': 'uploader'
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
            ':datetime': {
                'S': upload_datetime
            },
            ':uploader': {
                'S': uploader
            }
        },
        Key={
            'uniqueID': {
                'S': uniqueID
            }
        },
        UpdateExpression='SET #labelled = :labelled, #classifications = :classifications, #sanitisedSentence = :sanitisedSentence, #datetime = :datetime, #uploader = :uploader'
    )
    return response

def get_labelled_entries():
    print("PULLING NEW EXAMPLES FROM THE DB")
    # Get a batch of samples that are not yet labelled
    client = boto3.client('dynamodb',region_name = 'ap-southeast-2',aws_access_key_id=st.secrets["ACCESS_ID"],aws_secret_access_key=st.secrets["ACCESS_KEY"])

    response = client.scan(
        ExpressionAttributeValues = {
            ":labelled": {
                'BOOL': True
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



import random

try: len(st.session_state["items"])
except: 
    out = pull_samples()['Items']

    random.shuffle(out)
    st.session_state["items"] = out


out_labelled = get_labelled_entries()['Items']
num_labelled = len(out_labelled)
categories = []
uploader = 'undefined'
with open('categories.txt', 'r') as category_file:
    categories = category_file.read().split('\n') 

try: print(st.session_state.items_i)
except: st.session_state.items_i = 0

def update_screen():
    
    item_i = st.session_state.items_i
    uniqueIdOut = st.session_state["items"][item_i]['uniqueID']['S']
    # get new number of labelled tags
    out_labelled = get_labelled_entries()['Items']
    num_labelled = len(out_labelled)

    print(uniqueIdOut)
    string_uid.markdown(f"#### Sentence: {uniqueIdOut}")
    string_to_see.markdown(f'>{st.session_state["items"][item_i]["sentence"]["S"]}')
    progress_status.markdown(f"#### Progress: {num_labelled} / {NUM_ENTRIES}")

st.markdown("#### Instructions")


with st.form("name_form",clear_on_submit = False):
    st.markdown("#### Set Your Name:")
    name_text = st.empty()
    name = name_text.text_area(label="Please type your name here")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Set Name")
    if submitted:
        if not name.isspace():
            uploader = name 

with st.form("my_form", clear_on_submit=True):

    item_i = st.session_state.items_i

    print('working with item: ' + str(item_i))
    print(st.session_state["items"][item_i])
    print('___')
    
    # Progress bar
    progress_status = st.empty()
    progress_status.markdown(f"#### Progress: {num_labelled} / {NUM_ENTRIES}")

    progress = st.progress(num_labelled/NUM_ENTRIES)
    
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
        sanitisedSentence = text if not text.isspace() else st.session_state["items"][item_i]["sentence"]["S"]

        response = update_db(uniqueId, classifications, labelled, sanitisedSentence, uploader)
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