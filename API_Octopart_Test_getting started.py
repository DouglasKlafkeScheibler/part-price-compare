from six.moves import urllib
import json
import pandas as pd
import numpy as np

# copy pasted from: https://github.com/prisma-labs/python-graphql-client/blob/master/graphqlclient/client.py
class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None
        self.headername = None

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def inject_token(self, token, headername='token'):
        self.token = token
        self.headername = headername

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        req = urllib.request.Request(self.endpoint, json.dumps(data).encode('utf-8'), headers)

        try:
            response = urllib.request.urlopen(req)
            return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e

def get_parts(client, ids):
    query = '''
    query get_parts($ids: [String!]!) {
        parts(ids: $ids) {
            id
            manufacturer {
                name
            }
            mpn
        }
    }
    '''

    ids = [str(id) for id in ids]
    resp = client.execute(query, {'ids': ids})
    return json.loads(resp)['data']['parts']

def match_mpns(client, mpns):
    dsl = '''
    query match_mpns($queries: [PartMatchQuery!]!) {
        multi_match(queries: $queries) {
            hits
            parts {
                mpn
                sellers(authorized_only: true){
                    company{
                        name
                    }
                    offers{
                        inventory_level
                        prices{
                            price
                            quantity
                        }
                    }
                }
            }
        }
    }
    '''

    queries = []
    for mpn in mpns:
        queries.append({
            'mpn_or_sku': mpn,
            'start': 0,
            'limit': 5,
            'reference': mpn,
        })
    resp = client.execute(dsl, {'queries': queries})
    return json.loads(resp)['data']['multi_match']

def demo_part_get(client):
    print('\n---------------- demo_part_get')
    ids = ["1", "2", "asdf", "4"]
    parts = get_parts(client, ids)

    for id, part in zip(ids, parts):
        print(id, '\t', part)

def demo_match_mpns(client, mpns, quantity_BOM = 300):
    print('\n---------------- demo_match_mpns')
    
    matches = match_mpns(client, mpns)

    distributor_selections = []
    for match in matches:
        print(match)
        for part in match['parts']:
            for sellers in part['sellers']:
                distributor_name = sellers['company']['name']
                if( distributor_name == "Digi-Key" or 
                    distributor_name == 'Mouser' or 
                    distributor_name == 'Arrow Electronics'):
                    print("***********")
                    print("Fornecedor")
                    for offer in sellers['offers']:
                        distributor_prices = []
                        best_price = 0
                        stock = offer['inventory_level']
                        if(quantity_BOM <= stock):
                            for price in offer['prices']:
                                if(quantity_BOM > price['quantity']):
                                    best_price = price['price']
                    
                            distributor_prices.append(distributor_name)
                            distributor_prices.append(best_price)
                            distributor_prices.append(stock)
                        distributor_selections.append(distributor_prices)
                        print(distributor_selections)
    df_raw = pd.DataFrame(distributor_selections, columns=['Distribuidor', 'Preço', 'Estoque'])
    df_withoutNA = df_raw.dropna()
    final_df = df_withoutNA.drop_duplicates()
    print(final_df)


def reading_BOM():
    data = pd.read_excel(r'octo -Mapa 1.xlsx')
    data_raw = data.to_dict('split')
    BOM_data = np.array(data_raw["data"])
    fist_item = [[data.keys()[0],data.keys()[1]]]

    final_BOM_data = np.concatenate((fist_item, BOM_data), axis=0)

    return final_BOM_data[19]

def getting_data_octo(client, BOM_data):
    # for item in BOM_data:
    demo_match_mpns(client, BOM_data[0], float(BOM_data[1]))



if __name__ == '__main__':
    client = GraphQLClient('https://octopart.com/api/v4/endpoint')
    client.inject_token('6db6bc8e-c90b-48bd-90be-1f041fdd2e1b') #32723278-289c-4992-bfaa-b2ec91329f7b
    BOM_data = reading_BOM()
    getting_data_octo(client, BOM_data)
    # demo_part_get(client)
    