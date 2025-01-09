# ID2223 Final Project: League of Legends Champion Predictor ML System

## Link to GUI
[Champion Pick Predictor Web App](https://huggingface.co/spaces/ivwhy/lol_champion_pick_predictor)

---

## Introduction
In this project, we developed a web scraper specifically for the website OP.GG, a popular database and analytics platform for the game League of Legends. OP.GG provides detailed statistics and information about players, champions, and matches, making it a go-to resource for the game's community. While Riot Games offers an official API for retrieving data, its limitation of daily refresh intervals poses challenges for real-time machine learning systems. By leveraging a web scraper, we ensured timely and continuous access to the most recent match data, enabling our model to function effectively.

The core of this project is an XGBoost model that predicts the champion pick of the final player in a match. The model uses a variety of input parameters, which are represented in a tabular format, to make its predictions. These inputs include match-specific details such as player statistics, team compositions, and champion selection trends.

One practical application of this machine learning system is in the context of the League of Legends competitive scene. Drafting strategy has been a critical aspect of LoL professional matches, as it provides a competitive edge. Teams have been adding coaches and analysts to enhance match preparation. By accurately forecasting champion selections, this system can be a valuable assistant in aiding match preparation through predicting various champion draft variables and compositions.

---

## Dataset
### Data Collection:
- Dataset was taken from 857 high-profile/ranked players from the leaderboard of four key competitive regions (Korea, Western Europe, North America, and Vietnam).
- This data includes approximately 17,000 rows of individual and match statistics.
- Champion stats and meta trends were also collected to provide better context and additional features for engineering.

### Challenges:
- The nature of the data refresh cycle and the high processing demand of scraping introduced challenges.
- Dataset shifts caused by periodic refreshes could influence training outcomes.

### Feature Engineering:
1. **Champion Score:** Aggregated metrics from player performance and trends.
2. **Player Playstyle:** Derived from average performance metrics.
3. **Champion Loyalty:** Player preferences for specific champions.
4. **Role Distribution:** Statistical role preferences.

The dataset initially contained over 350 columns, which were reduced to fewer than 40 columns through feature selection and engineering. This optimization improved interpretability and performance.

---

## Methodology
### System Overview
The proposed system predicts the champion pick of the final player in a League of Legends match using data from OP.GG. The architecture consists of four major components: data collection, model training, model hosting, and user interaction.

### 1. Data Collection
A custom web scraper was developed to extract match data directly from OP.GG. This scraper retrieves raw match details, including player statistics, team compositions, and champion selection trends. The data is then preprocessed to ensure consistency, handle missing values, and convert it into a format suitable for machine learning.

### 2. Model Training
- An **XGBoost Classifier** was selected due to its capability to handle categorical data effectively.
- Data was split into training, validation, and testing datasets.
- Training features included player statistics, champion selections, and team compositions.
- Categorical features were optimized using XGBoost’s category handling.
- Training utilized parameter tuning and feature refinement to optimize performance.
- `objective='multi:softprob'` was used to provide better insights into prediction probabilities.

### 3. Model Deployment
The trained XGBoost model was uploaded to Hugging Face, leveraging its repository and hosting infrastructure for easy deployment. This ensured public accessibility and seamless integration into a web application.

### 4. User Interaction via Gradio
A web application was created using Gradio and deployed on Hugging Face Spaces. This application provides a user-friendly interface where users can input match-specific details and receive predictions for the final champion pick. The app ensures accessibility to non-technical users.

### Workflow Summary
1. **Data Collection:** OP.GG data is scraped and preprocessed.
2. **Model Training:** Data is fed into the XGBoost model for training and testing.
3. **Model Deployment:** The trained model is hosted on Hugging Face.
4. **Web Application:** Users interact with the system via a Gradio-based app, receiving predictions.

---

## Results
### Accuracy:
- The model achieved a **40% prediction accuracy** for the top prediction.
- **Top-2 Prediction:** >50% accuracy.
- **Top-3 Prediction:** ~60% accuracy.
- **Top-5 Prediction:** ~68% accuracy.
This performance pattern is reflected in the class-wise accuracy distribution (Figure 1), which shows a bimodal pattern with peaks at 0.0 and 1.0, indicating varied prediction success across different champions.

(images/distribution_of_class_wise_accuracy.jpg)

### Challenges:
- Imbalanced dataset due to players’ tendency to follow meta trends, clearly visible in the long-tail distribution pattern of champion selections (Figure 2).
- Some champions had fewer than five samples, but this did not significantly affect the accuracy, as evidenced by the low correlation (0.046) between sample size and accuracy (Figure 3).

### Feature Importance:
Analysis revealed that features such as champion scores and playstyles were among the most impactful (Figure 4). Specifically, "most_role_1", "most_role_3", and "most_champ_1" showed the highest importance scores, suggesting that player behavior and role preferences drive champion selection more than individual champion statistics.

### Practical Use:
Despite its limitations, the system can serve as a powerful guidance tool when paired with an eports analysts’ expertise.

---

## How to Run the Code
1. Clone the repository.
2. Install the required dependencies listed in `requirements.txt`.
3. Run the scraping module to collect data from OP.GG.
4. Train the model using the provided training script.
5. Deploy the Gradio web app and access it via the provided link.

---

## Future Improvements
1. Expand the dataset to balance under-represented champions.
2. Incorporate advanced feature engineering techniques.
3. Experiment with alternative machine learning models.
4. Enhance the web app’s interface for better user experience.

