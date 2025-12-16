#!/usr/bin/env python3
"""Test script for Webfuse SDK"""

import os
from webfuse import WebfuseClient

# Initialize client - use environment variables
api_key = os.environ.get('WEBFUSE_API_KEY')
space_id = os.environ.get('WEBFUSE_SPACE_ID')

if not api_key or not space_id:
    print('Please set WEBFUSE_API_KEY and WEBFUSE_SPACE_ID environment variables')
    print('Example:')
    print('  export WEBFUSE_API_KEY=rk_your_api_key')
    print('  export WEBFUSE_SPACE_ID=1234')
    exit(1)

client = WebfuseClient(api_key=api_key, space_id=space_id)

print('Creating session...')
session = client.create_session()
print(f'Session ID: {session.session_id}')
print(f'Link: {session.link}')

print('\n>>> Open this link in a browser, then press Enter to continue...')
input()

print('\nTesting automation...')

# Navigate to a page
print('1. Navigating to example.com...')
try:
    result = session.goto('https://example.com')
    print(f'   Result: {result}')
except Exception as e:
    print(f'   Error: {e}')

# Wait for page to load
print('2. Waiting 2 seconds...')
try:
    session.wait(2000)
    print('   Done waiting')
except Exception as e:
    print(f'   Error: {e}')

# Take a DOM snapshot
print('3. Taking DOM snapshot...')
try:
    dom = session.dom_snapshot()
    print(f'   DOM length: {len(dom)} chars')
    print(f'   Preview: {dom[:200]}...')
except Exception as e:
    print(f'   Error: {e}')

# End the session
print('\n4. Ending session...')
try:
    session.end()
    print('   Session ended')
except Exception as e:
    print(f'   Error: {e}')

client.close()
print('\nTest complete!')
