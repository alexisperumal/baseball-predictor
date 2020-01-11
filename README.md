# baseball-predictor

### Objective

Build a predictive model that can predict the winner of an MLB game, before it starts. (details below).


### Results

• It is hard to predict the outcome of a baseball game with meaningful uplift over 50% accuracy.

• We built a model based on historical team runs scored and starting pitcher runs allowed which was correct 54.24% of the time across the 2010-2017 (14,377 games)

• Simply picking the Home Team to win was correct 54.20% of the time!


### Key Files

• final-submission folder - Look here for all of our select final files for review. https://github.com/alexisperumal/baseball-predictor/tree/master/final-submission

• baseball-logistic-regression.ipynb - Our final Logistic Regression Notebook. Earlier analysis are further down in the file, as indicated in the headers. https://github.com/alexisperumal/baseball-predictor/blob/master/final-submission/baseball-logistic-regression.ipynb

• 2020-10-11_Baseball_Predictor_Project_Summary.pptx - Team presentation Deck. https://github.com/alexisperumal/baseball-predictor/blob/master/final-submission/2020-10-11_Baseball_Predictor_Project_Summary.pptx

• final-submission/plots folder - select plots for review. https://github.com/alexisperumal/baseball-predictor/tree/master/final-submission/plots

View other folders and files in our tree as you like.



# baseball-predictor - Original Scope

### UCSD Data Science Bootcamp Project 1 Proposal, 12/18/19
### MLB Game Winner Predictor

### Team Members:

•	Venkateswarlu Pinnika

•	Young You

•	Alexis Perumal


### Project Objective

•	Build a predictive model that can predict the winner of an MLB game, before it starts.

Project Description/Outline

•	Brainstorm the concept

•	Browse the dataset

•	Evaluate which factors drive runs

•	Build a simple 1 or 2 factor predictive model. Evaluate it. Tune it.

•	Layer additional factors as time allows.

•	Pull it together.

•	Write it up

•	Present it.


### Research Questions to Answer

•	What factors drive runs and game outcomes?

•	What is a reasonable expectation for predictive accuracy? Presumably 50% accurate is easy to do (random should do that). How much better can we do?

•	Should we consider a point spread?


### Datasets to use

•	SeanLahman.com – provides rich baseball game outcome for every MLB game going back to 1881. It includes game outcomes, player data, at bats, pitches.

•	We wouldn’t expect to use all that data. We would select what is most useful.

•	It is available as a CSV file.

•	The dataset is very rich, across multiple tables, so we don’t think other sources will be needed, but if we get the itch, we’ll find what else we can get.


### Rough Breakdown of Tasks 

•	Project Design and Strategy

•	Build and Release Management (manage git)

•	Technical architecture of the Jupyter notebook

•	Final analysis and write-up

•	Demo and Presentation

