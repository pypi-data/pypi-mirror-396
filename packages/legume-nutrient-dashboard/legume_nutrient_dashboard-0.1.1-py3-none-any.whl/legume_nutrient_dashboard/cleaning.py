import requests
import re
import pandas as pd


def read_api_key():
    """This function will open and read the api.txt
    file and create an api_key object to pass into
    the API call query. An API key is returned"""
    with open('api.txt') as file:
        api_key = file.read().strip()
    return api_key


def call_api(api_key):
    """This function will call the API by using a unique
    API key from the function above. It returns a rows of JSON
    that get appended to an emty list. A list of rows is returned."""
    query = "\"Legumes and Legume Products\""
    legus = []
    for page in range(1,6):
        url = f'https://api.nal.usda.gov/fdc/v1/foods/list?api_key={api_key}&query={query}&pageNumber={page}'
        response = requests.get(url)
        legu_rows = response.json()
        legus.extend(legu_rows)
    return legus


def create_df(legus):
    """This function will take the list of data rows and create
    a pandas data frame. It also filters the 'dataType' to just
    'Foundation foods' which we will be using in our analysis. A
    novel data frame with a reset index is returned."""
    legusdf = pd.DataFrame(legus)
    legusdf = legusdf[legusdf["dataType"] == "Foundation"]
    legusdf = legusdf.reset_index(drop = True)
    return legusdf


def extract_nutrient(nutrient_list, target):
    """This function will help us unpack the large tuples
    stored in the 'foodNutrients' column of our data set to
    extract certain nutrients and their amounts per 100g sample.
    Nothing is returned in this function."""
    if nutrient_list is None:
        return None
    if len(nutrient_list) == 0:
        return None
    for nutrient in nutrient_list:
        if nutrient.get('name') == target:
            return nutrient.get("amount")
    return None


def nutrient_cols(legusdf):
    """This function will create unique nutrient columns that
    are unpacked using the extract_nutrient() function.
    Legusdf is returned."""
    legusdf["Water (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Water"))
    legusdf["Calories (kcal)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Energy (Atwater General Factors)"))
    legusdf["Nitrogen (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Nitrogen"))
    legusdf["Protein (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Protein"))
    legusdf["Fat (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Total lipid (fat)"))
    legusdf["Ash (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Ash"))
    legusdf["Carbs (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Carbohydrate, by difference"))
    legusdf["Starch (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Starch"))
    legusdf["Resistant starch (g)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Resistant starch"))
    legusdf["Calcium (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Calcium, Ca"))
    legusdf["Iron (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Iron, Fe"))
    legusdf["Magnesium (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Magnesium, Mg"))
    legusdf["Phosphorus (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Phosphorus, P"))
    legusdf["Potassium (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Potassium, K"))
    legusdf["Sodium (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Sodium, Na"))
    legusdf["Zinc (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Zinc, Zn"))
    legusdf["Copper (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Copper, Cu"))
    legusdf["Manganese (mg)"] = legusdf['foodNutrients'].apply(lambda items: extract_nutrient(items, "Manganese, Mn"))
    return legusdf


def clean_cols(legusdf):
    """This function will fill any Nan values with zeros and round
    decimal places to two decimal places. Legusdf is returned."""
    legusdf = legusdf.fillna(0.0)
    legusdf = legusdf.round(2)
    return legusdf


def categorize(legusdf):
    """This function will use latex (regex??) to split the 'description'
    column into two disticnt columns of 'Category' and 'Type' for
    better organization. Legusdf is returned."""
    legusdf['Category'] = legusdf["description"].str.extract(r'^(.*?),')
    legusdf['Type'] = legusdf["description"].str.extract(r',\s*(.*)')
    return legusdf


def reorder_df(legusdf):
    legusdf = legusdf[[
    "fdcId",
    "Category",
    "Type",
    "description",
    "Water (g)",
    "dataType",
    "publicationDate",
    "ndbNumber",
    "foodNutrients",
    "Calories (kcal)",
    "Nitrogen (g)",
    "Protein (g)",
    "Fat (g)",
    "Ash (g)",
    "Carbs (g)",
    "Starch (g)",
    "Resistant starch (g)",
    "Iron (mg)",
    "Magnesium (mg)",
    "Phosphorus (mg)",
    "Potassium (mg)",
    "Sodium (mg)",
    "Zinc (mg)",
    "Copper (mg)",
    "Manganese (mg)"
]]
    return legusdf


def drop_unsedcols(legusdf):
    legusdf = legusdf.drop(columns = ["fdcId", "description", "dataType", "ndbNumber", "foodNutrients", "publicationDate"])
    return legusdf
