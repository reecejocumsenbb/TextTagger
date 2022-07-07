import streamlit as st
import scraper.quorascraper as qs
import chime

### Functions to reformat

tableName = "theFieldInclusiveLanguageToolLabelling"

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



### DynamoDB Config
import boto3

##### Header etc.
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

chime.theme('material')

st.title("DynamoDB Tagger")

st.markdown("Use this tool to label the provided sentences.")

#### Show update







###### Get DB Samples

test_dict = {'Items': [{'classifications': {'S': '1, 2, 3'}, 'uniqueID': {'S': 'de1e6b7e-32d0-4b88-afad-5b3f6012f3de'}, 'sentence': {'S': 'Besides, they know Nancy Pelosi is not deaf to their concerns'}, 'labelled': {'BOOL': False}, 'sanitisedSentence': {'S': 'Besides, they know Nancy Pelosi is not ignorant to their concerns'}}, {'classifications': {'S': ''}, 'uniqueID': {'S': 'f7159218-e77d-48d5-81f4-582161d931d4'}, 'sentence': {'S': 'Besides, they know Nancy Pelosi is not deaf to their concerns'}, 'labelled': {'BOOL': False}, 'sanitisedSentence': {'S': ''}}], 'Count': 2, 'ScannedCount': 3, 'ResponseMetadata': {'RequestId': 'J7S41PRF6NHRB0B46MS3PN6II7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 04 Jul 2022 11:37:32 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '552', 'connection': 'keep-alive', 'x-amzn-requestid': 'J7S41PRF6NHRB0B46MS3PN6II7VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '188234375'}, 'RetryAttempts': 0}}

# items = test_dict['Items']
data = []

if len(data) == 0:
    if st.button("Get More Samples From DB"):
        out = pull_samples()
        # print(type(out))
        # print(out)
        
        data = out
        items = data['Items']

        st.session_state.items = items

        st.markdown(f'Pulled: {len(items)} unlabelled items') 
        #Reset indices
        # st.session_state.string_i = 0
        # st.session_state.key_i = 0
        st.session_state.items_i = 0



# import pdb; pdb.set_trace()

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

print(type(st.session_state.items))


categories = []

with open('categories.txt', 'r') as category_file:
    categories = category_file.read().split('\n') 



def update_displayed_sentence():
    st.session_state.items_i += 1
    item_i = st.session_state.items_i
    subheader = st.subheader(f'Review sentence #{items[item_i]["uniqueID"]["S"]}')
    string_to_see.markdown(f'{items[item_i]["sentence"]["S"]}')




if st.session_state.items is not None:

    item_i = st.session_state.items_i
    print(item_i)

    items = st.session_state['items']

    # subheader = st.subheader(f'Review sentence #{item_i}, with uniqueId: {items[item_i]["uniqueID"]["S"]}')
    subheader = st.subheader(f'Review sentence #{items[item_i]["uniqueID"]["S"]}')
    string_to_see=st.empty()
    string_to_see.markdown(f'>{items[item_i]["sentence"]["S"]}')




    category_boxes = []

    st.markdown("#### Categorical")   
    for category in categories:
        category_boxes.append(st.checkbox(category, value=False))


    st.markdown("#### Sequence-to-sequence")
    text_to_change = st.empty()
    text = text_to_change.text_area(label="Change the phrasing of this text to something more inclusive.")


    # st.markdown(f'item_i+1: {item_i + 1} > (len(items)-1)): {len(items) - 1}')


    col1, col2, col3 = st.columns((1, 1, 10))

    

    if col1.button("Submit to Database", disabled=(item_i + 1 > (len(items)-1))):
        applied_categories = [categories[i] for i, x in enumerate(category_boxes) if x]
        print(applied_categories)
        print(categories)
        # print(items[item_i]["uniqueID"])
        uniqueID = items[item_i]["uniqueID"]["S"]
        classifications = "".join(applied_categories)
        labelled = True
        sanitisedSentence = text

        # st.markdown(uniqueID)
        # st.markdown(f'classifications: {classifications}')
        # st.markdown(labelled)
        # st.markdown(sanitisedSentence)
        # update_db(
        #     uniqueID,
        #     classifications,
        #     labelled,
        #     sanitisedSentence)

        update_displayed_sentence()
        # st.session_state.items_i += 1
        # subheader.subheader(f'Review sentence #{item_i}')
        # string_to_see.markdown(f'>{items[item_i]["sentence"]["S"]}')


    if col3.button("Throw away Sentence"):

        uniqueID = items[item_i]["uniqueID"]["S"]

        # update_throw(uniqueID)
        update_displayed_sentence()

        #Send to database

        # subheader.subheader()


    
    # if st.button("Submit"):
    #     print("YOOYOYO")
        
    #     st.markdown("#### Output")
    #     st.markdown(str(st.session_state))
    #     applied_categories = [categories[i] for i, x in enumerate(category_boxes) if x]
    #     st.markdown(applied_categories)

    #     st.markdown(text)
    #     print(st.session_state