# Sustainabytes Data Analysis

This repository contains the code and documentation used in the data analysis of our
**CS132 Project: Sustainabytes**.

More information can be found at our [dedicated website](https://prebollido.github.io/sustainabytes/).

## Feature Description: Food Prices Dataset (Raw)

### 1. Temporal

Features related to time periods and temporal indexing.

- `DATES`: full timestamp of observation (datetime format: `YYYY-MM-DD HH:MM:SS+TZ`)
- `year`: year of observation (integer: 2007-2025)
- `month`: month of observation (integer: 1-12)"
- `start_dense_data`: the earliest date for the entire dataset
  - all rows are "Jan 2007"
- `last_survey_point`: the most recent date for the entire dataset
  - all rows are "Sep 2025"

### 2. Geographic

Features identifying location and spatial characteristics.

- `ISO3`: three-letter country code
  - all rows are "PHL" for Philippines
- `country`: full country name
  - all rows are "Philippines"
- `adm1_name`: region (e.g. "Cordillera Administrative Region")
- `adm2_name`: province (e.g. "Abra")
- `mkt_name`: market - specific location name associated with the datapoint; can be cities, barangays, or municipalities within the province
- `lat`: latitude coordinate
- `lon`: longitude coordinate
- `geo_id`: unique geographic identifier for each market location

Coverage: 1 country, 18 regions, 109 markets across the Philippines

### 3. Metadata & Quality

Features providing context about data collection and reliability.

- `currency`: currency used for price values
  - all rows are "PHP" for Philippine Peso
- `components`: list of food items tracked at this market with their units and index weights (e.g. "beans (1 KG, Index Weight = 1)")
  - all rows have the same value: each food item is (1 KG, Index Weight = 1)
- `data_coverage`: overall percentage of data completeness across all time periods
  - all rows are "20.71"
- `data_coverage_recent`: percentage of data completeness for recent periods
  - all rows are "40.18"
- `index_confidence_score`: confidence score for the aggregate food price index (0-1 scale)
  - all rows are "0.98"
- `spatially_interpolated`: boolean flag (0 or 1) indicating whether  spatial interpolation was used
  - 0: prices that are directly measured or estimated for a specific location
  - 1: indicates that the price has been calculated using an inverse distance weighted interpolation method, based on data and estimates from nearby market locations
  - all rows are "0"

### 4. Base Food Price

There are 73 base food features representing the price for each food item. Base values represent the **actual raw survey data** collected at specific market and times.

The base columns are mostly sparse (high percentage of missing values).

```python
['apples', 'bananas', 'beans', 'bread', 'bulgur', 'cabbage', 'carrots', 'cassava', 'cassava_flour', 'cassava_meal', 'cheese', 'chickpeas', 'chili', 'coffee_instant', 'couscous', 'cowpeas', 'cucumbers', 'dates', 'eggplants', 'eggs', 'fish', 'fish_catfish', 'fish_mackerel', 'fish_sardine_canned', 'fish_tilapia', 'fish_tuna_canned', 'fonio', 'garlic', 'groundnuts', 'lentils', 'livestock_sheep_two_year_old_male', 'livestockgoat_castrated_male', 'livestocksheep_castrated_male', 'maize', 'maize_flour', 'maize_meal', 'meat_beef', 'meat_beef_chops', 'meat_beef_minced', 'meat_buffalo', 'meat_chicken', 'meat_chicken_broiler', 'meat_chicken_plucked', 'meat_chicken_whole', 'meat_goat', 'meat_lamb', 'meat_pork', 'milk', 'millet', 'oil', 'onions', 'oranges', 'parsley', 'pasta', 'peas', 'potatoes', 'pulses', 'rice', 'rice_various', 'salt', 'sesame', 'sorghum', 'sorghum_food_aid', 'spinach', 'sugar', 'tea', 'tomatoes', 'tomatoes_paste', 'watermelons', 'wheat', 'wheat_flour', 'yam', 'yogurt']
```

### 5. Derived Food Price

For each base food item, there are derived metric features. Derived values are **aggregated/interpolated values** from multiple raw observations.

- `o_[food_item]` - monthly opening price estimate: represents the initial market price at the start of each month
- `h_[food_item]` - monthly highest price achieved: captures market peaks, reflecting the maximum demand or valuation during the period
- `l_[food_item]` - monthly lowest price point: essential for understanding market dips, buyer interest at lower prices, and the floor value of the commodity
- `c_[food_item]` - monthly closing price estimate: reflects the closing market sentiment and valuation after a month's trading activity
- `inflation_[food_item]` - 12-month inflation rate: (also called price change rate) calculated by comparing the current price against the price from 12 months prior, giving an annualized percentage change.
- `trust_[food_item]` - trust score: ranging from 1-10, reflects the reliability of the inflation calculation for the food item; higher scores indicate greater confidence and robustness in the inflation figures

### 6. Derived Food Price Index

For each derived metric, there are also indexes. An index is the aggregate value for all food items under the respective metric. It uses a weighted average based on the `components` column.

- `o_food_price_index`
- `h_food_price_index`
- `l_food_price_index`
- `c_food_price_index`
- `inflation_food_price_index`
- `trust_food_price_index`

```python
'open':
  ['o_apples', 'o_bananas', 'o_beans', 'o_bread', 'o_bulgur', 'o_cabbage', 'o_carrots', 'o_cassava', 'o_cassava_flour', 'o_cassava_meal', 'o_cheese', 'o_chickpeas', 'o_chili', 'o_coffee_instant', 'o_couscous', 'o_cowpeas', 'o_cucumbers', 'o_dates', 'o_eggplants', 'o_eggs', 'o_fish', 'o_fish_catfish', 'o_fish_mackerel', 'o_fish_sardine_canned', 'o_fish_tilapia', 'o_fish_tuna_canned', 'o_fonio', 'o_garlic', 'o_groundnuts', 'o_lentils', 'o_livestock_sheep_two_year_old_male', 'o_livestockgoat_castrated_male', 'o_livestocksheep_castrated_male', 'o_maize', 'o_maize_flour', 'o_maize_meal', 'o_meat_beef', 'o_meat_beef_chops', 'o_meat_beef_minced', 'o_meat_buffalo', 'o_meat_chicken', 'o_meat_chicken_broiler', 'o_meat_chicken_plucked', 'o_meat_chicken_whole', 'o_meat_goat', 'o_meat_lamb', 'o_meat_pork', 'o_milk', 'o_millet', 'o_oil', 'o_onions', 'o_oranges', 'o_parsley', 'o_pasta', 'o_peas', 'o_potatoes', 'o_pulses', 'o_rice', 'o_rice_various', 'o_salt', 'o_sesame', 'o_sorghum', 'o_sorghum_food_aid', 'o_spinach', 'o_sugar', 'o_tea', 'o_tomatoes', 'o_tomatoes_paste', 'o_watermelons', 'o_wheat', 'o_wheat_flour', 'o_yam', 'o_yogurt', 'o_food_price_index'],

'high':
    ['h_apples', 'h_bananas', 'h_beans', 'h_bread', 'h_bulgur', 'h_cabbage', 'h_carrots', 'h_cassava', 'h_cassava_flour', 'h_cassava_meal', 'h_cheese', 'h_chickpeas', 'h_chili', 'h_coffee_instant', 'h_couscous', 'h_cowpeas', 'h_cucumbers', 'h_dates', 'h_eggplants', 'h_eggs', 'h_fish', 'h_fish_catfish', 'h_fish_mackerel', 'h_fish_sardine_canned', 'h_fish_tilapia', 'h_fish_tuna_canned', 'h_fonio', 'h_garlic', 'h_groundnuts', 'h_lentils', 'h_livestock_sheep_two_year_old_male', 'h_livestockgoat_castrated_male', 'h_livestocksheep_castrated_male', 'h_maize', 'h_maize_flour', 'h_maize_meal', 'h_meat_beef', 'h_meat_beef_chops', 'h_meat_beef_minced', 'h_meat_buffalo', 'h_meat_chicken', 'h_meat_chicken_broiler', 'h_meat_chicken_plucked', 'h_meat_chicken_whole', 'h_meat_goat', 'h_meat_lamb', 'h_meat_pork', 'h_milk', 'h_millet', 'h_oil', 'h_onions', 'h_oranges', 'h_parsley', 'h_pasta', 'h_peas', 'h_potatoes', 'h_pulses', 'h_rice', 'h_rice_various', 'h_salt', 'h_sesame', 'h_sorghum', 'h_sorghum_food_aid', 'h_spinach', 'h_sugar', 'h_tea', 'h_tomatoes', 'h_tomatoes_paste', 'h_watermelons', 'h_wheat', 'h_wheat_flour', 'h_yam', 'h_yogurt', 'h_food_price_index'],

'low':
    ['l_apples', 'l_bananas', 'l_beans', 'l_bread', 'l_bulgur', 'l_cabbage', 'l_carrots', 'l_cassava', 'l_cassava_flour', 'l_cassava_meal', 'l_cheese', 'l_chickpeas', 'l_chili', 'l_coffee_instant', 'l_couscous', 'l_cowpeas', 'l_cucumbers', 'l_dates', 'l_eggplants', 'l_eggs', 'l_fish', 'l_fish_catfish', 'l_fish_mackerel', 'l_fish_sardine_canned', 'l_fish_tilapia', 'l_fish_tuna_canned', 'l_fonio', 'l_garlic', 'l_groundnuts', 'l_lentils', 'l_livestock_sheep_two_year_old_male', 'l_livestockgoat_castrated_male', 'l_livestocksheep_castrated_male', 'l_maize', 'l_maize_flour', 'l_maize_meal', 'l_meat_beef', 'l_meat_beef_chops', 'l_meat_beef_minced', 'l_meat_buffalo', 'l_meat_chicken', 'l_meat_chicken_broiler', 'l_meat_chicken_plucked', 'l_meat_chicken_whole', 'l_meat_goat', 'l_meat_lamb', 'l_meat_pork', 'l_milk', 'l_millet', 'l_oil', 'l_onions', 'l_oranges', 'l_parsley', 'l_pasta', 'l_peas', 'l_potatoes', 'l_pulses', 'l_rice', 'l_rice_various', 'l_salt', 'l_sesame', 'l_sorghum', 'l_sorghum_food_aid', 'l_spinach', 'l_sugar', 'l_tea', 'l_tomatoes', 'l_tomatoes_paste', 'l_watermelons', 'l_wheat', 'l_wheat_flour', 'l_yam', 'l_yogurt', 'l_food_price_index'],

'close': 
    ['c_apples', 'c_bananas', 'c_beans', 'c_bread', 'c_bulgur', 'c_cabbage', 'c_carrots', 'c_cassava', 'c_cassava_flour', 'c_cassava_meal', 'c_cheese', 'c_chickpeas', 'c_chili', 'c_coffee_instant', 'c_couscous', 'c_cowpeas', 'c_cucumbers', 'c_dates', 'c_eggplants', 'c_eggs', 'c_fish', 'c_fish_catfish', 'c_fish_mackerel', 'c_fish_sardine_canned', 'c_fish_tilapia', 'c_fish_tuna_canned', 'c_fonio', 'c_garlic', 'c_groundnuts', 'c_lentils', 'c_livestock_sheep_two_year_old_male', 'c_livestockgoat_castrated_male', 'c_livestocksheep_castrated_male', 'c_maize', 'c_maize_flour', 'c_maize_meal', 'c_meat_beef', 'c_meat_beef_chops', 'c_meat_beef_minced', 'c_meat_buffalo', 'c_meat_chicken', 'c_meat_chicken_broiler', 'c_meat_chicken_plucked', 'c_meat_chicken_whole', 'c_meat_goat', 'c_meat_lamb', 'c_meat_pork', 'c_milk', 'c_millet', 'c_oil', 'c_onions', 'c_oranges', 'c_parsley', 'c_pasta', 'c_peas', 'c_potatoes', 'c_pulses', 'c_rice', 'c_rice_various', 'c_salt', 'c_sesame', 'c_sorghum', 'c_sorghum_food_aid', 'c_spinach', 'c_sugar', 'c_tea', 'c_tomatoes', 'c_tomatoes_paste', 'c_watermelons', 'c_wheat', 'c_wheat_flour', 'c_yam', 'c_yogurt', 'c_food_price_index'],

'inflation': 
    ['inflation_apples', 'inflation_bananas', 'inflation_beans', 'inflation_bread', 'inflation_bulgur', 'inflation_cabbage', 'inflation_carrots', 'inflation_cassava', 'inflation_cassava_flour', 'inflation_cassava_meal', 'inflation_cheese', 'inflation_chickpeas', 'inflation_chili', 'inflation_coffee_instant', 'inflation_couscous', 'inflation_cowpeas', 'inflation_cucumbers', 'inflation_dates', 'inflation_eggplants', 'inflation_eggs', 'inflation_fish', 'inflation_fish_catfish', 'inflation_fish_mackerel', 'inflation_fish_sardine_canned', 'inflation_fish_tilapia', 'inflation_fish_tuna_canned', 'inflation_fonio', 'inflation_garlic', 'inflation_groundnuts', 'inflation_lentils', 'inflation_livestock_sheep_two_year_old_male', 'inflation_livestockgoat_castrated_male', 'inflation_livestocksheep_castrated_male', 'inflation_maize', 'inflation_maize_flour', 'inflation_maize_meal', 'inflation_meat_beef', 'inflation_meat_beef_chops', 'inflation_meat_beef_minced', 'inflation_meat_buffalo', 'inflation_meat_chicken', 'inflation_meat_chicken_broiler', 'inflation_meat_chicken_plucked', 'inflation_meat_chicken_whole', 'inflation_meat_goat', 'inflation_meat_lamb', 'inflation_meat_pork', 'inflation_milk', 'inflation_millet', 'inflation_oil', 'inflation_onions', 'inflation_oranges', 'inflation_parsley', 'inflation_pasta', 'inflation_peas', 'inflation_potatoes', 'inflation_pulses', 'inflation_rice', 'inflation_rice_various', 'inflation_salt', 'inflation_sesame', 'inflation_sorghum', 'inflation_sorghum_food_aid', 'inflation_spinach', 'inflation_sugar', 'inflation_tea', 'inflation_tomatoes', 'inflation_tomatoes_paste', 'inflation_watermelons', 'inflation_wheat', 'inflation_wheat_flour', 'inflation_yam', 'inflation_yogurt', 'inflation_food_price_index'],

'trust':
    ['trust_apples', 'trust_bananas', 'trust_beans', 'trust_bread', 'trust_bulgur', 'trust_cabbage', 'trust_carrots', 'trust_cassava', 'trust_cassava_flour', 'trust_cassava_meal', 'trust_cheese', 'trust_chickpeas', 'trust_chili', 'trust_coffee_instant', 'trust_couscous', 'trust_cowpeas', 'trust_cucumbers', 'trust_dates', 'trust_eggplants', 'trust_eggs', 'trust_fish', 'trust_fish_catfish', 'trust_fish_mackerel', 'trust_fish_sardine_canned', 'trust_fish_tilapia', 'trust_fish_tuna_canned', 'trust_fonio', 'trust_garlic', 'trust_groundnuts', 'trust_lentils', 'trust_livestock_sheep_two_year_old_male', 'trust_livestockgoat_castrated_male', 'trust_livestocksheep_castrated_male', 'trust_maize', 'trust_maize_flour', 'trust_maize_meal', 'trust_meat_beef', 'trust_meat_beef_chops', 'trust_meat_beef_minced', 'trust_meat_buffalo', 'trust_meat_chicken', 'trust_meat_chicken_broiler', 'trust_meat_chicken_plucked', 'trust_meat_chicken_whole', 'trust_meat_goat', 'trust_meat_lamb', 'trust_meat_pork', 'trust_milk', 'trust_millet', 'trust_oil', 'trust_onions', 'trust_oranges', 'trust_parsley', 'trust_pasta', 'trust_peas', 'trust_potatoes', 'trust_pulses', 'trust_rice', 'trust_rice_various', 'trust_salt', 'trust_sesame', 'trust_sorghum', 'trust_sorghum_food_aid', 'trust_spinach', 'trust_sugar', 'trust_tea', 'trust_tomatoes', 'trust_tomatoes_paste', 'trust_watermelons', 'trust_wheat', 'trust_wheat_flour', 'trust_yam', 'trust_yogurt', 'trust_food_price_index']}
```

## Sources

- [Data schema for food price dataset](https://microdata.worldbank.org/index.php/catalog/4483/data-dictionary/WLD_2021_RTFP_MKT?file_name=WLD_RTFP_mkt_2025-08-11.csv)
