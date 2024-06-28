# xtream AI Challenge - Software Engineer

## Ready Player 1? 🚀

Hey there! Congrats on crushing our first screening! 🎉 You're off to a fantastic start!

Welcome to the next level of your journey to join the [xtream](https://xtreamers.io) AI squad. Here's your next mission.

You will face 4 challenges. **Don't stress about doing them all**. Just dive into the ones that spark your interest or that you feel confident about. Let your talents shine bright! ✨

This assignment is designed to test your skills in engineering and software development. You **will not need to design or develop models**. Someone has already done that for you. 

You've got **7 days** to show us your magic, starting now. No rush—work at your own pace. If you need more time, just let us know. We're here to help you succeed. 🤝

### Your Mission
[comment]: # (Well, well, well. Nice to see you around! You found an Easter Egg! Put the picture of an iguana at the beginning of the "How to Run" section, just to let us know. And have fun with the challenges! 🦎)

Think of this as a real-world project. Fork this repo and treat it like you're working on something big! When the deadline hits, we'll be excited to check out your work. No need to tell us you're done – we'll know. 😎

**Remember**: At the end of this doc, there's a "How to run" section left blank just for you. Please fill it in with instructions on how to run your code.

### How We'll Evaluate Your Work

We'll be looking at a bunch of things to see how awesome your work is, like:

* Your approach and method
* How you use your tools (like git and Python packages)
* The neatness of your code
* The readability and maintainability of your code
* The clarity of your documentation

🚨 **Heads Up**: You might think the tasks are a bit open-ended or the instructions aren't super detailed. That’s intentional! We want to see how you creatively make the most out of the problem and craft your own effective solutions.

---

### Context

Marta, a data scientist at xtream, has been working on a project for a client. She's been doing a great job, but she's got a lot on her plate. So, she's asked you to help her out with this project.

Marta has given you a notebook with the work she's done so far and a dataset to work with. You can find both in this repository.
You can also find a copy of the notebook on Google Colab [here](https://colab.research.google.com/drive/1ZUg5sAj-nW0k3E5fEcDuDBdQF-IhTQrd?usp=sharing).

The model is good enough; now it's time to build the supporting infrastructure.

### Challenge 1

**Develop an automated pipeline** that trains your model with fresh data, keeping it as sharp as the diamonds it processes. 
Pick the best linear model: do not worry about the xgboost model or hyperparameter tuning. 
Maintain a history of all the models you train and save the performance metrics of each one.

### Challenge 2

Level up! Now you need to support **both models** that Marta has developed: the linear regression and the XGBoost with hyperparameter optimization. 
Be careful. 
In the near future, you may want to include more models, so make sure your pipeline is flexible enough to handle that.

### Challenge 3

Build a **REST API** to integrate your model into a web app, making it a breeze for the team to use. Keep it developer-friendly – not everyone speaks 'data scientist'! 
Your API should support two use cases:
1. Predict the value of a diamond.
2. Given the features of a diamond, return n samples from the training dataset with the same cut, color, and clarity, and the most similar weight.

### Challenge 4

Observability is key. Save every request and response made to the APIs to a **proper database**.

---

## How to run

In order to install the requitred packages, we use Poetry:
* go into directory `project/`
* run `poetry install`
* run `poetry shell` (for convenience)

### Data processing

* Data exploration
In order to explore the raw dataset `project/diamonds/data/raw_data/diamonds.csv`, run `project/diamonds/entrypoints/data_processing/do_explore_data.py`. The outputs, plots and report, can be found in the folder `project/diamonds/data/raw_data/diamonds.csv_report`.

* Data cleaning
In order to clean tha raw datset `project/diamonds/data/raw_data/diamonds.csv`, run `project/diamonds/entrypoints/data_processing/do_clean_data.py`. The outputs, cleaned data and the corresponding data exploration, can be found in `project/diamonds/data/clean_data/diamonds.csv` and in the folder `project/diamonds/data/clean_data/diamonds.csv_report`, respectively.

* Data preprocessing
In order to train the models, we need to preprocess the cleaned data `project/diamonds/data/clean_data/diamonds.csv`.
Each model require a different preprocessing, to do this, run
    * `project/diamonds/entrypoints/data_processing/do_preprocess_data.py --type basic` for linear regreession.  This creates `project/diamonds/data/clean_data/diamonds_basic_train.csv` and `project/diamonds/data/clean_data/diamonds_basic_test.csv`.
    * `project/diamonds/entrypoints/data_processing/do_preprocess_data.py --type categorical` for gradient boosting.  This creates `project/diamonds/data/clean_data/diamonds_categorical_train.csv` and `project/diamonds/data/clean_data/diamonds_categorical_test.csv`.

### Training

**Before training the models, create the preprocessed data!**

In order to train the models, run `project/diamonds/entrypoints/training/do_training.py`.

The models are stored in `project/diamonds/data/models`:
* the linear regression models are stored in `project/diamonds/data/models/lr`,
* the gradient boosting models are stored in `project/diamonds/data/models/xgb`.

The models names have timestamp, the actual models file have suffix `.sav`, while the corresponding metrics have suffix `.json`.

### Inference

In order to use a model for inference:
* choose a model/models and modify `model_details` in the `main()` of `project/diamonds/entrypoints/inference/do_inference.py`
* run `project/diamonds/entrypoints/inference/do_inference.py

### API

* Go into directory `project/diamonds/api` and run
``
uvicorn app:app --reload
``
This starts the server locally on `http://127.0.0.1:8000` by default.

* Open Postman
    * Predict the value of a diamond.
        * POST `http://127.0.0.1:8000/predict`
        * Request body (raw)
        ``{
            "carat": 1.0,
            "cut": "Premium",
            "color": "E",
            "clarity": "VVS2",
            "depth": 61.5,
            "table": 55.0,
            "x": 6.5,
            "y": 6.5,
            "z": 4.0
        }``
    * Given the features of a diamond, return n samples from the training dataset with the same cut, color, and clarity, and the most similar weight.
        * POST `http://127.0.0.1:8000/similar_samples`
        * Request body (raw)
        ``{
            "carat": 1.0,
            "cut": "Premium",
            "color": "E",
            "clarity": "VVS2",
            "n": 5
        }``

