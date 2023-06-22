# Import necessary libraries
from flask import Flask, jsonify, request
import pandas as pd
import Levenshtein
import json

# Create a Flask app instance
app = Flask(__name__)

# Define the homepage route and functionality
@app.route('/', methods=['POST'])
def homepage():
  # Get the JSON data from the request
  data = request.get_json()
  # Extract the available matchers and target from the JSON data
  available_matchers = data['availableMatchers']
  target = data['target'].lower()
  # Initialize an empty list to store the results
  result = []

  # Loop through each matcher in the available matchers
  for matcher in available_matchers:
    # Extract the marketplace and items from the matcher
    marketplace = matcher['marketplace']  
    items = matcher['items']
    # Initialize variables to track whether a match was found and what item was matched
    matched_item = None
    success = False

    # First, try to find an exact match between the lowercase version of the item name and the target
    for item in items:
      if item['name'].lower() == target:
        matched_item = item
        success = True
        break

    # If no exact match is found, use the Levenshtein ratio calculation to find a close match
    if not matched_item:
      max_ratio = 0
      for item in items:
        ratio = Levenshtein.ratio(item['name'].lower(), target)
        if ratio > 0.8 and ratio > max_ratio: # set a threshold of 0.8 for Levenshtein ratio
          max_ratio = ratio
          matched_item = item
          success = True

    # If still no match is found, split the target and the marketplace brands and suggest a brand inside "item" that match the first word
    if not matched_item:
      for item in items:
        ratio = Levenshtein.ratio(target.split()[0], item['name'].lower())
        if len(target.split()) > 1 and ratio > 0.8:
          matched_item = item
          success = True
          break

    # Append the result of this matcher to the overall results list
    result.append({
      'marketplace': marketplace,
      'success': success,
      'matchedItem': matched_item
    })
  
  # Return the results as a JSON object
  return jsonify(result)

# Run the Flask app
app.run(host='0.0.0.0')