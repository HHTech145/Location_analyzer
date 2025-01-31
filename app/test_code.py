# import re
# from bs4 import BeautifulSoup

# # Mock HTML for testing
# html = """
# <div class="gt_a gt_f">
#     <p class="gt_b">Mean household income estimate before tax</p>
#     <div data-tile="true" data-round-corner-card="true" class="it_a gt_c">
#         <div class="gt_g">
#             <p data-tile-text="true" class="gt_b">Mean household income estimate before tax</p>
#             <p data-tile-value="true" class="gt_h"><span class="gn_a">£27,600 p/a</span></p>
#         </div>
#         <div data-tile-score="true" class="gt_i"><span class="h2_a">1/10</span></div>
#         <div class="gt_j"></div>
#     </div>
# </div>
# """


# <div class="gt_a gt_f">
#  <div class="it_a gt_c" data-round-corner-card="true" data-tile="true">
#   <div class="gt_g">
#    <p class="gt_h" data-tile-value="true">
#     Qualification LEVEL 4+
#    </p>
#   </div>
#   <div class="gt_i" data-tile-score="true">
#    <span class="h2_a">
#     3/10
#    </span>
#   </div>
#   <div class="gt_j">
#    <span class="iv_a">
#     <svg class="i1_a iv_b" data-icon="true" role="img">
#      <use href="#question-icon" role="presentation" xlink:href="#question-icon">
#      </use>
#     </svg>
#    </span>
#   </div>
#  </div>
# </div>



# # Create BeautifulSoup object
# soup = BeautifulSoup(html, 'html.parser')

# # Function to extract income and rating
# def extract_income_and_rating(soup):
#     try:
#         # Locate the income section
#         income_estimate_section = soup.find('div', class_=re.compile(r'^g.*a.*f$'))
        
#         if income_estimate_section:
#             # Extract the income value
#             income_value_element = income_estimate_section.find('span', class_=re.compile(r'^g.*a$'))
#             income_value = income_value_element.get_text(strip=True) if income_value_element else "No income data found"

#             # Extract the rating
#             income_rating_element = income_estimate_section.find('span', class_=re.compile(r'^h.*a$'))
#             income_rating = income_rating_element.get_text(strip=True) if income_rating_element else "No rating found"

#             return {'income': income_value, 'rating': income_rating}
#         else:
#             print("No income estimate section found!")
#             return {'income': "No income data found", 'rating': "No rating found"}
    
#     except Exception as e:
#         print("Exception occurred:", e)
#         return {'income': "Error occurred", 'rating': "Error occurred"}

# # Test the function
# result = extract_income_and_rating(soup)
# print(result)
