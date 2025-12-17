import unittest
from unittest import mock
import asyncio
from pyluga.responses import PaginatedResponse
from pyluga.async_api_client import AsyncBelugaClient

class AsyncPaginationTests(unittest.TestCase):

    def test_async_iteration(self):
        async def run_test():
            # Mock client and api_request
            client = mock.Mock(spec=AsyncBelugaClient)
            # api_request must return a coroutine
            client._api_request = mock.AsyncMock()
            
            # Setup first page data
            data = {
                'data': [{'id': 1}],
                'meta': {
                    'pagination': {
                        'total': 2,
                        'links': {'next': 'http://next'}
                    }
                }
            }
            
            # Setup second page response
            second_page_response = {
                'data': [{'id': 2}],
                'meta': {
                    'pagination': {
                        'total': 2,
                        'links': {'next': ''}
                    }
                }
            }
            
            client._api_request.return_value = second_page_response
            
            paginated = PaginatedResponse(client, 'endpoint', data)
            
            items = []
            async for page in paginated:
                items.extend(page.data)
                
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]['id'], 1)
            self.assertEqual(items[1]['id'], 2)
            
        asyncio.run(run_test())

    def test_collect_async(self):
        async def run_test():
            client = mock.Mock(spec=AsyncBelugaClient)
            client._api_request = mock.AsyncMock()
            
            data = {
                'data': [{'id': 1}],
                'meta': {
                    'pagination': {
                        'total': 2,
                        'links': {'next': 'http://next'}
                    }
                }
            }
             
            second_page_response = {
                'data': [{'id': 2}],
                'meta': {
                    'pagination': {
                        'total': 2,
                        'links': {'next': ''}
                    }
                }
            }
            
            client._api_request.return_value = second_page_response
            
            paginated = PaginatedResponse(client, 'endpoint', data)
            
            items = await paginated.collect_async()
            
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]['id'], 1)
            self.assertEqual(items[1]['id'], 2)

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
