from gql import gql, Client


class GQLQuery:
    def __init__(self, transport):
        self.transport = transport
        self.client = Client(transport=transport)

    def make_request(self, query_string):
        response = self.client.execute(gql(query_string))
        return response
